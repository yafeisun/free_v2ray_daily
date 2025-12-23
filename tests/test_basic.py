#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_imports():
    """测试导入"""
    try:
        from src.collectors.freeclashnode import FreeClashNodeCollector
        from src.collectors.mibei77 import Mibei77Collector
        from src.collectors.clashnodev2ray import ClashNodeV2RayCollector
        from src.collectors.proxyqueen import ProxyQueenCollector
        from src.collectors.wanzhuanmi import WanzhuanmiCollector
        from src.testers.connectivity_tester import ConnectivityTester
        from src.utils.file_handler import FileHandler
        from src.utils.logger import get_logger
        from config.settings import CONNECTION_TIMEOUT, MAX_WORKERS
        from config.websites import WEBSITES
        
        print("✓ 所有导入成功")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {str(e)}")
        return False

def test_collectors():
    """测试爬虫初始化"""
    try:
        from src.collectors.freeclashnode import FreeClashNodeCollector
        from config.websites import WEBSITES
        
        collector = FreeClashNodeCollector(WEBSITES["freeclashnode"])
        print(f"✓ {collector.site_name} 初始化成功")
        return True
    except Exception as e:
        print(f"✗ 爬虫初始化失败: {str(e)}")
        return False

def test_file_handler():
    """测试文件处理"""
    try:
        from src.utils.file_handler import FileHandler
        
        handler = FileHandler()
        test_nodes = [
            "vmess://eyJhZGQiOiJleGFtcGxlLmNvbSIsImFpZCI6MCwiaG9zdCI6ImV4YW1wbGUuY29tIiwiaWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJuZXQiOiJ3cyIsInBhdGgiOiIvIiwicG9ydCI6NDQzLCJwcyI6InRlc3QiLCJzY3kiOiJhdXRvIiwic25pIjoidGVzdCIsInRscyI6InRjcCIsInR5cGUiOiJub25lIiwidiI6IjIifQ==",
            "vless://test@example.com:443?encryption=none&security=tls&type=ws&host=example.com&path=/#test"
        ]
        
        # 测试保存
        success = handler.save_nodes_to_file(test_nodes, "test_nodes.txt")
        if success:
            print("✓ 文件保存成功")
            
            # 测试加载
            loaded_nodes = handler.load_nodes_from_file("test_nodes.txt")
            if len(loaded_nodes) == len(test_nodes):
                print("✓ 文件加载成功")
                
                # 清理测试文件
                os.remove("test_nodes.txt")
                return True
            else:
                print("✗ 文件加载失败")
                return False
        else:
            print("✗ 文件保存失败")
            return False
            
    except Exception as e:
        print(f"✗ 文件处理测试失败: {str(e)}")
        return False

def test_connectivity_tester():
    """测试连通性测试器"""
    try:
        from src.testers.connectivity_tester import ConnectivityTester
        
        tester = ConnectivityTester()
        print("✓ 连通性测试器初始化成功")
        
        # 测试一个已知无效的节点
        test_node = "vmess://eyJhZGQiOiJpbnZhbGlkLmV4YW1wbGUiLCJhaWQiOjAsImhvc3QiOiJpbnZhbGlkLmV4YW1wbGUiLCJpZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsIm5ldCI6IndzIiwicGF0aCI6Ii8iLCJwb3J0Ijo0NDMsInBzIjoidGVzdCIsInNjeSI6ImF1dG8iLCJzbmkiOiJ0ZXN0IiwidGxzIjoidGNwIiwidHlwZSI6Im5vbmUiLCJ2IjoiMiJ9"
        
        result = tester.test_node_connectivity(test_node)
        print(f"✓ 连通性测试完成 (预期结果: False, 实际结果: {result})")
        
        return True
        
    except Exception as e:
        print(f"✗ 连通性测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("开始测试")
    print("=" * 50)
    
    tests = [
        ("导入测试", test_imports),
        ("爬虫初始化测试", test_collectors),
        ("文件处理测试", test_file_handler),
        ("连通性测试", test_connectivity_tester),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n运行 {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"✗ {test_name} 失败")
    
    print("\n" + "=" * 50)
    print(f"测试完成: {passed}/{total} 通过")
    print("=" * 50)
    
    if passed == total:
        print("✓ 所有测试通过")
        return True
    else:
        print("✗ 部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)