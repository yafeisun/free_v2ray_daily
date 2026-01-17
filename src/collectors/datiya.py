#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Datiya 爬虫
"""

import re
import base64
from datetime import datetime
from bs4 import BeautifulSoup
from .base_collector import BaseCollector


class DatiyaCollector(BaseCollector):
    """Datiya 专用爬虫"""

    def get_latest_article_url(self, target_date=None):
        """获取文章URL，支持指定日期"""
        try:
            self.logger.info(f"访问网站: {self.base_url}")
            response = self._make_request(self.base_url)

            soup = BeautifulSoup(response.text, "html.parser")

            if target_date is None:
                target_date = datetime.now()

            date_str_no_dash = target_date.strftime("%Y%m%d")
            date_str_with_dash = target_date.strftime("%Y-%m-%d")
            date_str_alt = target_date.strftime("%Y/%m/%d")
            date_str_month_day_cn = f"{target_date.month}月{target_date.day}日"
            date_str_month_day_cn_alt = (
                f"{target_date.month:02d}月{target_date.day:02d}日"
            )
            date_str_month_day = target_date.strftime("%m-%d")

            all_links = soup.find_all("a", href=True)
            for link in all_links:
                href = link.get("href")
                text = link.get_text(strip=True)

                if href and (
                    date_str_no_dash in href
                    or date_str_with_dash in href
                    or date_str_alt in href
                    or date_str_month_day_cn in text
                    or date_str_month_day_cn_alt in text
                    or date_str_with_dash in text
                    or date_str_month_day in text
                ):
                    if href and not any(
                        x in href
                        for x in ["category", "tag", "page", "search", "about", "feed"]
                    ):
                        article_url = self._process_url(href)
                        self.logger.info(f"通过日期匹配找到文章: {article_url}")
                        return article_url

            selectors = self.site_config.get("selectors", [])
            for selector in selectors:
                links = soup.select(selector)
                if links:
                    href = links[0].get("href")
                    if href:
                        article_url = self._process_url(href)
                        self.logger.info(f"通过选择器找到文章: {article_url}")
                        return article_url

            self.logger.warning(f"未找到文章链接")
            return None

        except Exception as e:
            self.logger.error(f"获取文章链接失败: {str(e)}")
            return None

    def find_subscription_links(self, content):
        """重写订阅链接查找方法"""
        links = []

        parent_links = super().find_subscription_links(content)
        links.extend(parent_links)

        return list(set(links))

    def get_nodes_from_subscription(self, subscription_url):
        """重写订阅链接处理"""
        try:
            self.logger.info(f"获取订阅内容: {subscription_url}")
            response = self.session.get(
                subscription_url, timeout=self.timeout, verify=False
            )
            response.raise_for_status()

            content = response.text.strip()

            try:
                decoded_content = base64.b64decode(content).decode("utf-8")
                nodes = self.parse_node_text(decoded_content)
            except:
                nodes = self.parse_node_text(content)

            self.logger.info(f"从订阅链接获取到 {len(nodes)} 个节点")
            return nodes

        except Exception as e:
            self.logger.error(f"获取订阅链接失败: {str(e)}")
            return []
