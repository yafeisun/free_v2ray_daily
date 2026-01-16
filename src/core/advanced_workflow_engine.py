#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多源节点收集工作流引擎
集成多种数据源的高级收集系统
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.core.workflow_engine import WorkflowEngine
from src.core.node_validator import validate_nodes
from src.collectors.multi_source_collector import source_manager
from src.collectors.telegram_collector import create_telegram_collector
from src.collectors.github_collector import create_github_collector
from src.core.config_manager import get_config
from src.utils.logger import get_logger


class AdvancedWorkflowEngine(WorkflowEngine):
    """高级工作流引擎 - 支持多源收集和实时验证"""

    def __init__(self):
        super().__init__()
        self.config_manager = get_config()
        self.logger = get_logger("advanced_workflow")

        # 注册多源收集器
        self._setup_multi_source_collectors()

    def _setup_multi_source_collectors(self):
        """设置多源收集器"""
        # Telegram收集器配置
        telegram_config = {
            "name": "Telegram节点收集",
            "enabled": os.getenv("TELEGRAM_ENABLED", "true").lower() == "true",
            "priority": 9,  # 最高优先级
            "bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
            "channels": [
                # 高质量VPN频道示例（需要替换为实际的）
                "@vpn_nodes_daily",
                "@v2ray_free_nodes",
                "@proxy_updates_channel",
            ],
            "keywords": ["vmess", "vless", "trojan", "ss://", "节点"],
            "api_delay": 1.0,
            "max_messages": 50,
            "update_interval": 1800,  # 30分钟
        }

        if telegram_config["bot_token"]:
            telegram_collector = create_telegram_collector(telegram_config)
            source_manager.register_collector(telegram_collector)

        # GitHub收集器配置
        github_config = {
            "name": "GitHub项目聚合",
            "enabled": os.getenv("GITHUB_ENABLED", "true").lower() == "true",
            "priority": 8,  # 高优先级
            "github_token": os.getenv("GITHUB_TOKEN"),
            "repositories": [
                {
                    "owner": "Loyalsoldier",
                    "repo": "v2ray_node_list",
                    "files": ["*.txt", "nodes/*.txt"],
                },
                {
                    "owner": "paimonhub",
                    "repo": "v2ray-free",
                    "files": ["*.txt", "*.md"],
                },
                {"owner": "ermaozi", "repo": "Free-VPN", "files": ["*.txt", "*.yaml"]},
            ],
            "timeout": 30,
            "max_files": 20,
        }

        github_collector = create_github_collector(github_config)
        source_manager.register_collector(github_collector)

        self.logger.info(f"已注册 {len(source_manager.collectors)} 个多源收集器")

    async def run_advanced_collection(
        self, sources: Optional[List[str]] = None
    ) -> bool:
        """运行高级节点收集"""
        self.logger.info("🚀 开始高级节点收集...")
        start_time = datetime.now()

        try:
            # 从多源收集节点
            nodes = await source_manager.collect_all_nodes()

            if not nodes:
                self.logger.warning("未从任何数据源收集到节点")
                return False

            # 转换为节点URL列表
            node_urls = []
            for node in nodes:
                if isinstance(node, dict) and "url" in node:
                    node_urls.append(node["url"])
                elif isinstance(node, str):
                    node_urls.append(node)

            # 实时验证节点质量
            self.logger.info(f"开始验证 {len(node_urls)} 个节点的质量...")
            validated_results = await validate_nodes(
                node_urls,
                output_file=f"result/nodes_detailed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            )

            # 保存高质量节点
            validated_urls = [r.url for r in validated_results]

            # 保存到标准格式
            date_str = datetime.now().strftime("%Y%m%d")
            date_dir = f"result/{date_str}"
            os.makedirs(date_dir, exist_ok=True)

            # 保存详细节点信息
            detailed_file = os.path.join(date_dir, "nodes_advanced.json")
            import json

            with open(detailed_file, "w", encoding="utf-8") as f:
                json.dump(
                    validated_results, f, indent=2, ensure_ascii=False, default=str
                )

            # 保存标准节点列表
            nodetotal_file = os.path.join(date_dir, "nodetotal.txt")
            with open(nodetotal_file, "w", encoding="utf-8") as f:
                for url in validated_urls:
                    f.write(f"{url}\\n")

            # 统计信息
            duration = (datetime.now() - start_time).total_seconds()
            online_count = len([r for r in validated_results if r.is_online])
            avg_quality = (
                sum(r.quality_score for r in validated_results) / len(validated_results)
                if validated_results
                else 0
            )

            # 数据源统计
            source_stats = {}
            for node in nodes:
                source_type = node.get("source_type", "unknown")
                source_stats[source_type] = source_stats.get(source_type, 0) + 1

            self.logger.info("=" * 60)
            self.logger.info("📊 高级收集统计:")
            self.logger.info(f"总耗时: {duration:.2f}秒")
            self.logger.info(f"原始节点: {len(node_urls)} 个")
            self.logger.info(f"在线节点: {online_count} 个")
            self.logger.info(f"平均质量: {avg_quality:.3f}")
            self.logger.info("📈 数据源分布:")
            for source_type, count in source_stats.items():
                self.logger.info(f"  {source_type}: {count} 个")
self.logger.info("=" * 60)
        
        except Exception as e:
            self.logger.error(f"高级收集异常: {str(e)}")
            return False
    
    def show_advanced_status(self):
        """显示高级工作流状态"""
        self.logger.info("🔄 开始混合工作流...")
        start_time = datetime.now()

        try:
            # 第一阶段：传统网站收集
            self.logger.info("📡 第一阶段：传统网站收集")
            import asyncio

            loop = asyncio.get_event_loop()
            traditional_success = await loop.run_in_executor(
                None, lambda: self._run_collection_phase(sources)
            )

            # 第二阶段：高级多源收集
            self.logger.info("🚀 第二阶段：高级多源收集")
            advanced_success = await self.run_advanced_collection(sources)

            # 第三阶段：节点验证和质量筛选
            if enable_validation:
                self.logger.info("⚡ 第三阶段：实时节点验证")
                await self._run_validation_phase()

            # 第四阶段：保存和同步
            self.logger.info("💾 第四阶段：保存和同步")
            sync_success = self._run_save_sync_phase()

            # 第五阶段：GitHub更新
            if update_github:
                self.logger.info("🚀 第五阶段：GitHub更新")
                github_success = self._run_github_update_phase()

            # 工作流完成
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info("🎉 混合工作流完成!")
            self.logger.info(f"总耗时: {duration:.2f}秒")

            return True

        except Exception as e:
            self.logger.error(f"混合工作流执行异常: {str(e)}")
            return False

    async def _run_validation_phase(self) -> bool:
        """运行验证阶段"""
        try:
            # 读取最新收集的节点
            date_str = datetime.now().strftime("%Y%m%d")
            nodetotal_file = f"result/{date_str}/nodetotal.txt"

            if not os.path.exists(nodetotal_file):
                self.logger.warning(f"节点文件不存在: {nodetotal_file}")
                return False

            with open(nodetotal_file, "r", encoding="utf-8") as f:
                node_urls = [line.strip() for line in f if line.strip()]

            # 验证节点
            validated_results = await validate_nodes(
                node_urls, output_file=f"result/{date_str}/nodelist_validated.txt"
            )

            # 保存验证后的节点
            validated_urls = [
                r.url
                for r in validated_results
                if r.is_online and r.quality_score >= 0.6
            ]

            nodelist_file = f"result/{date_str}/nodelist.txt"
            with open(nodelist_file, "w", encoding="utf-8") as f:
                for url in validated_urls:
                    f.write(f"{url}\\n")

            online_count = len(validated_results)
            high_quality_count = len(validated_urls)

            self.logger.info(
                f"节点验证完成: {online_count} 个在线，{high_quality_count} 个高质量"
            )
            return True

        except Exception as e:
            self.logger.error(f"验证阶段失败: {str(e)}")
            return False

    def show_advanced_status(self):
        """显示高级工作流状态"""
        print("🚀 高级节点收集系统状态")
        print("=" * 60)

        # 基础状态
        basic_status = self.get_workflow_status()
        for key, value in basic_status.items():
            if isinstance(value, bool):
                status = "✅ 就绪" if value else "❌ 未就绪"
            else:
                status = value
            print(f"  {key}: {status}")

        # 多源收集器状态
        print("\\n📊 多源收集器状态:")
        for collector in source_manager.collectors:
            enabled_status = "✅" if collector.enabled else "❌"
            print(
                f"  {collector.source_name}: {enabled_status} (优先级: {collector.priority})"
            )

        # 环境变量状态
        print("\\n🔧 环境变量配置:")
        env_vars = [
            "TELEGRAM_ENABLED",
            "TELEGRAM_BOT_TOKEN",
            "GITHUB_ENABLED",
            "GITHUB_TOKEN",
        ]

        for var in env_vars:
            value = os.getenv(var)
            if value:
                # 隐藏敏感信息
                display_value = "***SET***" if "TOKEN" in var else value
                print(f"  {var}: {display_value}")
            else:
                print(f"  {var}: ❌ 未设置")

        print("=" * 60)


# 创建高级工作流引擎实例
advanced_workflow = AdvancedWorkflowEngine()


async def run_advanced_collection(sources: Optional[List[str]] = None):
    """运行高级收集的便捷函数"""
    return await advanced_workflow.run_advanced_collection(sources)


def run_hybrid_workflow(
    sources: Optional[List[str]] = None,
    enable_validation: bool = True,
    update_github: bool = False,
):
    """运行混合工作流的便捷函数"""
    return advanced_workflow.run_hybrid_workflow(
        sources, enable_validation, update_github
    )


if __name__ == "__main__":
    # 测试高级工作流
    import asyncio

    # 显示状态
    advanced_workflow.show_advanced_status()

    # 运行测试
    asyncio.run(run_advanced_collection())
