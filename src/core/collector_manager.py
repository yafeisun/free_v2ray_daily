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
