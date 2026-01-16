#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临时解决方案：为所有收集器添加简化的collect()方法
"""

import sys

sys.path.insert(0, "/home/geely/Documents/Github/free_v2ray_daily")


def fix_collectors():
    """为所有收集器添加简化的collect()方法"""
    import re
    from pathlib import Path

    collectors_dir = Path(
        "/home/geely/Documents/Github/free_v2ray_daily/src/collectors"
    )

    # 需要修复的文件列表
    files_to_fix = [
        "cfmem.py",
        "clashnodecc.py",
        "clashnodev2ray.py",
        "datiya.py",
        "example_site.py",
        "freeclashnode.py",
        "freev2raynode.py",
        "github_collector.py",
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

        # 检查是否已经有collect方法
        if "def collect(self)" in content:
            print(f"{filename} 已有collect方法")
            continue

        # 查找类的结束位置
        class_pattern = r"class\s+\w+.*?:"
        lines = content.split("\n")
        class_end_line = -1

        for i, line in enumerate(lines):
            if re.match(r"^\s*class\s+", line):
                class_end_line = i
            elif (
                line.strip()
                and not line.startswith(" ")
                and not line.startswith("\t")
                and i > class_end_line
            ):
                # 找到类定义后的第一个空行
                class_end_line = i - 1
                break

        if class_end_line == -1:
            class_end_line = len(lines) - 1

        # 添加collect方法
        collect_method = '''
    def collect(self):  # type: ignore
        """简化收集方法"""
        try:
            # 尝试调用现有的节点获取方法
            if hasattr(self, 'get_v2ray_subscription_links') and hasattr(self, 'last_article_url'):
                links = self.get_v2ray_subscription_links(getattr(self, 'last_article_url', ''))
                nodes = []
                for link in links:
                    try:
                        nodes_from_link = self.get_nodes_from_subscription(link)
                        nodes.extend(nodes_from_link)
                    except:
                        pass
                
                return nodes
            
            # 如果有直接节点提取方法
            if hasattr(self, 'extract_direct_nodes'):
                page_content = getattr(self, 'fetch_page', lambda x: "")(self.base_url) if hasattr(self, 'base_url') else ""
                direct_nodes = self.extract_direct_nodes(page_content)
                return direct_nodes
                
        except Exception:
            return []
'''

        # 插入方法
        lines.insert(class_end_line + 1, collect_method)

        # 写回文件
        file_path.write_text("\n".join(lines))
        print(f"✅ 为 {filename} 添加了collect方法")


if __name__ == "__main__":
    fix_collectors()
