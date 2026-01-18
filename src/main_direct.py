#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序入口
"""

import sys
import os
import time
import argparse
import traceback
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入工具模块
try:
    from utils.logger import get_logger
    from utils.file_handler import FileHandler
    from config.settings import *
    from config.websites import WEBSITES
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保在正确的目录运行")
    sys.exit(1)

# 导入各个网站的爬虫
from src.collectors.freeclashnode import FreeClashNodeCollector
from src.collectors.mibei77 import Mibei77Collector
from src.collectors.clashnodev2ray import ClashNodeV2RayCollector
from src.collectors.proxyqueen import ProxyQueenCollector
from src.collectors.wanzhuanmi import WanzhuanmiCollector
from src.collectors.cfmem import CfmemCollector
from src.collectors.clashnodecc import ClashNodeCCCollector
from src.collectors.datiya import DatiyaCollector
from src.collectors.telegeam import TelegeamCollector
from src.collectors.clashgithub import ClashGithubCollector
from src.collectors.freev2raynode import FreeV2rayNodeCollector
from src.collectors.eighty_five_la import EightyFiveLaCollector
from src.collectors.oneclash import OneClashCollector


class CollectorFactory:
    """收集器工厂类"""

    @staticmethod
    def get_collector(site_name):
        """根据网站名称获取收集器类"""
        collectors = {
            "freeclashnode": FreeClashNodeCollector,
            "mibei77": Mibei77Collector,
            "clashnodev2ray": ClashNodeV2RayCollector,
            "proxyqueen": ProxyQueenCollector,
            "wanzhuanmi": WanzhuanmiCollector,
            "cfmem": CfmemCollector,
            "clashnodecc": ClashNodeCCCollector,
            "datiya": DatiyaCollector,
            "telegeam": TelegeamCollector,
            "clashgithub": ClashGithubCollector,
            "freev2raynode": FreeV2rayNodeCollector,
            "85la": EightyFiveLaCollector,
            "oneclash": OneClashCollector,
        }

        return collectors.get(site_name)


class NodeCollector:
    """节点收集器主类"""

    def __init__(self):
        self.logger = get_logger("main")
        self.file_handler = FileHandler()

        # 初始化爬虫
        self.collectors = {
            "freeclashnode": FreeClashNodeCollector(WEBSITES["freeclashnode"]),
            "mibei77": Mibei77Collector(WEBSITES["mibei77"]),
            "clashnodev2ray": ClashNodeV2RayCollector(WEBSITES["clashnodev2ray"]),
            "proxyqueen": ProxyQueenCollector(WEBSITES["proxyqueen"]),
            "wanzhuanmi": WanzhuanmiCollector(WEBSITES["wanzhuanmi"]),
            "cfmem": CfmemCollector(WEBSITES["cfmem"]),
            "clashnodecc": ClashNodeCCCollector(WEBSITES["clashnodecc"]),
            "datiya": DatiyaCollector(WEBSITES["datiya"]),
            "telegeam": TelegeamCollector(WEBSITES["telegeam"]),
            "clashgithub": ClashGithubCollector(WEBSITES["clashgithub"]),
            "freev2raynode": FreeV2rayNodeCollector(WEBSITES["freev2raynode"]),
            "85la": EightyFiveLaCollector(WEBSITES["85la"]),
            "oneclash": OneClashCollector(WEBSITES["oneclash"]),
        }

    def collect_sites(self, sites=None):
        """收集指定网站或所有网站"""
        if sites is None:
            sites = list(self.collectors.keys())

        all_nodes = []

        for site_name in sites:
            if site_name not in self.collectors:
                self.logger.warning(f"未知的网站: {site_name}")
                continue

            collector = self.collectors[site_name]

            if not collector.enabled:
                self.logger.info(f"跳过已禁用的网站: {site_name}")
                continue

            try:
                self.logger.info(f"开始收集: {site_name}")

                # 获取最新文章URL
                article_url = collector.get_latest_article_url()

                if article_url:
                    # 从文章中提取节点
                    nodes = collector.extract_nodes_from_article(article_url)

                    if nodes:
                        all_nodes.extend(nodes)
                        self.logger.info(f"{site_name} 收集到 {len(nodes)} 个节点")
                    else:
                        self.logger.warning(f"{site_name} 未找到节点")
                else:
                    self.logger.warning(f"{site_name} 未找到文章链接")

            except Exception as e:
                self.logger.error(f"{site_name} 收集失败: {str(e)}")
                continue

            # 添加延迟避免请求过快
            from config.settings import REQUEST_DELAY

            time.sleep(REQUEST_DELAY)

        # 去重
        unique_nodes = list(set(all_nodes))
        self.logger.info(f"总计收集到 {len(unique_nodes)} 个去重节点")

        return unique_nodes

    def _extract_nodes_and_links(self, collector, article_url):
        """从文章中提取节点和订阅链接"""
        nodes = []
        subscription_links = []

        try:
            # 获取文章页面内容
            html_content = collector._get_page(article_url)
            if html_content:
                # 使用收集器的订阅链接提取方法
                if hasattr(collector, "_get_links_from_article"):
                    subscription_links = collector._get_links_from_article(article_url)
                else:
                    # 使用基类方法
                    subscription_links = collector._get_links_from_article(article_url)

                # 从每个订阅链接获取节点
                for link in subscription_links:
                    try:
                        link_nodes = collector._get_nodes_from_subscription(link)
                        if link_nodes:
                            nodes.extend(link_nodes)
                    except Exception as e:
                        self.logger.warning(f"获取订阅链接节点失败 {link}: {e}")
            else:
                self.logger.warning(f"无法获取文章内容: {article_url}")

        except Exception as e:
            self.logger.error(f"提取节点和链接失败: {e}")

        return nodes, subscription_links

    def _save_site_info(self, site_name, article_url, subscription_links):
        """保存网站信息到YYYYMMDD_info.txt文件"""
        try:
            from datetime import datetime

            date_str = datetime.now().strftime("%Y%m%d")

            # 创建目录 result/YYYYMMDD/
            date_dir = os.path.join("result", date_str)
            os.makedirs(date_dir, exist_ok=True)

            # 生成info文件路径
            info_filename = f"{site_name}_info.txt"
            info_path = os.path.join(date_dir, info_filename)

            # 写入信息文件（匹配现有格式）
            with open(info_path, "w", encoding="utf-8") as f:
                f.write(f"# {site_name} 文章和订阅链接\n")
                f.write(f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 60 + "\n")
                f.write(f"\n")
                f.write(f"## 文章链接\n")
                f.write(f"{article_url}\n")
                f.write(f"\n")
                f.write(f"## 订阅链接\n")

                for i, link in enumerate(subscription_links, 1):
                    f.write(f"{link}\n")

            self.logger.info(f"网站信息已保存到: {info_path}")

        except Exception as e:
            self.logger.error(f"保存网站信息失败 {site_name}: {e}")

    def save_results(self, nodes, date_str=None):
        """保存收集结果"""
        if not date_str:
            date_str = datetime.now().strftime("%Y%m%d")

        # 创建结果目录
        result_dir = os.path.join("result", date_str)
        os.makedirs(result_dir, exist_ok=True)

        # 保存总节点
        total_file = os.path.join(result_dir, "nodetotal.txt")
        with open(total_file, "w", encoding="utf-8") as f:
            for node in nodes:
                f.write(node + "\n")

        self.logger.info(f"节点已保存到: {total_file}")
        return total_file


def main():
    """主函数"""
    try:
        import argparse

        parser = argparse.ArgumentParser(description="V2Ray节点收集器")
        parser.add_argument("--sites", nargs="+", help="指定要收集的网站")
        parser.add_argument(
            "--list-sites", action="store_true", help="列出所有可用网站"
        )
        parser.add_argument("--status", action="store_true", help="显示状态信息")

        args = parser.parse_args()

        if args.list_sites:
            print("可用网站:")
            for site_name in WEBSITES.keys():
                status = "启用" if WEBSITES[site_name].get("enabled", True) else "禁用"
                print(f"  {site_name}: {status}")
            return

        if args.status:
            print("系统状态:")
            print(f"  支持网站数: {len(WEBSITES)}")
            enabled_count = sum(
                1 for site in WEBSITES.values() if site.get("enabled", True)
            )
            print(f"  启用网站数: {enabled_count}")
            return

        # 创建收集器
        collector = NodeCollector()

        if args.sites:
            # 收集指定网站
            nodes = collector.collect_sites(args.sites)
        else:
            # 收集所有网站
            nodes = collector.collect_sites()

        # 保存结果
        collector.save_results(nodes)

        print("✅ 收集完成")

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 运行出错: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
