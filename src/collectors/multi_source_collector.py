#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多源节点收集器基类
支持多种数据源的统一接口
"""

import asyncio

try:
    import aiohttp
except ImportError:
    print("⚠️ aiohttp not installed, some features will be limited")
    aiohttp = None
import json
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.core.config_manager import get_config
from src.utils.logger import get_logger
from .base_collector import BaseCollector


class MultiSourceCollector(BaseCollector):
    """多源收集器基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_name = config.get("name", self.__class__.__name__)
        self.enabled = config.get("enabled", True)
        self.priority = config.get("priority", 1)
        self.update_interval = config.get("update_interval", 3600)  # 秒

        self.config_manager = get_config()
        self.logger = get_logger(f"multisource.{self.source_name.lower()}")

        # 质量评分权重
        self.quality_weights = {
            "freshness": 0.3,  # 新鲜度
            "reliability": 0.4,  # 可靠性
            "speed": 0.2,  # 速度
            "geographic": 0.1,  # 地理多样性
        }

    @abstractmethod
    async def collect_nodes(self) -> List[Dict[str, Any]]:
        """收集节点的抽象方法"""
        pass

    @abstractmethod
    def validate_source(self) -> bool:
        """验证数据源是否可用"""
        pass

    def calculate_quality_score(self, node: Dict[str, Any]) -> float:
        """计算节点质量评分"""
        score = 0.0

        # 新鲜度评分
        if "created_at" in node:
            age = (
                datetime.now() - datetime.fromisoformat(node["created_at"])
            ).total_seconds()
            freshness_score = max(0, 1 - age / 86400)  # 24小时内为满分
            score += freshness_score * self.quality_weights["freshness"]

        # 可靠性评分
        reliability_score = node.get("reliability", 0.5)
        score += reliability_score * self.quality_weights["reliability"]

        # 速度评分
        speed_score = min(1.0, node.get("speed", 0) / 100)  # 假设100Mbps为满分
        score += speed_score * self.quality_weights["speed"]

        # 地理多样性评分
        geo_score = 0.8 if node.get("country") not in ["CN", "HK", "TW"] else 0.3
        score += geo_score * self.quality_weights["geographic"]

        return min(1.0, score)

    def filter_high_quality_nodes(
        self, nodes: List[Dict[str, Any]], min_score: float = 0.6
    ) -> List[Dict[str, Any]]:
        """过滤高质量节点"""
        high_quality = []

        for node in nodes:
            quality_score = self.calculate_quality_score(node)
            node["quality_score"] = quality_score

            if quality_score >= min_score:
                high_quality.append(node)
                self.logger.debug(
                    f"高质量节点: {node.get('name', 'Unknown')} (评分: {quality_score:.2f})"
                )

        self.logger.info(
            f"从 {len(nodes)} 个节点中筛选出 {len(high_quality)} 个高质量节点"
        )
        return high_quality

    async def collect_with_retry(
        self, max_retries: int = 3
    ) -> Optional[List[Dict[str, Any]]]:
        """带重试的节点收集"""
        for attempt in range(max_retries):
            try:
                self.logger.info(
                    f"尝试从 {self.source_name} 收集节点 (第 {attempt + 1} 次)"
                )

                if not self.validate_source():
                    self.logger.warning(f"数据源 {self.source_name} 不可用")
                    return None

                nodes = await self.collect_nodes()

                if nodes:
                    self.logger.info(
                        f"从 {self.source_name} 成功收集到 {len(nodes)} 个节点"
                    )
                    return nodes
                else:
                    self.logger.warning(f"从 {self.source_name} 未收集到节点")

            except Exception as e:
                self.logger.error(f"收集失败 (第 {attempt + 1} 次): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)  # 指数退避

        return None


class SourceManager:
    """数据源管理器"""

    def __init__(self):
        self.collectors = []
        self.config_manager = get_config()
        self.logger = get_logger("source_manager")

    def register_collector(self, collector: MultiSourceCollector):
        """注册收集器"""
        self.collectors.append(collector)
        self.logger.info(f"注册收集器: {collector.source_name}")

    async def collect_all_nodes(self) -> List[Dict[str, Any]]:
        """从所有数据源收集节点"""
        all_nodes = []

        # 按优先级排序
        self.collectors.sort(key=lambda x: x.priority, reverse=True)

        tasks = []
        for collector in self.collectors:
            if collector.enabled:
                task = asyncio.create_task(collector.collect_with_retry())
                tasks.append((collector.source_name, task))

        if tasks:
            self.logger.info(f"并行收集节点，共 {len(tasks)} 个数据源")

            for source_name, task in tasks:
                try:
                    nodes = await task
                    if nodes:
                        all_nodes.extend(nodes)
                        self.logger.info(f"✅ {source_name}: {len(nodes)} 个节点")
                    else:
                        self.logger.warning(f"❌ {source_name}: 无节点")
                except Exception as e:
                    self.logger.error(f"❌ {source_name}: 收集异常 - {str(e)}")

        # 去重基于server:port
        unique_nodes = self.deduplicate_nodes(all_nodes)

        # 质量过滤
        high_quality_nodes = []
        for node in unique_nodes:
            node["quality_score"] = self.calculate_overall_quality(node)
            if node["quality_score"] >= 0.5:  # 最低质量要求
                high_quality_nodes.append(node)

        # 按质量评分排序
        high_quality_nodes.sort(key=lambda x: x["quality_score"], reverse=True)

        self.logger.info(
            f"总计: {len(all_nodes)} 个原始节点 -> {len(unique_nodes)} 个去重节点 -> {len(high_quality_nodes)} 个高质量节点"
        )

        return high_quality_nodes

    def deduplicate_nodes(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重节点"""
        seen = set()
        unique_nodes = []

        for node in nodes:
            # 提取唯一标识
            identifier = self.extract_node_identifier(node)
            if identifier and identifier not in seen:
                seen.add(identifier)
                unique_nodes.append(node)

        return unique_nodes

    def extract_node_identifier(self, node: Dict[str, Any]) -> Optional[str]:
        """提取节点唯一标识"""
        if "url" in node:
            # 从URL中提取server:port
            import re

            match = re.search(r"@([^:]+):(\d+)", node["url"])
            if match:
                return f"{match.group(1)}:{match.group(2)}"
        elif "server" in node and "port" in node:
            return f"{node['server']}:{node['port']}"
        elif "host" in node and "port" in node:
            return f"{node['host']}:{node['port']}"

        return None

    def calculate_overall_quality(self, node: Dict[str, Any]) -> float:
        """计算综合质量评分"""
        score = 0.0

        # 基础分数
        score += node.get("quality_score", 0.3) * 0.6

        # 数据源权重
        source_weight = {"telegram": 0.9, "github": 0.8, "community": 0.7, "web": 0.6}

        source_type = node.get("source_type", "web")
        score += source_weight.get(source_type, 0.5) * 0.4

        return min(1.0, score)


# 全局源管理器实例
source_manager = SourceManager()


def register_source(collector_class, config: Dict[str, Any]):
    """注册数据源的便捷函数"""
    collector = collector_class(config)
    source_manager.register_collector(collector)
    return collector


async def collect_all_sources():
    """收集所有数据源的便捷函数"""
    return await source_manager.collect_all_nodes()


    def collect(self):  # type: ignore
        """简化收集方法"""
        try:
            # 尝试调用现有的节点获取方法
            if hasattr(self, 'get_v2ray_subscription_links') and hasattr(self, 'last_article_url'):
                links = self.get_v2ray_subscription_links(getattr(self, 'last_article_url', ''))
                nodes = []
                for link in links:
                    try:
                        nodes_from_link = self.get_nodes_from_subscription(link)
                        nodes.extend(nodes_from_link)
                    except:
                        pass
                
                return nodes
            
            # 如果有直接节点提取方法
            if hasattr(self, 'extract_direct_nodes'):
                page_content = getattr(self, 'fetch_page', lambda x: "")(self.base_url) if hasattr(self, 'base_url') else ""
                direct_nodes = self.extract_direct_nodes(page_content)
                return direct_nodes
                
        except Exception:
            return []
