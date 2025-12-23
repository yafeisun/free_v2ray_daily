#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
玩转迷爬虫
"""

import re
from bs4 import BeautifulSoup
from .base_collector import BaseCollector

class WanzhuanmiCollector(BaseCollector):
    """玩转迷专用爬虫"""
    
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
            
            # 玩转迷可能有技术分享类网站的结构
            selectors = [
                '.tech-post h2 a',          # 技术文章
                '.tutorial-list h3 a',       # 教程列表
                '.guide-list h2 a',          # 指南列表
                '.tool-share h2 a',          # 工具分享
                '.vpn-post h2 a',            # VPN相关文章
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
    
    def find_subscription_links(self, content):
        """重写订阅链接查找方法"""
        links = []
        
        # 调用父类方法
        parent_links = super().find_subscription_links(content)
        links.extend(parent_links)
        
        # 玩转迷可能有技术分享的特殊格式
        # 查找技术标签中的链接
        tech_patterns = [
            r'<code[^>]*>(https?://[^\s<"]*)</code>',
            r'<pre[^>]*><code[^>]*>(https?://[^\s<"]*)</code></pre>',
            r'订阅链接[：:]\s*(https?://[^\s\n\r]+)',
            r'配置链接[：:]\s*(https?://[^\s\n\r]+)',
            r'节点订阅[：:]\s*(https?://[^\s\n\r]+)',
        ]
        
        for pattern in tech_patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                links.extend(matches)
            except Exception as e:
                self.logger.warning(f"技术链接匹配失败: {pattern} - {str(e)}")
        
        # 查找可能在技术说明中的链接
        description_patterns = [
            r'说明[：:][^。]*?(https?://[^\s\n\r]+)',
            r'使用方法[：:][^。]*?(https?://[^\s\n\r]+)',
            r'教程[：:][^。]*?(https?://[^\s\n\r]+)',
        ]
        
        for pattern in description_patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                links.extend(matches)
            except Exception as e:
                self.logger.warning(f"说明链接匹配失败: {pattern} - {str(e)}")
        
        return list(set(links))  # 去重
    
    def extract_direct_nodes(self, content):
        """重写直接节点提取方法"""
        nodes = []
        
        # 调用父类方法
        parent_nodes = super().extract_direct_nodes(content)
        nodes.extend(parent_nodes)
        
        # 玩转迷可能有技术教程的格式
        # 查找教程步骤中的节点
        tutorial_patterns = [
            r'步骤\d*[：:][^。]*?(vmess://[^\s\n\r]+)',
            r'步骤\d*[：:][^。]*?(vless://[^\s\n\r]+)',
            r'步骤\d*[：:][^。]*?(trojan://[^\s\n\r]+)',
            r'配置\d*[：:][^。]*?(vmess://[^\s\n\r]+)',
            r'配置\d*[：:][^。]*?(vless://[^\s\n\r]+)',
            r'配置\d*[：:][^。]*?(trojan://[^\s\n\r]+)',
        ]
        
        for pattern in tutorial_patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if len(match) >= 20:  # 确保是有效节点
                        nodes.append(match.strip())
            except Exception as e:
                self.logger.warning(f"教程节点匹配失败: {pattern} - {str(e)}")
        
        # 查找可能在下载区域中的节点
        download_patterns = [
            r'<div[^>]*class="[^"]*(?:download|button)[^"]*"[^>]*>(.*?)</div>',
            r'<a[^>]*class="[^"]*(?:download|button)[^"]*"[^>]*>(.*?)</a>',
        ]
        
        for pattern in download_patterns:
            try:
                matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    download_nodes = self.parse_node_text(match)
                    nodes.extend(download_nodes)
            except Exception as e:
                self.logger.warning(f"下载区域匹配失败: {pattern} - {str(e)}")
        
        return list(set(nodes))  # 去重