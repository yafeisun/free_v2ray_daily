#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用收集器脚本 - 支持所有网站的统一入口
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.utils.logger import get_logger
from src.core.plugin_registry import get_registry
from src.utils.file_handler import FileHandler
from config.websites import WEBSITES


class UniversalCollector:
    """通用收集器 - 支持所有网站"""
    
    def __init__(self):
        self.logger = get_logger("universal_collector")
        self.file_handler = FileHandler()
        self.registry = get_registry()
    
    def run_site(self, site_key: str) -> bool:
        """运行指定网站的收集器"""
        try:
            # 检查网站配置
            if site_key not in WEBSITES:
                self.logger.error(f"未找到网站配置: {site_key}")
                return False
            
            site_config = WEBSITES[site_key]
            if not site_config.get("enabled", True):
                self.logger.info(f"网站已禁用: {site_key}")
                return True
            
            # 检查收集器插件
            collector_key = site_config.get("collector_key", site_key)
            if not self.registry.is_collector_available(collector_key):
                self.logger.error(f"未找到收集器插件: {collector_key}")
                return False
            
            # 创建收集器实例
            collector = self.registry.create_collector_instance(collector_key, site_config)
            
            # 开始收集
            self.logger.info(f"开始收集 {site_key} 的节点...")
            nodes = collector.collect()
            
            # 收集V2Ray订阅链接
            v2ray_links = []
            if hasattr(collector, 'last_article_url') and collector.last_article_url:
                v2ray_links = collector.get_v2ray_subscription_links(collector.last_article_url)
            
            # 保存结果
            self._save_results(site_key, collector, nodes, v2ray_links)
            
            self.logger.info(f"{site_key} 收集完成: {len(nodes)} 个节点，{len(v2ray_links)} 个订阅链接")
            return True
            
        except Exception as e:
            self.logger.error(f"收集 {site_key} 失败: {str(e)}")
            return False
    
    def _save_results(self, site_key: str, collector, nodes: list, v2ray_links: list):
        """保存收集结果"""
        try:
            # 保存文章链接
            if hasattr(collector, 'last_article_url') and collector.last_article_url:
                article_file = f"result/{site_key}_article.txt"
                with open(article_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {site_key} 最新文章链接\n")
                    f.write(f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"{collector.last_article_url}\n")
            
            # 保存订阅链接
            if v2ray_links:
                subscription_file = f"result/{site_key}_subscription.txt"
                with open(subscription_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {site_key} V2Ray订阅链接\n")
                    f.write(f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"# 共 {len(v2ray_links)} 个链接\n")
                    for i, link in enumerate(v2ray_links, 1):
                        f.write(f"{i}. {link}\n")
            
            # 保存节点
            if nodes:
                nodes_file = f"result/{site_key}_nodes.txt"
                with open(nodes_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {site_key} 节点列表\n")
                    f.write(f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"# 共 {len(nodes)} 个节点\n")
                    f.write("\n")
                    for node in nodes:
                        f.write(f"{node}\n")
            
        except Exception as e:
            self.logger.error(f"保存结果失败: {str(e)}")
    
    def get_available_sites(self) -> list:
        """获取所有可用网站"""
        available_sites = []
        for site_key, site_config in WEBSITES.items():
            if site_config.get("enabled", True):
                collector_key = site_config.get("collector_key", site_key)
                if self.registry.is_collector_available(collector_key):
                    available_sites.append(site_key)
        return available_sites
    
    def run_all_sites(self) -> dict:
        """运行所有网站"""
        results = {}
        available_sites = self.get_available_sites()
        
        self.logger.info(f"开始运行 {len(available_sites)} 个网站...")
        
        for site_key in available_sites:
            success = self.run_site(site_key)
            results[site_key] = success
        
        success_count = sum(results.values())
        self.logger.info(f"运行完成: {success_count}/{len(available_sites)} 个网站成功")
        
        return results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="通用收集器脚本")
    parser.add_argument("site", nargs="?", help="指定要收集的网站")
    parser.add_argument("--all", action="store_true", help="运行所有网站")
    parser.add_argument("--list", action="store_true", help="列出所有可用网站")
    parser.add_argument("--exclude", nargs="+", help="排除的网站（与--all一起使用）")
    parser.add_argument("--test", action="store_true", help="启用连通性测试")
    
    args = parser.parse_args()
    
    collector = UniversalCollector()
    
    # 列出可用网站
    if args.list:
        sites = collector.get_available_sites()
        print("可用网站:")
        for site in sites:
            print(f"  - {site}")
        return
    
    # 运行所有网站
    if args.all:
        sites = collector.get_available_sites()
        if args.exclude:
            sites = [site for site in sites if site not in args.exclude]
        
        results = {}
        for site in sites:
            print(f"\n🚀 运行 {site}...")
            success = collector.run_site(site)
            results[site] = success
            if success:
                print(f"✅ {site}: 成功")
            else:
                print(f"❌ {site}: 失败")
        
        # 汇总结果
        success_count = sum(results.values())
        print(f"\n{'='*60}")
        print(f"运行完成: {success_count}/{len(sites)} 个网站成功")
        if success_count < len(sites):
            failed_sites = [site for site, success in results.items() if not success]
            print(f"失败网站: {', '.join(failed_sites)}")
        return
    
    # 运行指定网站
    if args.site:
        if args.site not in collector.get_available_sites():
            print(f"❌ 网站 '{args.site}' 不可用")
            sys.exit(1)
        
        print(f"🚀 运行 {args.site}...")
        success = collector.run_site(args.site)
        if success:
            print(f"✅ {args.site}: 成功")
        else:
            print(f"❌ {args.site}: 失败")
            sys.exit(1)
        return
    
    # 没有指定参数，显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()