#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ClashGithub 网站独立脚本
获取最新的节点文章和订阅链接
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.collectors.clashgithub import ClashGithubCollector
from src.utils.logger import get_logger
from src.utils.file_handler import FileHandler
from config.websites import WEBSITES

def main():
    """主函数"""
    logger = get_logger("clashgithub")
    file_handler = FileHandler()
    
    try:
        # 初始化收集器
        site_name = 'clashgithub'
        collector = ClashGithubCollector(WEBSITES[site_name])
        
        logger.info(f"开始收集 {site_name} 的节点...")
        
        # 获取最新文章链接
        article_url = collector.get_latest_article_url()
        if not article_url:
            logger.error(f"{site_name}: 未找到最新文章")
            return False
        
        logger.info(f"{site_name}: 找到最新文章 {article_url}")
        
        # 保存文章链接到独立文件
        result_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "result")
        os.makedirs(result_dir, exist_ok=True)
        
        article_file = os.path.join(result_dir, f"{site_name}_article.txt")
        with open(article_file, 'w', encoding='utf-8') as f:
            f.write(f"# {site_name} 最新文章链接\n")
            f.write(f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{article_url}\n")
        
        logger.info(f"文章链接已保存到 {article_file}")
        
        # 获取V2Ray订阅链接
        v2ray_links = collector.get_v2ray_subscription_links(article_url)
        
        # 保存订阅链接
        subscription_file = os.path.join(result_dir, f"{site_name}_subscription.txt")
        with open(subscription_file, 'w', encoding='utf-8') as f:
            f.write(f"# {site_name} V2Ray订阅链接\n")
            f.write(f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 文章链接: {article_url}\n")
            f.write(f"# 链接数量: {len(v2ray_links)}\n")
            f.write("-" * 60 + "\n\n")
            
            for i, link in enumerate(v2ray_links, 1):
                f.write(f"{link}\n")
        
        logger.info(f"订阅链接已保存到 {subscription_file}，共 {len(v2ray_links)} 个链接")
        
        # 保存订阅链接
        subscription_file = os.path.join(result_dir, f"{site_name}_subscription.txt")
        with open(subscription_file, 'w', encoding='utf-8') as f:
            f.write(f"# {site_name} V2Ray订阅链接\n")
            f.write(f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 文章链接: {article_url}\n")
            f.write(f"# 链接数量: {len(v2ray_links)}\n")
            f.write("-" * 60 + "\n\n")
            
            for i, link in enumerate(v2ray_links, 1):
                f.write(f"{link}\n")
        
        logger.info(f"订阅链接已保存到 {subscription_file}，共 {len(v2ray_links)} 个链接")
        
        logger.info(f"{site_name} 收集完成")
        return True
        
    except Exception as e:
        logger.error(f"运行 {site_name} 脚本时发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)