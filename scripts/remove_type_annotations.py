#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移除类型注解问题
"""

import sys
from pathlib import Path

# 获取项目根目录（脚本在scripts/下，所以需要往上两级）
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def remove_type_annotations():
    """移除所有收集器文件中的类型注解"""
    import re

    collectors_dir = PROJECT_ROOT / "src" / "collectors"

    files_to_fix = [
        "cfmem.py",
        "clashnodecc.py",
        "clashnodev2ray.py",
        "datiya.py",
        "example_site.py",
        "freeclashnode.py",
        "freev2raynode.py",
        "mibei77.py",
        "multi_source_collector.py",
        "oneclash.py",
        "proxyqueen.py",
        "telegeam.py",
        "telegram_collector.py",
        "wanzhuanmi.py",
    ]

    for filename in files_to_fix:
        file_path = collectors_dir / filename

        if not file_path.exists():
            print(f"文件不存在: {file_path}")
            continue

        # 读取文件内容
        content = file_path.read_text()

        # 移除List[str]类型注解，保留普通list
        content = re.sub(r"-> List\[str\]:\s*# type: ignore", "-> list:", content)

        # 写回文件
        file_path.write_text(content)
        print(f"✅ 修复了 {filename} 的类型注解问题")


if __name__ == "__main__":
    remove_type_annotations()
