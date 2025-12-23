#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试地区分类功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.region_detector import RegionDetector
from src.utils.file_handler import FileHandler

def test_region_detection():
    """测试地区检测功能"""
    print("=" * 50)
    print("测试地区检测功能")
    print("=" * 50)
    
    detector = RegionDetector()
    
    # 测试节点（模拟数据）
    test_nodes = [
        # 香港节点
        'vmess://eyJhZGQiOiJoa2ctZXhhbXBsZS5jb20iLCJhaWQiOiAwLCJob3N0IjoiaGtnLWV4YW1wbGUuY29tIiwicHMiOiLmtYvor5XkuK3mlofmnKzkuI3ku6PnoIHmg4Xotb3liqDovabpojoj5aSJ9',
        'vless://test@example.hk:443?name=香港节点',
        'trojan://password@123.45.67.89:443?name=HK-Server',
        
        # 其他节点
        'vmess://eyJhZGQiOiJ1cy1leGFtcGxlLmNvbSIsImFpZCI6IDAsImhvc3QiOiJ1cy1leGFtcGxlLmNvbSIsInBzIjoi5Lit5Zu95Lq65LitIn0=',
        'vless://test@sg.example.com:443?name=Singapore',
        'trojan://password@45.67.89.12:443?name=US-Server',
    ]
    
    print("测试节点:")
    for i, node in enumerate(test_nodes, 1):
        region = detector.detect_region(node)
        print(f"{i}. {region} - {node[:50]}...")
    
    # 测试分类功能
    classified = detector.classify_nodes(test_nodes)
    
    print(f"\n分类结果:")
    print(f"香港节点: {len(classified['HK'])} 个")
    for node in classified['HK']:
        print(f"  - {node[:50]}...")
    
    print(f"其他节点: {len(classified['OTHER'])} 个")
    for node in classified['OTHER']:
        print(f"  - {node[:50]}...")
    
    return len(classified['HK']) > 0 and len(classified['OTHER']) > 0

def test_file_handler():
    """测试文件处理功能"""
    print("\n" + "=" * 50)
    print("测试文件处理功能")
    print("=" * 50)
    
    handler = FileHandler()
    
    # 测试节点
    test_nodes = [
        'vmess://eyJhZGQiOiJoa2ctZXhhbXBsZS5jb20iLCJhaWQiOiAwLCJob3N0IjoiaGtnLWV4YW1wbGUuY29tIiwicHMiOiLmtYvor5XkuK3mlofmnKzkuI3ku6PnoIHmg4Xotb3liqDovabpojoj5aSJ9',
        'vmess://eyJhZGQiOiJ1cy1leGFtcGxlLmNvbSIsImFpZCI6IDAsImhvc3QiOiJ1cy1leGFtcGxlLmNvbSIsInBzIjoi5Lit5Zu95Lq65LitIn0=',
        'vless://test@example.hk:443?name=香港节点',
        'vless://test@sg.example.com:443?name=Singapore',
    ]
    
    # 保存测试
    success = handler.save_nodes_classified(test_nodes)
    
    if success:
        print("✓ 文件保存成功")
        
        # 检查文件是否存在
        from config.settings import NODELIST_FILE, NODELIST_HK_FILE
        
        if os.path.exists(NODELIST_HK_FILE):
            with open(NODELIST_HK_FILE, 'r', encoding='utf-8') as f:
                hk_nodes = f.read().strip().split('\n')
                print(f"✓ 香港节点文件: {len(hk_nodes)} 个节点")
        
        if os.path.exists(NODELIST_FILE):
            with open(NODELIST_FILE, 'r', encoding='utf-8') as f:
                other_nodes = f.read().strip().split('\n')
                print(f"✓ 其他节点文件: {len(other_nodes)} 个节点")
        
        return True
    else:
        print("✗ 文件保存失败")
        return False

def main():
    """主测试函数"""
    print("开始测试地区分类功能")
    
    try:
        # 测试地区检测
        test1_result = test_region_detection()
        
        # 测试文件处理
        test2_result = test_file_handler()
        
        print("\n" + "=" * 50)
        print("测试结果:")
        print(f"地区检测: {'✓ 通过' if test1_result else '✗ 失败'}")
        print(f"文件处理: {'✓ 通过' if test2_result else '✗ 失败'}")
        
        if test1_result and test2_result:
            print("✓ 所有测试通过")
            return True
        else:
            print("✗ 部分测试失败")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)