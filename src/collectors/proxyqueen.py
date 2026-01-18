#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProxyQueen 爬虫
"""

import re
from bs4 import BeautifulSoup
from src.core.base_collector import BaseCollector


class ProxyQueenCollector(BaseCollector):
    """ProxyQueen 专用爬虫"""

    def _get_latest_article_url(self):
        """获取最新文章URL - 实现抽象方法"""
        return self.get_latest_article_url()

    def get_latest_article_url(self, target_date=None):
        """重写获取最新文章URL的方法"""
        # 如果指定了日期，使用基类的日期匹配逻辑
        if target_date:
            return super().get_latest_article_url(target_date)

        try:
            response = self.session.get(
                self.base_url, timeout=self.timeout, verify=False
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            selectors = [
                'a[href*="/archives/"]',
                "article h2 a",
                ".post-title a",
                ".entry-title a",
            ]

            # 先尝试特定选择器
            for selector in selectors:
                links = soup.select(selector)
                if links:
                    href = links[0].get("href")
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

        # ProxyQueen可能有特殊的订阅链接格式
        # 查找区域特定的订阅链接
        region_patterns = [
            r"(?:美国|日本|新加坡|香港|韩国|德国|英国|法国|加拿大|澳大利亚)[^:]*[:：]\s*(https?://[^\s\n\r]+)",
            r"(?:USA|Japan|Singapore|Hong Kong|Korea|Germany|UK|France|Canada|Australia)[^:]*[:：]\s*(https?://[^\s\n\r]+)",
            r"(?:us|jp|sg|hk|kr|de|uk|fr|ca|au)[^:]*[:：]\s*(https?://[^\s\n\r]+)",
        ]

        for pattern in region_patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                links.extend(matches)
            except Exception as e:
                self.logger.warning(f"区域订阅链接匹配失败: {pattern} - {str(e)}")

        # 查找可能的API端点
        api_patterns = [
            r'/api/v1/[^\\s\\\'"]*',
            r'/api/node[^\\s\\\'"]*',
            r'/subscribe/[^\\s\\\'"]*',
        ]

        for pattern in api_patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if match.startswith("/"):
                        full_url = self._process_url(match)
                    else:
                        full_url = match

                    if full_url not in links:
                        links.append(full_url)
            except Exception as e:
                self.logger.warning(f"API端点匹配失败: {pattern} - {str(e)}")

        return list(set(links))  # 去重

    def extract_direct_nodes(self, content):
        """重写直接节点提取方法"""
        nodes = []

        # 调用父类方法
        parent_nodes = super().extract_direct_nodes(content)
        nodes.extend(parent_nodes)

        # ProxyQueen可能按区域组织节点
        # 查找区域标题下的节点
        section_patterns = [
            r"<h[1-6][^>]*>(?:美国|USA|US)[^<]*</h[1-6]>(.*?)(?=<h[1-6]|$)",
            r"<h[1-6][^>]*>(?:日本|Japan|JP)[^<]*</h[1-6]>(.*?)(?=<h[1-6]|$)",
            r"<h[1-6][^>]*>(?:新加坡|Singapore|SG)[^<]*</h[1-6]>(.*?)(?=<h[1-6]|$)",
            r"<h[1-6][^>]*>(?:香港|Hong Kong|HK)[^<]*</h[1-6]>(.*?)(?=<h[1-6]|$)",
        ]

        for pattern in section_patterns:
            try:
                matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    section_nodes = self.parse_node_text(match)
                    nodes.extend(section_nodes)
            except Exception as e:
                self.logger.warning(f"区域节点匹配失败: {pattern} - {str(e)}")

        return list(set(nodes))  # 去重
