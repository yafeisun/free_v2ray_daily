#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
收集器管理器
统一管理所有收集器的运行逻辑
"""

import sys
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.config_manager import get_config
from src.collectors import get_collector_instance, run_collector
from src.utils.logger import get_logger
from src.utils.file_handler import FileHandler


class CollectorManager:
    """收集器管理器 - 统一管理所有收集器的运行逻辑"""

    def __init__(self):
        self.config_manager = get_config()
        self.logger = get_logger("collector_manager")
        self.file_handler = FileHandler()
        self.collectors = {}
        self.results = {}

    def initialize_collectors(self, sites: Optional[List[str]] = None):
        """初始化收集器"""
        self.logger.info("初始化收集器...")

        websites = self.config_manager.websites.get_websites()

        for site_key, site_config in websites.items():
            if sites and site_key not in sites:
                self.logger.debug(f"跳过未指定的网站: {site_key}")
                continue

            if not site_config.get("enabled", True):
                self.logger.debug(f"跳过已禁用的网站: {site_key}")
                continue

            collector = get_collector_instance(site_key, site_config)
            if collector:
                self.collectors[site_key] = collector
                self.logger.info(f"✓ 初始化收集器: {site_config['name']}")
            else:
                self.logger.warning(f"✗ 初始化失败: {site_config['name']}")

        self.logger.info(f"成功初始化 {len(self.collectors)} 个收集器")
        return len(self.collectors) > 0

    def get_available_sites(self) -> List[str]:
        """获取所有可用网站列表"""
        websites = self.config_manager.websites.get_websites()
        return [
            site_key
            for site_key, config in websites.items()
            if config.get("enabled", True)
        ]

    def get_plugin_info(self) -> Dict[str, Dict]:
        """获取插件信息"""
        from src.core.plugin_registry import get_registry

        registry = get_registry()

        websites = self.config_manager.websites.get_websites()
        info = {}

        for site_key, site_config in websites.items():
            if not site_config.get("enabled", True):
                continue

            metadata = registry.get_collector_metadata(site_key)
            info[site_key] = {
                "collector_class": metadata.get("class_name", "Unknown")
                if metadata
                else "Unknown",
                "module": metadata.get("module", "Unknown") if metadata else "Unknown",
                "description": metadata.get("description", "No description")
                if metadata
                else "No description",
                "enabled": site_config.get("enabled", True),
            }

        return info

    def collect_all_links(self) -> Dict[str, Dict]:
        """
        阶段1：收集所有网站的文章链接和订阅链接（带重试机制）

        Returns:
            链接收集结果字典
        """
        results = {}
        max_retries = 3
        retry_delay = 2  # 秒

        for site_key, collector in self.collectors.items():
            success = False
            last_error = None

            # 重试机制
            for attempt in range(max_retries):
                try:
                    # 只在重试时显示尝试信息
                    if attempt > 0:
                        self.logger.info(
                            f"📄 重新收集 {collector.site_name} 的链接... (尝试 {attempt + 1}/{max_retries})"
                        )
                    else:
                        self.logger.info(f"📄 收集 {collector.site_name} 的链接...")

                    # 只收集链接，不解析订阅内容
                    links_info = collector.collect_links()

                    if links_info and links_info.get("subscription_links"):
                        results[site_key] = {
                            "name": collector.site_name,
                            "article_url": links_info.get("article_url"),
                            "subscription_links": links_info.get(
                                "subscription_links", []
                            ),
                            "raw_data": links_info.get("raw_data"),
                            "success": True,
                        }
                        self.logger.info(
                            f"✓ {collector.site_name} 找到 {len(links_info.get('subscription_links', []))} 个订阅链接"
                        )
                        success = True
                        break
                    else:
                        # 如果没有找到订阅链接，也可能是正常情况（网站暂时没有更新）
                        results[site_key] = {
                            "name": collector.site_name,
                            "article_url": links_info.get("article_url")
                            if links_info
                            else None,
                            "subscription_links": [],
                            "raw_data": links_info.get("raw_data")
                            if links_info
                            else None,
                            "success": True,  # 成功访问但没有新内容
                        }
                        self.logger.info(
                            f"✓ {collector.site_name} 访问成功但未找到新订阅链接"
                        )
                        success = True
                        break

                except Exception as e:
                    last_error = str(e)
                    self.logger.warning(
                        f"❌ {collector.site_name} 链接收集失败 (尝试 {attempt + 1}/{max_retries}): {last_error}"
                    )

                    # 如果不是最后一次尝试，等待后重试
                    if attempt < max_retries - 1:
                        self.logger.info(f"⏳ {retry_delay}秒后重试...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                    else:
                        # 最后一次失败，记录错误
                        results[site_key] = {
                            "name": collector.site_name,
                            "success": False,
                            "error": last_error,
                        }
                        self.logger.error(
                            f"❌ {collector.site_name} 链接收集最终失败: {last_error}"
                        )

        return results

    def parse_all_subscriptions(
        self, links_results: Dict[str, Dict]
    ) -> Dict[str, Dict]:
        """
        阶段2：统一解析所有订阅链接

        Args:
            links_results: 阶段1的链接收集结果

        Returns:
            最终的节点收集结果
        """
        final_results = {}

        # 收集所有订阅链接进行统一解析
        all_subscription_links = []
        for site_key, site_data in links_results.items():
            if site_data.get("success") and site_data.get("subscription_links"):
                for link in site_data["subscription_links"]:
                    all_subscription_links.append(
                        {
                            "site_key": site_key,
                            "link": link,
                            "site_name": site_data["name"],
                        }
                    )

        self.logger.info(
            f"🔍 共收集到 {len(all_subscription_links)} 个订阅链接，开始统一解析..."
        )

        # 解析所有订阅链接（带容错机制）
        parsed_nodes = {}
        failed_links = 0
        total_parsed = 0

        for link_info in all_subscription_links:
            site_key = link_info["site_key"]
            link = link_info["link"]
            site_name = link_info["site_name"]

            try:
                self.logger.debug(f"解析 {site_name}: {link[:50]}...")
                nodes = self._parse_single_subscription_with_retry(link)

                if nodes:  # 只记录有内容的解析结果
                    if site_key not in parsed_nodes:
                        parsed_nodes[site_key] = []
                    parsed_nodes[site_key].extend(nodes)
                    total_parsed += len(nodes)
                    self.logger.debug(f"✓ {site_name} 解析成功: {len(nodes)} 个节点")
                else:
                    self.logger.debug(f"⚠️ {site_name} 解析为空: {link[:50]}...")

            except Exception as e:
                failed_links += 1
                self.logger.warning(
                    f"❌ 订阅链接解析失败 {site_name}: {link[:50]}... - {str(e)}"
                )

        if failed_links > 0:
            success_rate = (
                (len(all_subscription_links) - failed_links)
                / len(all_subscription_links)
                * 100
            )
            self.logger.info(
                f"📊 解析完成: {len(all_subscription_links) - failed_links}/{len(all_subscription_links)} 成功 ({success_rate:.1f}%)"
            )

        # 合并结果
        for site_key, site_data in links_results.items():
            nodes = parsed_nodes.get(site_key, [])
            # 高级去重（基于server:port）
            unique_nodes = self._deduplicate_nodes_advanced(nodes)

            final_results[site_key] = {
                "name": site_data["name"],
                "nodes": unique_nodes,
                "article_url": site_data.get("article_url"),
                "subscription_links": site_data.get("subscription_links", []),
                "success": len(unique_nodes) > 0,
            }

            if unique_nodes:
                self.logger.info(
                    f"✓ {site_data['name']} 解析完成: {len(unique_nodes)} 个节点 ({len(nodes)} → {len(unique_nodes)} 去重)"
                )
            else:
                self.logger.warning(f"⚠️ {site_data['name']} 未解析到节点")

        return final_results

    def _deduplicate_nodes_advanced(self, nodes: List[str]) -> List[str]:
        """高级去重：基于server:port组合去重"""
        return self._deduplicate_nodes(nodes)

    def _parse_single_subscription_with_retry(self, subscription_url: str) -> List[str]:
        """解析单个订阅链接（带重试机制）"""
        max_retries = 2
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                from src.core.subscription_parser import SubscriptionParser

                parser = SubscriptionParser()
                nodes = parser.parse_subscription_url(subscription_url)

                # 验证解析结果
                if nodes and isinstance(nodes, list):
                    return nodes
                else:
                    self.logger.debug(
                        f"解析结果无效 (尝试 {attempt + 1}): {type(nodes)}"
                    )
                    return []

            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.debug(f"解析重试 (尝试 {attempt + 1}): {str(e)}")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise e

        return []

    def _parse_single_subscription(self, subscription_url: str) -> List[str]:
        """解析单个订阅链接（兼容旧接口）"""
        return self._parse_single_subscription_with_retry(subscription_url)

    def collect_all_sites(self, sites: Optional[List[str]] = None) -> Dict[str, Dict]:
        """
        收集所有网站的节点（两阶段流程）

        Args:
            sites: 指定要收集的网站列表，为None时收集所有启用网站

        Returns:
            收集结果字典
        """
        self.logger.info("开始收集所有网站...")

        # 初始化收集器
        self.initialize_collectors(sites)

        if not self.collectors:
            self.logger.error("没有可用的收集器")
            return {}

        # 阶段1：收集所有链接（文章URL和订阅链接）
        self.logger.info("📋 阶段1：收集文章链接和订阅链接...")
        links_results = self.collect_all_links()

        # 阶段2：统一解析所有订阅链接
        self.logger.info("🔍 阶段2：统一解析订阅链接...")
        final_results = self.parse_all_subscriptions(links_results)

        total_nodes = sum(
            len(result.get("nodes", [])) for result in final_results.values()
        )
        self.logger.info(f"所有网站收集完成，共获取 {total_nodes} 个节点")

        return final_results

    def run_single_collector(self, site_key: str) -> Tuple[bool, List[str]]:
        """运行单个收集器"""
        if site_key not in self.collectors:
            self.logger.error(f"收集器不存在: {site_key}")
            return False, []

        collector = self.collectors[site_key]
        site_name = collector.site_name

        try:
            self.logger.info(f"🚀 开始收集 {site_name}...")
            start_time = time.time()

            # 运行收集器
            nodes = collector.collect()

            # 记录结果
            duration = time.time() - start_time
            self.results[site_key] = {
                "success": bool(nodes),
                "node_count": len(nodes),
                "duration": duration,
                "nodes": nodes,
            }

            if nodes:
                self.logger.info(
                    f"✅ {site_name} 完成，收集到 {len(nodes)} 个节点，耗时 {duration:.2f}s"
                )
                return True, nodes
            else:
                self.logger.warning(f"⚠️ {site_name} 未收集到节点，耗时 {duration:.2f}s")
                return False, []

        except Exception as e:
            self.logger.error(f"❌ {site_name} 运行异常: {str(e)}")
            self.results[site_key] = {
                "success": False,
                "node_count": 0,
                "duration": 0,
                "error": str(e),
                "nodes": [],
            }
            return False, []

    def run_all_collectors(self) -> Dict[str, List[str]]:
        """运行所有收集器"""
        self.logger.info("🚀 开始运行所有收集器...")
        start_time = time.time()

        all_nodes = []
        success_count = 0
        total_count = len(self.collectors)

        for i, site_key in enumerate(self.collectors, 1):
            site_name = self.collectors[site_key].site_name
            self.logger.info(f"\n[{i}/{total_count}] {site_name}")
            self.logger.info("=" * 50)

            success, nodes = self.run_single_collector(site_key)
            if success:
                success_count += 1
                all_nodes.extend(nodes)

            # 请求间隔
            if i < total_count:
                time.sleep(self.config_manager.base.REQUEST_DELAY)

        # 去重节点
        unique_nodes = self._deduplicate_nodes(all_nodes)

        # 统计结果
        duration = time.time() - start_time
        duplicate_count = len(all_nodes) - len(unique_nodes)

        self.logger.info("\n" + "=" * 50)
        self.logger.info("📊 收集结果统计:")
        self.logger.info(f"总网站数: {total_count}")
        self.logger.info(f"成功网站数: {success_count}")
        self.logger.info(f"失败网站数: {total_count - success_count}")
        self.logger.info(f"原始节点数: {len(all_nodes)}")
        self.logger.info(f"去重节点数: {len(unique_nodes)}")
        self.logger.info(f"重复节点数: {duplicate_count}")
        self.logger.info(f"总耗时: {duration:.2f}s")
        self.logger.info("=" * 50)

        return {site_key: self.results[site_key]["nodes"] for site_key in self.results}

    def _deduplicate_nodes(self, nodes: List[str]) -> List[str]:
        """去重节点，基于server:port组合"""
        if not nodes:
            return []

        seen = set()
        unique_nodes = []

        for node in nodes:
            server_port = self._extract_server_port(node)
            if server_port and server_port not in seen:
                seen.add(server_port)
                unique_nodes.append(node)

        return unique_nodes

    def _extract_server_port(self, node: str) -> Optional[str]:
        """从节点中提取server:port作为唯一标识"""
        try:
            if "://" not in node:
                return None

            protocol = node.split("://", 1)[0]
            rest = node.split("://", 1)[1]

            # 移除名称部分
            if "#" in rest:
                rest = rest.rsplit("#", 1)[0]

            # 提取server:port
            if "@" in rest:
                rest = rest.split("@", 1)[1]

            if ":" in rest:
                parts = rest.split(":")
                if len(parts) >= 2:
                    server = parts[0]
                    port = parts[1].split("?")[0].split("/")[0].rstrip("/")
                    return f"{server}:{port}"

        except Exception:
            pass

        return None

    def get_results_summary(self) -> Dict:
        """获取收集结果摘要"""
        if not self.results:
            return {}

        summary = {
            "total_sites": len(self.results),
            "successful_sites": sum(
                1 for r in self.results.values() if r.get("success", False)
            ),
            "total_nodes": sum(r.get("node_count", 0) for r in self.results.values()),
            "total_duration": sum(r.get("duration", 0) for r in self.results.values()),
            "sites": {},
        }

        for site_key, result in self.results.items():
            site_name = (
                self.collectors.get(site_key, {}).site_name
                if site_key in self.collectors
                else site_key
            )
            summary["sites"][site_name] = {
                "success": result.get("success", False),
                "node_count": result.get("node_count", 0),
                "duration": result.get("duration", 0),
                "error": result.get("error"),
            }

        return summary

    def list_available_collectors(self) -> List[Dict]:
        """列出所有可用的收集器"""
        collectors_info = []

        websites = self.config_manager.websites.get_websites()

        for site_key, site_config in websites.items():
            collectors_info.append(
                {
                    "key": site_key,
                    "name": site_config["name"],
                    "enabled": site_config.get("enabled", True),
                    "url": site_config["url"],
                }
            )

        return collectors_info

    def test_collectors(self) -> Dict[str, bool]:
        """测试所有收集器的导入"""
        self.logger.info("🧪 测试收集器导入...")

        test_results = {}
        websites = self.config_manager.websites.get_websites()

        for site_key, site_config in websites.items():
            try:
                collector = get_collector_instance(site_key, site_config)
                if collector:
                    self.logger.info(f"✅ {site_config['name']} 导入成功")
                    test_results[site_key] = True
                else:
                    self.logger.warning(f"⚠️ {site_config['name']} 获取失败")
                    test_results[site_key] = False
            except Exception as e:
                self.logger.error(f"❌ {site_config['name']} 导入失败: {e}")
                test_results[site_key] = False

        success_count = sum(test_results.values())
        websites_count = len(self.config_manager.websites.get_websites())
        self.logger.info(f"📊 测试结果: {success_count}/{websites_count} 成功")

        return test_results
