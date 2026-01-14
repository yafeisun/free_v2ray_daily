"""
智能超时和并发管理器 - 修复版本
研究参考：Karing, subs-check, advanced-proxy-checker, wiz64等GitHub项目
修复了所有类型错误和格式问题
"""

import time
import math
from typing import Tuple, Dict, Any, Optional


class IntelligentTimeoutManager:
    """智能超时和并发管理器 - 修复版本"""

    def __init__(self):
        self.performance_history = []

    def calculate_optimal_timeout(
        self, phase: int, node_count: int, avg_latency: Optional[float] = None
    ) -> int:
        """计算最优超时时间"""
        if avg_latency is None:
            avg_latency = 200.0  # 默认200ms延迟

        # 基础超时
        base_timeout = 3000 if phase == 1 else 6000

        # 根据GitHub开源项目最佳实践调整
        if phase == 1:
            # 阶段1：连通性测试
            if avg_latency < 100:
                return 2000  # 低延迟，更快超时
            elif avg_latency < 200:
                return 3000  # 中等延迟，标准超时
            else:
                return 4000  # 高延迟，稍长超时
        else:
            # 阶段2：媒体检测，需要更长的超时
            if avg_latency < 500:
                return 6000  # 快速响应
            elif avg_latency < 1000:
                return 8000  # 中等响应
            elif avg_latency < 2000:
                return 12000  # 慢速响应
            else:
                return 15000  # 超慢响应

        # 基于并发数调整
        concurrency_factor = 1.0
        if node_count <= 50:
            concurrency_factor = 0.7  # 少量节点更保守
        elif node_count <= 100:
            concurrency_factor = 0.85  # 中等数量适中
        else:
            concurrency_factor = 1.0  # 大量节点保持标准

        # 基于平均延迟调整
        if avg_latency < 100:
            latency_factor = 0.8  # 低延迟，提高并发
        elif avg_latency < 200:
            latency_factor = 1.0  # 中等延迟，保持标准
        elif avg_latency < 500:
            latency_factor = 1.2  # 中等延迟，增加并发
        else:
            latency_factor = 1.0  # 高延迟，减少并发避免超时

        adjusted_timeout = int(base_timeout * concurrency_factor * latency_factor)
        return max(adjusted_timeout, 2000)  # 最少2秒

    def should_continue_waiting(
        self,
        progress: float,
        remaining_nodes: int,
        silent_elapsed: int,
        phase: int,
        last_update_time: Optional[float] = None,
    ) -> Tuple[bool, str]:
        """智能判断是否应该继续等待"""

        if phase == 1:
            # 阶段1：更严格的等待策略
            if progress >= 98.5 and remaining_nodes <= 2:
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
            # 阶段2：更宽松的等待策略（媒体检测通常较慢）
            if progress >= 99.5 and remaining_nodes <= 1:
                return (
                    True,
                    f"阶段2几乎完成({progress:.1f}%)，剩余{remaining_nodes}个节点完成中...",
                )
            elif progress >= 97.0 and remaining_nodes <= 3:
                max_wait = 180  # 3分钟
                if silent_elapsed < max_wait:
                    return (
                        True,
                        f"阶段2高进度({progress:.1f}%)，剩余{remaining_nodes}个节点，即将完成...",
                    )
            elif progress >= 95.0 and remaining_nodes <= 5:
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

    def get_learned_timeout(
        self, node_count: int, phase: int, avg_latency: Optional[float] = None
    ) -> int:
        """基于历史数据学习最优超时"""
        if not self.performance_history:
            return self.calculate_optimal_timeout(phase, node_count)

        # 找到相似的配置
        similar_records = [
            r
            for r in self.performance_history
            if r["node_count"] <= node_count * 1.2
            and r["phase"] == phase
            and r["success_rate"] > 0.8
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

    def record_node_processed(self, latency: Optional[float] = None):
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
        self.current_concurrency = 8
        self.max_concurrency = 20
        self.performance_window = []

    def adjust_concurrency(
        self, current_progress: float, avg_latency: float, error_rate: float
    ):
        """动态调整并发数"""
        if avg_latency < 100 and error_rate < 0.05:
            # 低延迟低错误率，可以增加并发
            new_concurrency = min(self.max_concurrency, self.current_concurrency + 2)
        elif avg_latency > 500 or error_rate > 0.1:
            # 高延迟高错误率，减少并发
            new_concurrency = max(1, self.current_concurrency - 1)
        else:
            # 保持当前并发
            new_concurrency = self.current_concurrency

        if new_concurrency != self.current_concurrency:
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
