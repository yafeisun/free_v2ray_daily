#!/usr/bin/env python3
"""
V2Ray节点收集器 - 简单入口脚本
运行 python3 collect.py 或 python3 -m src.main
"""

import sys
import subprocess


def main():
    """主入口函数"""
    print("🌐 V2Ray Daily Node Collector")
    print("📍 正在启动主程序...")
    print()
    print("使用方法:")
    print(" python3 collect.py")
    print(" 或: python3 -m src.main")
    print()
    print("正在启动主程序...")
    print()

    try:
        # 直接执行Python文件
        result = subprocess.run(
            [sys.executable, "src/main.py"], capture_output=False, text=True
        )

        if result.returncode != 0:
            print(f"❌ 运行失败，退出码: {result.returncode}")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
        else:
            print("✅ 程序执行完成")

    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
