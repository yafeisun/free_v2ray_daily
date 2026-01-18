#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegeam 爬虫
"""

import re
import base64
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from src.core.base_collector import BaseCollector


class TelegeamCollector(BaseCollector):
    """Telegeam 专用爬虫"""

    def _get_latest_article_url(self):
        """获取最新文章URL - 实现抽象方法"""
        return self.get_latest_article_url()

    def get_latest_article_url(self, target_date=None):
        """重写获取最新文章URL的方法，支持查找最近7天的文章"""
        if target_date:
            return super().get_latest_article_url(target_date)

        try:
            response = self.session.get(
                self.base_url, timeout=self.timeout, verify=False
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for days_ago in range(7):
                check_date = datetime.now() - timedelta(days=days_ago)
                date_patterns = [
                    check_date.strftime("%Y/%m/%d"),
                    check_date.strftime("%Y/%-m/%-d"),
                    check_date.strftime("%m月%d日"),
                    check_date.strftime("%-m月%-d日"),
                ]

                date_info = check_date.strftime("%Y-%m-%d")
                if days_ago == 0:
                    self.logger.info(f"尝试查找今天的文章: {date_info}")
                else:
                    self.logger.info(f"尝试查找 {days_ago} 天前的文章: {date_info}")

                all_links = soup.find_all("a", href=re.compile(r"/\d{4}/\d{2}/\d{2}/"))

                for link in all_links:
                    href = link.get("href")
                    text = link.get_text(strip=True)

                    if href:
                        for pattern in date_patterns:
                            if pattern in href or pattern in text:
                                article_url = self._process_url(href)
                                if days_ago == 0:
                                    self.logger.info(f"找到今天的文章: {article_url}")
                                else:
                                    self.logger.info(
                                        f"今天还没有更新，使用 {days_ago} 天前的文章: {article_url}"
                                    )
                                return article_url

            self.logger.warning("未找到最近7天的文章，使用父类方法")
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

        # 去重
        return list(set(links))

    def get_nodes_from_subscription(self, subscription_url):
        """使用统一订阅解析器处理订阅链接"""
        from src.core.subscription_parser import get_subscription_parser

        parser = get_subscription_parser()
        return parser.parse_subscription_url(subscription_url, self.session)
