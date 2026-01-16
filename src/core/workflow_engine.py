#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流引擎
统一管理完整的工作流程：收集 -> 测速 -> 保存 -> 提交
"""

import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.collector_manager import CollectorManager
from src.core.config_manager import get_config
from src.utils.logger import get_logger
from src.utils.file_handler import FileHandler


class WorkflowEngine:
    """工作流引擎 - 统一管理完整的工作流程"""

    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("workflow_engine")
        self.file_handler = FileHandler()
        self.collector_manager = CollectorManager()

    def run_full_workflow(
        self,
        sites: Optional[List[str]] = None,
        enable_speedtest: bool = False,
        update_github: bool = False,
    ) -> bool:
        """运行完整工作流：收集 -> 测速 -> 保存 -> 提交"""
        self.logger.info("🔄 开始完整工作流...")
        start_time = datetime.now()

        try:
            # 第一阶段：收集节点
            success = self._run_collection_phase(sites)
            if not success:
                self.logger.error("❌ 收集阶段失败，终止工作流")
                return False

            # 第二阶段：节点测速（可选）
            if enable_speedtest:
                success = self._run_speedtest_phase()
                if not success:
                    self.logger.warning("⚠️ 测速阶段失败，但继续工作流")

            # 第三阶段：保存和同步
            success = self._run_save_sync_phase()
            if not success:
                self.logger.warning("⚠️ 保存同步阶段失败")

            # 第四阶段：更新GitHub（可选）
            if update_github:
                success = self._run_github_update_phase()
                if not success:
                    self.logger.warning("⚠️ GitHub更新阶段失败")

            # 工作流完成
            duration = datetime.now() - start_time
            self.logger.info("🎉 完整工作流完成!")
            self.logger.info(f"总耗时: {duration.total_seconds():.2f}秒")
            return True

        except Exception as e:
            self.logger.error(f"❌ 工作流执行异常: {str(e)}")
            return False

    def _run_collection_phase(self, sites: Optional[List[str]] = None) -> bool:
        """运行收集阶段"""
        self.logger.info("📡 第一阶段：收集节点")
        self.logger.info("=" * 50)

        # 初始化收集器
        if not self.collector_manager.initialize_collectors(sites):
            self.logger.error("❌ 收集器初始化失败")
            return False

        # 运行所有收集器
        results = self.collector_manager.run_all_collectors()

        # 合并所有节点
        all_nodes = []
        for nodes in results.values():
            all_nodes.extend(nodes)

        if not all_nodes:
            self.logger.warning("⚠️ 未收集到任何节点")
            return False

        # 保存节点到文件
        date_str = datetime.now().strftime("%Y%m%d")
        date_dir = f"result/{date_str}"
        os.makedirs(date_dir, exist_ok=True)

        # 保存总节点文件
        nodetotal_file = os.path.join(date_dir, "nodetotal.txt")
        with open(nodetotal_file, "w", encoding="utf-8") as f:
            for node in all_nodes:
                f.write(f"{node}\n")

        self.logger.info(
            f"✅ 收集阶段完成，保存了 {len(all_nodes)} 个节点到 {nodetotal_file}"
        )
        return True

    def _run_speedtest_phase(self) -> bool:
        """运行测速阶段"""
        self.logger.info("⚡ 第二阶段：节点测速")
        self.logger.info("=" * 50)

        # 查找测速脚本
        speedtest_script = (
            project_root / "src" / "cli" / "speedtest" / "test_nodes_with_subscheck.py"
        )
        if not speedtest_script.exists():
            self.logger.warning("⚠️ 测速脚本不存在，跳过测速")
            return True

        # 构建测速命令
        date_str = datetime.now().strftime("%Y%m%d")
        input_file = f"result/{date_str}/nodetotal.txt"
        output_file = f"result/{date_str}/nodelist.txt"

        if not os.path.exists(input_file):
            self.logger.error(f"❌ 输入文件不存在: {input_file}")
            return False

        cmd = [
            sys.executable,
            str(speedtest_script),
            "--input",
            input_file,
            "--output",
            output_file,
        ]

        try:
            self.logger.info(f"🚀 执行测速命令: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=1800
            )  # 30分钟超时

            if result.returncode == 0:
                self.logger.info("✅ 测速阶段完成")
                if result.stdout:
                    self.logger.info(f"测速输出: {result.stdout}")
                return True
            else:
                self.logger.error(f"❌ 测速失败: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("❌ 测速超时")
            return False
        except Exception as e:
            self.logger.error(f"❌ 测速执行异常: {str(e)}")
            return False

    def _run_save_sync_phase(self) -> bool:
        """运行保存同步阶段"""
        self.logger.info("💾 第三阶段：保存和同步")
        self.logger.info("=" * 50)

        try:
            # 同步最新结果到根目录
            date_str = datetime.now().strftime("%Y%m%d")
            sync_success = self.file_handler.sync_latest_to_root(date_str)

            if sync_success:
                self.logger.info("✅ 文件同步完成")
            else:
                self.logger.warning("⚠️ 文件同步失败")

            # 清理临时文件
            clean_success = self.file_handler.clean_root_temp_files()
            if clean_success:
                self.logger.info("✅ 临时文件清理完成")

            return True

        except Exception as e:
            self.logger.error(f"❌ 保存同步异常: {str(e)}")
            return False

    def _run_github_update_phase(self) -> bool:
        """运行GitHub更新阶段"""
        self.logger.info("🚀 第四阶段：更新GitHub")
        self.logger.info("=" * 50)

        try:
            # 检查是否有Git仓库
            if not os.path.exists(".git"):
                self.logger.warning("⚠️ 不是Git仓库，跳过GitHub更新")
                return True

            # 检查是否有变化
            result = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True
            )
            if not result.stdout.strip():
                self.logger.info("✅ 没有变化需要提交")
                return True

            # 添加文件到暂存区
            subprocess.run(["git", "add", "result/"], check=True)

            # 生成提交信息
            commit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            summary = self.collector_manager.get_results_summary()

            commit_message = f"更新节点列表 - {commit_time}\n"
            commit_message += f"成功网站: {summary.get('successful_sites', 0)}\n"
            commit_message += f"总节点数: {summary.get('total_nodes', 0)}\n"

            # 提交
            subprocess.run(["git", "commit", "-m", commit_message], check=True)

            # 推送
            subprocess.run(["git", "push"], check=True)

            self.logger.info("✅ GitHub更新完成")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Git命令执行失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ GitHub更新异常: {str(e)}")
            return False

    def run_collection_only(self, sites: Optional[List[str]] = None) -> bool:
        """仅运行收集阶段"""
        return self._run_collection_phase(sites)

    def run_speedtest_only(self) -> bool:
        """仅运行测速阶段"""
        return self._run_speedtest_phase()

    def run_github_update_only(self) -> bool:
        """仅运行GitHub更新阶段"""
        return self._run_github_update_phase()

    def get_workflow_status(self) -> Dict:
        """获取工作流状态"""
        speedtest_script_path = (
            project_root / "src" / "cli" / "speedtest" / "test_nodes_with_subscheck.py"
        )

        status = {
            "collectors_initialized": len(self.collector_manager.collectors) > 0,
            "collector_count": len(self.collector_manager.collectors),
            "last_results": self.collector_manager.get_results_summary(),
            "git_repo": os.path.exists(".git"),
            "result_dir": os.path.exists("result"),
            "speedtest_script": speedtest_script_path.exists(),
        }

        return status
