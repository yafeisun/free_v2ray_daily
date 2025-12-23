#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
米贝节点爬虫
"""

import re
from bs4 import BeautifulSoup
from .base_collector import BaseCollector

class Mibei77Collector(BaseCollector):
    """米贝节点专用爬虫"""
    
    def get_latest_article_url(self, target_date=None):
        """重写获取最新文章URL的方法"""
        # 如果指定了日期，使用基类的日期匹配逻辑
        if target_date:
            return super().get_latest_article_url(target_date)
        
        try:
            self.logger.info(f"访问网站: {self.base_url}")
            response = self.session.get(self.base_url, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 米贝节点通常有特定的文章结构
            selectors = [
                '.post-list .post-title a',  # 文章列表
                '.article-list .title a',
                '.content-list h2 a',
                '.blog-list .entry-title a'
            ]
            
            # 先尝试特定选择器
            for selector in selectors:
                links = soup.select(selector)
                if links:
                    href = links[0].get('href')
                    if href:
                        article_url = self._process_url(href)
                        self.logger.info(f"通过特定选择器找到文章: {article_url}")
                        return article_url
            
            # 调用父类方法
            return super().get_latest_article_url()
            
        except Exception as e:
            self.logger.error(f"获取文章链接失败: {str(e)}")
            return None
    
    def extract_direct_nodes(self, content):
        """重写直接节点提取方法"""
        nodes = []
        
        # 调用父类方法
        parent_nodes = super().extract_direct_nodes(content)
        nodes.extend(parent_nodes)
        
        # 米贝节点可能有特殊的节点展示格式
        # 查找包含节点信息的特定区域
        node_areas = [
            r'<div[^>]*class="[^"]*(?:node|config|subscription)[^"]*"[^>]*>(.*?)</div>',
            r'<pre[^>]*class="[^"]*(?:node|config)[^"]*"[^>]*>(.*?)</pre>',
            r'<textarea[^>]*class="[^"]*(?:node|config)[^"]*"[^>]*>(.*?)</textarea>',
        ]
        
        for pattern in node_areas:
            try:
                matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    area_nodes = self.parse_node_text(match)
                    nodes.extend(area_nodes)
            except Exception as e:
                self.logger.warning(f"节点区域匹配失败: {pattern} - {str(e)}")
        
        # 查找可能在表格中的节点
        table_pattern = r'<table[^>]*>(.*?)</table>'
        try:
            tables = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)
            for table in tables:
                table_nodes = self.parse_node_text(table)
                nodes.extend(table_nodes)
        except:
            pass
        
        return list(set(nodes))  # 去重