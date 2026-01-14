#!/usr/bin/env python3
"""
节点收集器统一运行脚本
调用src/collectors中的收集器模块
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.websites import WEBSITES
from src.collectors import get_collector_instance, run_collector


def run_single_collector(site_key: str):
    """运行单个收集器"""
    if site_key not in WEBSITES:
        print(f"❌ 未找到网站配置: {site_key}")
        return False

    site_config = WEBSITES[site_key]
    if not site_config.get("enabled", True):
        print(f"⚠️ 网站已禁用: {site_key}")
        return False

    print(f"🔍 运行收集器: {site_config['name']} ({site_key})")
    return run_collector(site_key, site_config)


def run_all_collectors():
    """运行所有启用的收集器"""
    print("🚀 运行所有收集器...")

    success_count = 0
    total_count = 0

    for site_key, site_config in WEBSITES.items():
        if site_config.get("enabled", True):
            total_count += 1
            print(f"\n[{total_count}] {site_config['name']}")
            print("=" * 50)

            if run_collector(site_key, site_config):
                success_count += 1
                print(f"✅ {site_config['name']} 完成")
            else:
                print(f"❌ {site_config['name']} 失败")

    print(f"\n📊 收集结果: {success_count}/{total_count} 成功")
    return success_count == total_count


def list_collectors():
    """列出所有可用的收集器"""
    print("📋 可用收集器列表:")
    print("=" * 60)

    for i, (site_key, site_config) in enumerate(WEBSITES.items(), 1):
        status = "✅ 启用" if site_config.get("enabled", True) else "❌ 禁用"
        print(f"{i:2d}. {site_config['name']} ({site_key}) - {status}")

    enabled_count = sum(
        1 for config in WEBSITES.values() if config.get("enabled", True)
    )
    print(f"\n总计: {len(WEBSITES)} 个网站，{enabled_count} 个启用")


def test_collectors():
    """测试所有收集器的导入"""
    print("🧪 测试收集器导入...")
    print("=" * 50)

    success_count = 0
    for site_key, site_config in WEBSITES.items():
        try:
            collector = get_collector_instance(site_key, site_config)
            if collector:
                print(f"✅ {site_config['name']} 导入成功")
                success_count += 1
            else:
                print(f"❌ {site_config['name']} 获取失败")
        except Exception as e:
            print(f"❌ {site_config['name']} 导入失败: {e}")

    print(f"\n📊 测试结果: {success_count}/{len(WEBSITES)} 成功")
    return success_count == len(WEBSITES)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="节点收集器运行器")
    parser.add_argument("--list", action="store_true", help="列出所有收集器")
    parser.add_argument("--test", action="store_true", help="测试所有收集器")
    parser.add_argument("--all", action="store_true", help="运行所有收集器")
    parser.add_argument("site", nargs="?", help="运行指定收集器")

    args = parser.parse_args()

    if args.list:
        list_collectors()
    elif args.test:
        test_collectors()
    elif args.all:
        run_all_collectors()
    elif args.site:
        run_single_collector(args.site)
    else:
        parser.print_help()
        print("\n🔧 示例:")
        print("  python3 run_collectors.py --list")
        print("  python3 run_collectors.py --test")
        print("  python3 run_collectors.py --all")
        print("  python3 run_collectors.py cfmem")


if __name__ == "__main__":
    main()
