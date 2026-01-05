#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插件化主程序入口 - 支持可插拔架构
"""

import sys
import os
import time
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.utils.logger import get_logger
from src.utils.file_handler import FileHandler
from src.testers.connectivity_tester import ConnectivityTester
from src.core.plugin_registry import get_registry
from config.settings import *
from config.websites import WEBSITES


class PluginNodeCollector:
    """插件化节点收集器主类"""
    
    def __init__(self):
        self.logger = get_logger("plugin_main")
        self.file_handler = FileHandler()
        self.connectivity_tester = ConnectivityTester()
        
        # 获取插件注册器
        self.registry = get_registry()
        
        # 动态创建收集器实例
        self.collectors = {}
        self._initialize_collectors()
        
        self.all_nodes = []
        self.v2ray_subscription_links = []
        self.v2ray_links_with_source = []
        self.articles_with_source = []
        self.source_info = {}
    
    def _initialize_collectors(self):
        """动态初始化收集器"""
        self.logger.info("开始初始化收集器...")
        
        for site_key, site_config in WEBSITES.items():
            if not site_config.get("enabled", True):
                self.logger.info(f"跳过已禁用的网站: {site_key}")
                continue
            
            try:
                # 获取收集器关键字
                collector_key = site_config.get("collector_key", site_key)
                
                # 检查收集器是否可用
                if not self.registry.is_collector_available(collector_key):
                    self.logger.warning(f"未找到网站 '{site_key}' 的收集器插件: {collector_key}")
                    continue
                
                # 创建收集器实例
                collector = self.registry.create_collector_instance(collector_key, site_config)
                self.collectors[site_key] = collector
                
                self.logger.info(f"成功初始化收集器: {site_key} -> {collector.__class__.__name__}")
                
            except Exception as e:
                self.logger.error(f"初始化收集器失败 {site_key}: {str(e)}")
        
        self.logger.info(f"共初始化了 {len(self.collectors)} 个收集器: {list(self.collectors.keys())}")
    
    def collect_all_nodes(self):
        """收集所有网站的节点"""
        self.logger.info("=" * 50)
        self.logger.info("开始收集节点")
        self.logger.info("=" * 50)
        
        start_time = time.time()
        today = datetime.now().strftime('%Y-%m-%d')
        date_suffix = datetime.now().strftime('%Y%m%d')
        
        for site_name, collector in self.collectors.items():
            try:
                self.logger.info(f"正在收集 {site_name} 的节点...")
                
                # 收集节点
                nodes = collector.collect()
                
                # 收集V2Ray订阅链接
                v2ray_links = []
                if hasattr(collector, 'last_article_url') and collector.last_article_url:
                    v2ray_links = collector.get_v2ray_subscription_links(collector.last_article_url)
                
                # 保存文章链接信息
                if hasattr(collector, 'last_article_url') and collector.last_article_url:
                    self.articles_with_source.append({
                        'website_name': site_name,
                        'article_url': collector.last_article_url,
                        'date': today
                    })
                
                # 记录V2Ray订阅链接信息
                if not v2ray_links:
                    self.v2ray_links_with_source.append({
                        'url': '# 无V2Ray订阅链接',
                        'source': site_name,
                        'source_url': collector.last_article_url if hasattr(collector, 'last_article_url') else 'N/A'
                    })
                else:
                    for link in v2ray_links:
                        self.v2ray_links_with_source.append({
                            'url': link,
                            'source': site_name,
                            'source_url': collector.last_article_url
                        })
                
                if nodes:
                    self.all_nodes.extend(nodes)
                    self.v2ray_subscription_links.extend(v2ray_links)
                    
                    self.source_info[site_name] = {
                        "count": len(nodes),
                        "enabled": collector.enabled,
                        "subscription_links": len(collector.subscription_links),
                        "v2ray_links": len(v2ray_links),
                        "links": collector.subscription_links[:5],
                        "v2ray_link_samples": v2ray_links[:5]
                    }
                    self.logger.info(f"{site_name} 收集完成: {len(nodes)} 个节点，{len(v2ray_links)} 个V2Ray订阅链接")
                else:
                    self.source_info[site_name] = {
                        "count": 0,
                        "enabled": collector.enabled,
                        "subscription_links": 0,
                        "v2ray_links": 0,
                        "links": [],
                        "v2ray_link_samples": []
                    }
                    self.logger.warning(f"{site_name} 未收集到节点")
                
                # 请求间隔
                if site_name != list(self.collectors.keys())[-1]:
                    time.sleep(REQUEST_DELAY)
                    
            except Exception as e:
                self.logger.error(f"收集 {site_name} 时出错: {str(e)}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 去重
        original_count = len(self.all_nodes)
        self.all_nodes = list(set(self.all_nodes))
        duplicate_count = original_count - len(self.all_nodes)
        
        original_v2ray_count = len(self.v2ray_subscription_links)
        self.v2ray_subscription_links = list(set(self.v2ray_subscription_links))
        v2ray_duplicate_count = original_v2ray_count - len(self.v2ray_subscription_links)
        
        self.logger.info("=" * 50)
        self.logger.info("节点收集完成")
        self.logger.info(f"总收集时间: {duration:.2f}秒")
        self.logger.info(f"原始节点数: {original_count}")
        self.logger.info(f"去重后节点数: {len(self.all_nodes)}")
        self.logger.info(f"重复节点数: {duplicate_count}")
        self.logger.info(f"原始V2Ray订阅链接数: {original_v2ray_count}")
        self.logger.info(f"去重后V2Ray订阅链接数: {len(self.v2ray_subscription_links)}")
        self.logger.info(f"重复V2Ray订阅链接数: {v2ray_duplicate_count}")
        self.logger.info("=" * 50)
        
        return self.all_nodes
    
    def get_available_sites(self):
        """获取所有可用的网站列表"""
        return list(self.collectors.keys())
    
    def get_plugin_info(self):
        """获取插件信息"""
        info = {}
        for site_key in self.collectors:
            metadata = self.registry.get_collector_metadata(site_key)
            info[site_key] = {
                'collector_class': metadata.get('class_name', 'Unknown'),
                'module': metadata.get('module', 'Unknown'),
                'description': metadata.get('description', 'No description'),
                'enabled': WEBSITES[site_key].get('enabled', True)
            }
        return info


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="插件化免费V2Ray节点收集器")
    parser.add_argument("--test", action="store_true", help="启用连通性测试")
    parser.add_argument("--update-github", action="store_true", help="更新GitHub仓库")
    parser.add_argument("--sites", nargs="+", help="指定要收集的网站")
    parser.add_argument("--list-sites", action="store_true", help="列出所有可用网站")
    parser.add_argument("--plugin-info", action="store_true", help="显示插件信息")
    
    args = parser.parse_args()
    
    # 创建收集器
    collector = PluginNodeCollector()
    
    # 列出可用网站
    if args.list_sites:
        available_sites = collector.get_available_sites()
        print("可用网站:")
        for site in available_sites:
            print(f"  - {site}")
        return
    
    # 显示插件信息
    if args.plugin_info:
        info = collector.get_plugin_info()
        print("插件信息:")
        for site, data in info.items():
            print(f"  {site}:")
            print(f"    类名: {data['collector_class']}")
            print(f"    模块: {data['module']}")
            print(f"    描述: {data['description']}")
            print(f"    启用: {data['enabled']}")
        return
    
    # 如果指定了特定网站，只启用这些网站
    if args.sites:
        for site_name in list(collector.collectors.keys()):
            if site_name not in args.sites:
                del collector.collectors[site_name]
                collector.logger.info(f"禁用网站: {site_name}")
    
    # 运行收集
    success = collector.run(test_connectivity=args.test)
    
    # 更新GitHub
    if success and args.update_github:
        collector.update_github()
    
    if success:
        print("✓ 任务完成")
        sys.exit(0)
    else:
        print("✗ 任务失败")
        sys.exit(1)


if __name__ == "__main__":
    main()