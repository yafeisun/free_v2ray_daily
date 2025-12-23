#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ClashNodeV2Ray 爬虫
"""

import re
from bs4 import BeautifulSoup
from .base_collector import BaseCollector

class ClashNodeV2RayCollector(BaseCollector):
    """ClashNodeV2Ray 专用爬虫"""
    
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
            
            # ClashNodeV2Ray 通常有特定的文章结构
            selectors = [
                '.post-list .post-title a',  # 文章列表
                '.article-list .title a',
                '.content-list h2 a',
                '.blog-list .entry-title a'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                if links:
                    article_url = links[0].get('href')
                    if article_url:
                        article_url = self._process_url(article_url)
                        self.logger.info(f"找到文章: {article_url}")
                        return article_url
            
            # 如果上述选择器都找不到，尝试通用方法
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                # 检查是否是文章链接
                if href and any(keyword in href.lower() for keyword in ['node', 'v2ray', 'clash', 'proxy']):
                    article_url = self._process_url(href)
                    self.logger.info(f"找到文章: {article_url}")
                    return article_url
            
            self.logger.warning("未找到任何文章链接")
            return None
            
        except Exception as e:
            self.logger.error(f"获取文章链接失败: {str(e)}")
            return None    
    def _has_node_content(self, content):
        """检查页面是否包含节点内容"""
        # 检查是否包含V2Ray节点协议
        protocols = ['vmess://', 'vless://', 'trojan://', 'hysteria2://', 'hysteria://', 'ss://']
        for protocol in protocols:
            if protocol in content.lower():
                return True
        return False
    
    def extract_direct_nodes(self, content):
        """重写直接节点提取方法，优化GitHub Pages解析"""
        nodes = []
        
        # 调用父类方法
        parent_nodes = super().extract_direct_nodes(content)
        nodes.extend(parent_nodes)
        
        # GitHub Pages通常使用Markdown格式，可能有特殊的节点展示
        # 查找Markdown代码块
        markdown_patterns = [
            r'```(?:bash|shell|text|nodes?|v2ray)(.*?)```',
            r'```(.*?)```',
        ]
        
        for pattern in markdown_patterns:
            try:
                matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    code_nodes = self.parse_node_text(match)
                    nodes.extend(code_nodes)
            except Exception as e:
                self.logger.warning(f"Markdown代码块匹配失败: {pattern} - {str(e)}")
        
        # 查找可能在列表中的节点
        list_patterns = [
            r'<li[^>]*>(.*?)</li>',
            r'<p[^>]*>(.*?)</p>',
        ]
        
        for pattern in list_patterns:
            try:
                matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    if any(proto in match.lower() for proto in ['vmess://', 'vless://', 'trojan://']):
                        list_nodes = self.parse_node_text(match)
                        nodes.extend(list_nodes)
            except:
                pass
        
        return list(set(nodes))  # 去重