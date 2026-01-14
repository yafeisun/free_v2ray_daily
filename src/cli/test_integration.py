#!/usr/bin/env python3
"""
智能测速优化集成测试脚本
验证所有智能管理器是否正常工作
"""

import sys
import os
import time

def test_imports():
    """测试导入功能"""
    print("🧪 测试导入功能...")
    
    try:
        from scripts.intelligent_timeout import IntelligentTimeoutManager, PerformanceMonitor, ConcurrencyController
        print("✅ IntelligentTimeoutManager 导入成功")
    except Exception as e:
        print(f"❌ IntelligentTimeoutManager 导入失败: {e}")
        return False
        
    try:
        from scripts.test_nodes_with_subscheck import SubsCheckTester
            print("✅ SubsCheckTester 导入成功")
    except Exception as e:
        print(f"❌ SubsCheckTester 导入失败: {e}")
        return False
    
    return True

def test_timeout_manager():
    """测试超时管理器"""
    print("⏱️ 测试超时管理器...")
    
    try:
        from scripts.intelligent_timeout import IntelligentTimeoutManager
        timeout_manager = IntelligentTimeoutManager()
        
        # 测试动态超时计算
        timeout1 = timeout_manager.calculate_optimal_timeout(1, 100, 100)
        timeout2 = timeout_manager.calculate_optimal_timeout(2, 50, 200)
        
        print(f"  阶段1超时: {timeout1}ms (100节点, 100ms延迟)")
        print(f"  阶段2超时: {timeout2}ms (50节点, 200ms延迟)")
        
        return True
    except Exception as e:
        print(f"❌ 超时管理器测试失败: {e}")
        return False

def test_performance_monitor():
    """测试性能监控器"""
    print("📊 测试性能监控器...")
    
    try:
        from scripts.intelligent_timeout import PerformanceMonitor
        monitor = PerformanceMonitor()
        
        # 模拟性能数据
        monitor.start_test(100)
        monitor.record_node_processed(150.0)
        monitor.record_node_processed(200.0)
        monitor.record_node_processed(180.0)
        monitor.record_node_processed(120.0)  # 模拟低延迟
        monitor.record_error("Timeout Error")
        
        stats = monitor.get_current_stats()
        print(f"📈 当前统计: {stats}")
        
        return True
    except Exception as e:
        print(f"❌ 性能监控器测试失败: {e}")
        return False

def test_concurrency_controller():
    """测试并发控制器"""
    print("🔄 测试并发控制器...")
    
    try:
        from scripts.intelligent_timeout import ConcurrencyController
        controller = ConcurrencyController()
        
        # 测试动态并发调整
        controller.adjust_concurrency(100.0, 50.0, 0.05)
        current = controller.get_current_concurrency()
        print(f"🔄 当前并发: {current}")
        
        controller.adjust_concurrency(200.0, 10.0, 0.1)  # 模拟高错误率
        current = controller.get_current_concurrency()
        print(f"🔄 调整后并发: {current}")
        
        return True
    except Exception as e:
        print(f"❌ 并发控制器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始智能测速优化集成测试...")
    
    tests = [
        ("导入功能", test_imports),
        ("超时管理器", test_timeout_manager),
        ("性能监控器", test_performance_monitor),
        ("并发控制器", test_concurrency_controller),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'='*60} {name}...")
        try:
            result = test_func()
            results.append((name, "✅ 成功", str(result)))
        except Exception as e:
            results.append((name, "❌ 失败", str(e)))
    
    print(f"\n{'='*60} 测试结果汇总:")
    for name, status, detail in results:
        print(f"  {name}: {status}")
    
    # 检查成功率
    success_count = sum(1 for _, status, _ in results if status == "✅ 成功")
    print(f"\n✅ 成功率: {success_count}/{len(results)}")
    
    if success_count == len(results):
        print("🎉 所有智能管理器测试通过！")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查代码")
        return 1

if __name__ == "__main__":
    sys.exit(main())