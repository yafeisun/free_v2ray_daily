#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例网站收集器 - 演示可插拔架构
"""

from src.collectors.base_collector import BaseCollector


class ExampleSiteCollector(BaseCollector):
    """示例网站收集器
    
    这是一个示例收集器，演示如何创建新的网站插件。
    只需要继承BaseCollector并实现必要的方法即可。
    """
    
    def __init__(self, site_config):
        super().__init__(site_config)
        # 可以在这里添加网站特定的初始化逻辑
        self.logger.info(f"初始化示例网站收集器: {self.site_name}")
    
    def get_latest_article_url(self, target_date=None):
        """获取最新文章URL
        
        这个方法演示如何重写基类方法来实现网站特定的逻辑。
        如果不需要特殊逻辑，可以不重写，使用基类的默认实现。
        """
        # 调用基类方法
        return super().get_latest_article_url(target_date)
    
    def find_subscription_links(self, content):
        """查找订阅链接
        
        可以重写这个方法来实现网站特定的订阅链接查找逻辑。
        """
        # 先调用基类方法
        links = super().find_subscription_links(content)
        
        # 添加网站特定的处理逻辑
        # 例如：示例网站可能有特殊的链接格式
        import re
        
        # 示例：查找特定格式的链接
        example_pattern = r'example://([^\s\n\r]+)'
        matches = re.findall(example_pattern, content, re.IGNORECASE)
        links.extend(matches)
        
        return links