#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouNeedWin 爬虫
"""

import re
import base64
from bs4 import BeautifulSoup
from .base_collector import BaseCollector

class YouNeedWinCollector(BaseCollector):
    """YouNeedWin 专用爬虫"""
    
    def find_subscription_links(self, content):
        """重写订阅链接查找方法"""
        links = []
        
        # 调用父类方法
        parent_links = super().find_subscription_links(content)
        links.extend(parent_links)
        
        # 去重
        return list(set(links))
    
    def get_nodes_from_subscription(self, subscription_url):
        """重写订阅链接处理"""
        try:
            self.logger.info(f"获取订阅内容: {subscription_url}")
            response = self.session.get(subscription_url, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            content = response.text.strip()
            
            # 如果是base64编码，先解码
            try:
                decoded_content = base64.b64decode(content).decode('utf-8')
                nodes = self.parse_node_text(decoded_content)
            except:
                # 如果不是base64，直接解析
                nodes = self.parse_node_text(content)
            
            # 保留所有协议的节点
            self.logger.info(f"从订阅链接获取到 {len(nodes)} 个节点")
            return nodes
            
        except Exception as e:
            self.logger.error(f"获取订阅链接失败: {str(e)}")
            return []