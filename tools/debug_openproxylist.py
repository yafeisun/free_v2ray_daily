#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试OpenProxyList收集器
"""

import sys
import os

sys.path.insert(0, os.getcwd())

from src.collectors.openproxylist_collector import OpenProxyListCollector

# from config.settings import PROXY
import logging

# 设置详细日志
logging.basicConfig(level=logging.DEBUG)

# 测试配置
config = {
    "name": "OpenProxyList",
    "url": "https://openproxylist.com/v2ray/",
    "enabled": True,
    "collector_key": "openproxylist_collector",
    "selectors": [
        'a[href*="/v2ray"]',
        'a[href*="/rawlist"]',
        'a[href*="/subscribe"]',
        'a[href*=".txt"]',
    ],
    "patterns": [
        r"vmess://[^\s\n\r]+",
        r"vless://[^\s\n\r]+",
        r"trojan://[^\s\n\r]+",
        r"hysteria://[^\s\n\r]+",
        r"hysteria2://[^\s\n\r]+",
        r"ss://[^\s\n\r]+",
        r"ssr://[^\s\n\r]+",
        r'https?://[^\s\'"]*\.txt[^\s\'"]*',
        r'https?://[^\s\'"]*(?:rawlist|subscribe|v2ray)[^\s\'"]*',
    ],
    "timeout": 30,
    "update_interval": 7,
}


def test_collector():
    """测试收集器"""
    print("开始测试OpenProxyList收集器...")

    collector = OpenProxyListCollector(config)

    # 测试基本方法
    print(f"测试订阅URL: {collector.subscription_url}")

    # 测试内容获取
    try:
        import requests

        response = requests.get(
            collector.subscription_url, headers=collector.session.headers, timeout=10
        )
        if response.status_code == 200:
            content = response.text.strip()
            print(f"获取内容长度: {len(content)}")
            print(f"前100字符: {content[:100]}")

            # 测试解析
            nodes = collector._parse_node_content(content)
            print(f"解析到 {len(nodes)} 个节点")

            # 显示前5个节点
            for i, node in enumerate(nodes[:5]):
                print(f"节点 {i + 1}: {node}")
        else:
            print(f"请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"测试失败: {str(e)}")

    # 测试完整收集
    print("\n测试完整收集流程...")
    nodes = collector.collect()
    print(f"完整收集到 {len(nodes)} 个节点")


if __name__ == "__main__":
    test_collector()
