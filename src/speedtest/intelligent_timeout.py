"""
智能超时和并发管理器 - 基于开源项目最佳实践
研究参考：Karing, subs-check, advanced-proxy-checker, wiz64等GitHub项目
"""

import time
import math
from typing import Tuple, Dict, Any


class IntelligentTimeoutManager:
    """智能超时和并发管理器"""

    def __init__(self):
        self.performance_history = []

    def calculate_optimal_timeout(
        self, phase: int, node_count: int, avg_latency: float = None
    ) -> int:
        """计算最优超时时间"""
        if avg_latency is None:
            avg_latency = 200.0  # 默认200ms延迟

        # 基础超时，并根据节点数量调整
        base_timeout = 3000 if phase == 1 else 6000

        # 根据节点数量增加超时时间
        if node_count > 1000:
            base_timeout *= 2  # 大量节点需要更长时间
        elif node_count > 500:
            base_timeout *= 1.5

        # 根据GitHub开源项目最佳实践调整
        if phase == 1:
            # 阶段1：连通性测试，较短超时
            if avg_latency < 100:
                return 2000  # 超低延迟，更快超时
            elif avg_latency < 200:
                return 3000  # 低延迟，标准超时
            else:
                return 4000  # 中高延迟，稍长超时
        else:
            # 阶段2：媒体检测，较长超时
            if avg_latency < 500:
                return 6000  # 快速响应
            elif avg_latency < 1000:
                return 8000  # 中等响应
            elif avg_latency < 2000:
                return 12000  # 慢速响应
            else:
                return 15000  # 超慢响应

    def calculate_optimal_concurrency(
        self, node_count: int, phase: int, avg_latency: float = None
    ) -> int:
        """计算最优并发数"""
        if avg_latency is None:
            avg_latency = 200.0

        if phase == 1:
            # 阶段1：连通性测试
            if node_count <= 50:
                if avg_latency < 100:
                    return 4  # 少量+低延迟
                elif avg_latency < 200:
                    return 6  # 少量+中等延迟
                else:
                    return 8  # 少量+高延迟
            elif node_count <= 100:
                if avg_latency < 100:
                    return 8  # 中等数量+低延迟
                elif avg_latency < 200:
                    return 10  # 中等数量+中等延迟
                else:
                    return 12  # 中等数量+高延迟
            elif node_count <= 200:
                if avg_latency < 200:
                    return 12  # 较多数量+低延迟
                elif avg_latency < 300:
                    return 8  # 较多数量+中等延迟
                else:
                    return 6  # 较多数量+高延迟，降低避免超时
            else:
                return 3  # 大量时进一步降低并发，确保稳定
        else:
            # 阶段2：媒体检测，需要更保守的并发
            if node_count <= 10:
                return 2  # 少量节点，极少并发
            elif node_count <= 20:
                return 3  # 少量节点
            elif node_count <= 50:
                return 4  # 中等数量
            else:
                return 4  # 较多节点，降低并发确保稳定

    def should_continue_waiting(
        self,
        progress: float,
        remaining_nodes: int,
        silent_elapsed: int,
        phase: int,
        last_update_time: float = None,
    ) -> Tuple[bool, str]:
        """智能判断是否应该继续等待"""

        # 基于进度的分层等待策略
        if phase == 1:
            # 阶段1：更严格的策略
            if progress >= 98.5 and remaining_nodes <= 3:
                return (
                    True,
                    f"阶段1接近完成({progress:.1f}%)，剩余{remaining_nodes}个节点，继续等待...",
                )
            elif progress >= 95.0 and remaining_nodes <= 5:
                max_wait = 120  # 2分钟
                if silent_elapsed < max_wait:
                    return (
                        True,
                        f"阶段1高进度({progress:.1f}%)，剩余{remaining_nodes}个节点，继续等待...",
                    )
            elif progress >= 90.0 and remaining_nodes <= 10:
                max_wait = 90  # 1.5分钟
                if silent_elapsed < max_wait:
                    return (
                        True,
                        f"阶段1中等进度({progress:.1f}%)，剩余{remaining_nodes}个节点，继续等待...",
                    )
            else:
                return (
                    False,
                    f"阶段1进度较低({progress:.1f}%)或剩余节点过多({remaining_nodes})，可能卡住",
                )

        else:
            # 阶段2：更宽松的策略（媒体检测通常较慢）
            if progress >= 99.0 and remaining_nodes <= 2:
                return (
                    True,
                    f"阶段2几乎完成({progress:.1f}%)，剩余{remaining_nodes}个节点，继续等待...",
                )
            elif progress >= 97.0 and remaining_nodes <= 5:
                max_wait = 180  # 3分钟
                if silent_elapsed < max_wait:
                    return (
                        True,
                        f"阶段2高进度({progress:.1f}%)，剩余{remaining_nodes}个节点，继续等待...",
                    )
            elif progress >= 95.0 and remaining_nodes <= 10:
                max_wait = 120  # 2分钟
                if silent_elapsed < max_wait:
                    return (
                        True,
                        f"阶段2中等进度({progress:.1f}%)，剩余{remaining_nodes}个节点，继续等待...",
                    )
            elif progress >= 90.0 and remaining_nodes <= 15:
                max_wait = 90  # 1.5分钟
                if silent_elapsed < max_wait:
                    return (
                        True,
                        f"阶段2一般进度({progress:.1f}%)，剩余{remaining_nodes}个节点，继续等待...",
                    )
            else:
                return (
                    False,
                    f"阶段2进度较低({progress:.1f}%)或剩余节点过多({remaining_nodes})，可能需要终止",
                )

    def get_retry_strategy(self, error_count: int) -> Tuple[bool, int]:
        """获取重试策略"""
        if error_count == 0:
            return True, 0
        elif error_count <= 2:
            return True, error_count * 2  # 指数退避
        elif error_count <= 5:
            return True, 30000  # 30秒
        else:
            return False, 0  # 不再重试

    def update_performance_metrics(
        self, node_count: int, avg_latency: float, success_rate: float, duration: float
    ):
        """更新性能指标用于学习优化"""
        self.performance_history.append(
            {
                "timestamp": time.time(),
                "node_count": node_count,
                "avg_latency": avg_latency,
                "success_rate": success_rate,
                "duration": duration,
            }
        )

        # 只保留最近10次记录
        if len(self.performance_history) > 10:
            self.performance_history = self.performance_history[-10:]

    def get_learned_timeout(self, node_count: int, phase: int) -> int:
        """基于历史数据学习最优超时"""
        if not self.performance_history:
            return self.calculate_optimal_timeout(phase, node_count)

        # 找到相似的配置
        similar_records = [
            r
            for r in self.performance_history
            if r["node_count"] <= node_count * 1.2
            and r["node_count"] >= node_count * 0.8
            and r["phase"] == phase
        ]

        if similar_records:
            avg_successful_timeout = sum(
                r["duration"] for r in similar_records if r["success_rate"] > 0.8
            ) / len(similar_records)
            return int(avg_successful_timeout * 0.9)  # 学习历史的90%成功超时

        return self.calculate_optimal_timeout(phase, node_count)


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.metrics = {
            "start_time": None,
            "last_update": None,
            "processed_nodes": 0,
            "total_nodes": 0,
            "errors": [],
            "latency_samples": [],
        }

    def start_test(self, total_nodes: int):
        """开始测试"""
        self.metrics["start_time"] = time.time()
        self.metrics["total_nodes"] = total_nodes
        self.metrics["processed_nodes"] = 0
        self.metrics["errors"] = []
        self.metrics["latency_samples"] = []

    def record_node_processed(self, latency: float = None):
        """记录节点处理完成"""
        self.metrics["processed_nodes"] += 1
        if latency is not None:
            self.metrics["latency_samples"].append(latency)
        self.metrics["last_update"] = time.time()

    def record_error(self, error: str):
        """记录错误"""
        self.metrics["errors"].append({"timestamp": time.time(), "error": error})
        self.metrics["last_update"] = time.time()

    def get_current_stats(self) -> Dict[str, Any]:
        """获取当前统计"""
        current_time = time.time()
        duration = (
            current_time - self.metrics["start_time"]
            if self.metrics["start_time"]
            else 0
        )
        progress = (
            (self.metrics["processed_nodes"] / self.metrics["total_nodes"] * 100)
            if self.metrics["total_nodes"] > 0
            else 0
        )

        avg_latency = (
            sum(self.metrics["latency_samples"]) / len(self.metrics["latency_samples"])
            if self.metrics["latency_samples"]
            else 0
        )

        return {
            "duration": duration,
            "processed_nodes": self.metrics["processed_nodes"],
            "total_nodes": self.metrics["total_nodes"],
            "progress": progress,
            "avg_latency": avg_latency,
            "error_count": len(self.metrics["errors"]),
            "nodes_per_minute": self.metrics["processed_nodes"] / (duration / 60)
            if duration > 0
            else 0,
            "eta": (
                (self.metrics["total_nodes"] - self.metrics["processed_nodes"])
                / (self.metrics["processed_nodes"] / (duration / 60))
            )
            if self.metrics["processed_nodes"] > 0 and duration > 0
            else None,
        }


class ConcurrencyController:
    """并发控制器"""

    def __init__(self):
        self.current_concurrency = 1
        self.max_concurrency = 15
        self.performance_window = []

    def adjust_concurrency(
        self, current_progress: float, avg_latency: float, error_rate: float
    ):
        """动态调整并发数"""
        if avg_latency < 100 and error_rate < 0.05:
            # 低延迟低错误，可以增加并发
            new_concurrency = min(self.max_concurrency, self.current_concurrency + 2)
        elif avg_latency > 500 or error_rate > 0.1:
            # 高延迟或高错误率，减少并发
            new_concurrency = max(1, self.current_concurrency - 1)
        else:
            # 稳定当前并发
            new_concurrency = self.current_concurrency

        self.current_concurrency = new_concurrency
        self.performance_window.append(
            {
                "progress": current_progress,
                "avg_latency": avg_latency,
                "error_rate": error_rate,
                "concurrency": new_concurrency,
            }
        )

        return new_concurrency
