#!/usr/bin/env python3
"""
环境配置检查脚本
检查高级功能所需的环境变量和依赖
"""

import os
import subprocess
import sys
from pathlib import Path


def check_environment_variable(var_name, description):
    """检查环境变量"""
    value = os.getenv(var_name)
    if value:
        if var_name.endswith("_ENABLED"):
            status = (
                "✅ 已启用" if value.lower() in ("true", "1", "yes") else "⚠️ 已禁用"
            )
        elif var_name.endswith("_TOKEN"):
            status = "✅ 已配置" if len(value) > 10 else "⚠️ 可能无效"
        else:
            status = "✅ 已设置"
        return True, status, value[:20] + "..." if len(value) > 20 else value
    else:
        return False, "❌ 未配置", ""


def check_dependency(package_name):
    """检查Python包是否已安装"""
    try:
        result = subprocess.run(
            [sys.executable, "-c", f"import {package_name}"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except:
        return False


def main():
    """主函数"""
    print("🔧 环境配置检查报告")
    print("=" * 60)

    # 检查环境变量
    print("\n📋 环境变量状态:")
    env_vars = [
        ("TELEGRAM_ENABLED", "Telegram收集器"),
        ("TELEGRAM_BOT_TOKEN", "Telegram Bot Token"),
        ("GITHUB_ENABLED", "GitHub收集器"),
        ("GITHUB_TOKEN", "GitHub Token"),
        ("NODE_VALIDATION_ENABLED", "节点验证"),
        ("COMMUNITY_CONTRIBUTIONS", "社区贡献"),
    ]

    env_score = 0
    for var, desc in env_vars:
        configured, status, value = check_environment_variable(var, desc)
        if configured:
            env_score += 1
        print(f"  {status} {desc} ({var})")
        if value:
            print(f"       值: {value}")

    # 检查依赖
    print("\n📦 依赖包状态:")
    dependencies = [
        ("aiohttp", "异步HTTP客户端"),
        ("telethon", "Telegram API客户端"),
        ("APScheduler", "任务调度器"),
        ("asyncio", "异步编程（内置）"),
        ("pathlib", "路径操作（内置）"),
    ]

    dep_score = 0
    for package, desc in dependencies:
        if package in ["asyncio", "pathlib"]:
            print(f"  ✅ {desc} - 内置模块")
            dep_score += 1
        else:
            installed = check_dependency(package)
            status = "✅ 已安装" if installed else "❌ 未安装"
            print(f"  {status} {desc} ({package})")
            if installed:
                dep_score += 1

    # 检查重要文件
    print("\n📁 重要文件状态:")
    important_files = [
        "src/core/simple_advanced_workflow.py",
        "src/core/multi_source_collector.py",
        "src/collectors/telegram_collector.py",
        "src/collectors/github_collector.py",
        "config/multi_source_config.py",
    ]

    file_score = 0
    for file_path in important_files:
        exists = Path(file_path).exists()
        status = "✅ 存在" if exists else "❌ 缺失"
        print(f"  {status} {file_path}")
        if exists:
            file_score += 1

    # 总结
    print("\n" + "=" * 60)
    print("📊 配置完整性评估:")

    total_possible = len(env_vars) + len(dependencies) + len(important_files)
    total_score = env_score + dep_score + file_score
    percentage = (total_score / total_possible) * 100

    print(
        f"  环境变量: {env_score}/{len(env_vars)} ({(env_score / len(env_vars)) * 100:.0f}%)"
    )
    print(
        f"  依赖包: {dep_score}/{len(dependencies)} ({(dep_score / len(dependencies)) * 100:.0f}%)"
    )
    print(
        f"  文件完整性: {file_score}/{len(important_files)} ({(file_score / len(important_files)) * 100:.0f}%)"
    )
    print(f"  总体配置: {total_score}/{total_possible} ({percentage:.0f}%)")

    if percentage >= 80:
        print("\n🎉 环境配置良好！系统可以正常运行。")
        return 0
    elif percentage >= 60:
        print("\n⚠️ 环境配置基本就绪，建议优化以提高功能完整性。")
        return 0
    else:
        print("\n❌ 环境配置不完整，可能影响高级功能使用。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
