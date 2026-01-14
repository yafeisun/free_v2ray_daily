#!/usr/bin/env python3
"""
V2Ray节点管理主入口
提供统一的命令行界面来管理节点收集和测速
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_collectors():
    """运行所有节点收集器"""
    print("🔍 开始收集节点...")

    # 使用统一的收集器运行器
    collector_script = project_root / "scripts" / "run_collectors.py"
    if collector_script.exists():
        print("📡 运行统一收集器...")
        result = subprocess.run(
            [sys.executable, str(collector_script), "--all"],
            capture_output=False,
            text=True,
            cwd=project_root,
        )
        if result.returncode == 0:
            print("✅ 节点收集完成")
        else:
            print("❌ 节点收集失败")
    else:
        print("❌ 收集器运行器不存在")
        return False

    return result.returncode == 0


def run_single_collectors():
    """运行单个收集器"""
    collectors_dir = project_root / "scripts" / "collectors"
    if collectors_dir.exists():
        for collector_file in collectors_dir.glob("*.py"):
            if collector_file.name != "__init__.py":
                print(f"📡 运行收集器: {collector_file.name}")
                subprocess.run(
                    [sys.executable, str(collector_file)],
                    capture_output=False,
                    text=True,
                )


def run_speedtest(input_file="result/nodetotal.txt", output_file="result/nodelist.txt"):
    """运行节点测速"""
    print("⚡ 开始节点测速...")

    # 确保输入文件存在
    input_path = project_root / input_file
    if not input_path.exists():
        print(f"❌ 输入文件不存在: {input_path}")
        return

    # 运行主测速脚本
    speedtest_script = (
        project_root / "scripts" / "speedtest" / "test_nodes_with_subscheck.py"
    )
    if speedtest_script.exists():
        cmd = [
            sys.executable,
            str(speedtest_script),
            "--input",
            str(input_path),
            "--output",
            str(project_root / output_file),
        ]
        print(f"🚀 执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=False, text=True)

        if result.returncode == 0:
            print("✅ 节点测速完成")

            # 统计结果
            output_path = project_root / output_file
            if output_path.exists():
                with open(input_path) as f_in, open(output_path) as f_out:
                    total_nodes = len(f_in.readlines())
                    valid_nodes = len(f_out.readlines())
                    print(
                        f"📊 统计结果: 总节点{total_nodes}个, 有效节点{valid_nodes}个, 通过率{valid_nodes / total_nodes * 100:.1f}%"
                    )
        else:
            print("❌ 节点测速失败")
    else:
        print("❌ 测速脚本不存在")


def run_full_workflow():
    """运行完整工作流: 收集 -> 测速"""
    print("🔄 开始完整工作流...")
    run_collectors()
    run_speedtest()
    print("🎉 完整工作流完成!")


def show_status():
    """显示当前状态"""
    print("📊 当前项目状态:")

    # 检查关键文件
    files_to_check = [
        ("结果目录", "result/nodetotal.txt"),
        ("有效节点", "result/nodelist.txt"),
        ("主测速脚本", "scripts/speedtest/test_nodes_with_subscheck.py"),
        ("收集器模块", "src/collectors"),
        ("收集器运行器", "scripts/run_collectors.py"),
    ]

    for name, path in files_to_check:
        full_path = project_root / path
        if full_path.exists():
            if full_path.is_file():
                with open(full_path) as f:
                    lines = len(f.readlines())
                print(f"  ✅ {name}: {lines} 行")
            else:
                files = len(list(full_path.glob("*.py")))
                print(f"  ✅ {name}: {files} 个脚本")
        else:
            print(f"  ❌ {name}: 不存在")


def main():
    parser = argparse.ArgumentParser(description="V2Ray节点管理工具")
    parser.add_argument("--collect", action="store_true", help="收集节点")
    parser.add_argument("--test", action="store_true", help="测速节点")
    parser.add_argument("--full", action="store_true", help="完整工作流")
    parser.add_argument("--status", action="store_true", help="显示状态")
    parser.add_argument("--input", default="result/nodetotal.txt", help="输入文件路径")
    parser.add_argument("--output", default="result/nodelist.txt", help="输出文件路径")

    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.collect:
        run_collectors()
    elif args.test:
        run_speedtest(args.input, args.output)
    elif args.full:
        run_full_workflow()
    else:
        parser.print_help()
        print("\n🔧 示例用法:")
        print("  python3 run.py --status      # 显示状态")
        print("  python3 run.py --collect     # 收集节点")
        print("  python3 run.py --test        # 测速节点")
        print("  python3 run.py --full        # 完整工作流")


if __name__ == "__main__":
    main()
