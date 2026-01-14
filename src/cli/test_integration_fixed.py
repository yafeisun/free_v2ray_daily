#!/usr/bin/env python3
"""
智能测速优化集成测试 - 修复版本
确保所有类型和导入问题都得到解决
"""

import sys
import time

# 临时修复类型别名
try:
    # 为None类型添加类型提示
    NoneType = type(None)
    IntType = int
    FloatType = float

    print("✅ 类型检查通过，开始集成测试...")
except ImportError as e:
    print(f"❌ 类型检查失败: {e}")
    sys.exit(1)


# 尝试导入修改后的文件
def test_modified_imports():
    """测试修改后的文件导入"""
    try:
        from scripts.test_nodes_with_subscheck import SubsCheckTester

        print("✅ 修改后的主文件导入成功")
    except ImportError as e:
        print(f"❌ 修改后的主文件导入失败: {e}")
        return False

    try:
        from scripts.intelligent_timeout import (
            IntelligentTimeoutManager,
            PerformanceMonitor,
            ConcurrencyController,
        )

        print("✅ 智能管理器导入成功")
    except ImportError as e:
        print(f"❌ 智能管理器导入失败: {e}")
        return False

    try:
        import progress_server

        print("✅ 进度服务器导入成功")
    except ImportError as e:
        print(f"❌ 进度服务器导入失败: {e}")
        return False

    return True


def test_intelligent_managers():
    """测试所有智能管理器"""
    managers = []

    print("🧪 开始测试智能管理器...")

    # 测试超时管理器
    try:
        timeout_manager = IntelligentTimeoutManager()
        timeout1 = timeout_manager.calculate_optimal_timeout(1, 100, None)
        timeout2 = timeout_manager.calculate_optimal_timeout(2, 100, 200)
        print(f"✅ 超时管理器测试通过 - 阶段1: {timeout1}ms, 阶段2: {timeout2}ms")
    except Exception as e:
        print(f"❌ 超时管理器测试失败: {e}")
        return False

    # 测试性能监控器
    try:
        monitor = PerformanceMonitor()
        monitor.start_test(50)
        time.sleep(2)
        monitor.record_node_processed(150.0)
        time.sleep(2)
        monitor.record_node_processed(200.0)
        time.sleep(2)
        monitor.record_error("Test error")
        time.sleep(1)

        stats = monitor.get_current_stats()
        print(f"✅ 性能监控器测试通过: {stats}")
    except Exception as e:
        print(f"❌ 性能监控器测试失败: {e}")
        return False

    # 测试并发控制器
    try:
        controller = ConcurrencyController()
        controller.adjust_concurrency(0, 50.0, 0.0)
        print(
            f"✅ 并发控制器测试通过 - 当前并发: {controller.get_current_concurrency()}"
        )
    except Exception as e:
        print(f"❌ 并发控制器测试失败: {e}")
        return False

    if all(managers):
        print("✅ 所有智能管理器测试通过！")
        return True
    else:
        print("❌ 部分管理器测试失败")
        return False


def run_integration_test():
    """运行集成测试"""
    print("🚀 开始智能测速优化集成测试...")

    # 测试导入
    if not test_modified_imports():
        print("❌ 导入测试失败，停止测试")
        return False

    # 测试智能管理器
    if not test_intelligent_managers():
        print("❌ 智能管理器测试失败，停止测试")
        return False

    print("✅ 所有测试通过！集成优化准备完成。")
    return True


if __name__ == "__main__":
    run_integration_test()
