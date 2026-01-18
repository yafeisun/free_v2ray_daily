#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
玩转迷爬虫
"""

import re
import base64
from bs4 import BeautifulSoup
from src.core.base_collector import BaseCollector


class WanzhuanmiCollector(BaseCollector):
    """玩转迷专用爬虫"""

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

            # 玩转迷网站的最新文章在首页第一个位置
            # 查找所有包含 /archives/ 的链接，第一个通常是最新的
            archive_links = soup.select('h2 a[href*="/archives/"]')

            if archive_links:
                # 获取第一个非置顶的文章链接
                for link in archive_links:
                    href = link.get("href")
                    text = link.get_text(strip=True)

                    # 检查是否包含日期信息 (格式: 2026年01月17日)
                    # 跳过置顶文章（通常不包含具体日期）
                    if href and ("202" in text and "日" in text):
                        article_url = self._process_url(href)
                        self.logger.info(f"找到最新文章: {article_url} - {text}")
                        return article_url

            # 备用：尝试查找今天或最近的日期
            # 先尝试今天的日期，然后尝试昨天、前天等
            from datetime import datetime, timedelta

            for days_ago in range(7):  # 查找最近7天的文章
                check_date = datetime.now() - timedelta(days=days_ago)
                date_str_cn = check_date.strftime("%Y年%m月%d日")
                date_str_cn_alt = check_date.strftime("%Y年%-m月%-d日")  # 去掉前导零

                self.logger.info(f"尝试查找日期: {date_str_cn}")

                all_links = soup.find_all("a", href=re.compile(r"/archives/\d+"))
                for link in all_links:
                    text = link.get_text(strip=True)
                    href = link.get("href")

                    if (date_str_cn in text or date_str_cn_alt in text) and href:
                        article_url = self._process_url(href)
                        self.logger.info(
                            f"通过日期匹配找到文章: {article_url} - {text}"
                        )
                        return article_url

            # 如果还是没找到，使用第一个 archives 链接
            first_archive = soup.select_one('h2 a[href*="/archives/"]')
            if first_archive:
                href = first_archive.get("href")
                if href:
                    article_url = self._process_url(href)
                    self.logger.info(f"使用第一个 archives 链接: {article_url}")
                    return article_url

            # 最后尝试父类方法
            self.logger.warning("未找到特定格式的文章链接，尝试使用父类方法")
            return super().get_latest_article_url()

        except Exception as e:
            self.logger.error(f"获取文章链接失败: {str(e)}")
            return None

    def get_nodes_from_subscription(self, subscription_url):
        """重写订阅链接处理，支持base64解码"""
        try:
            self.logger.info(f"获取订阅内容: {subscription_url}")
            response = self.session.get(
                subscription_url, timeout=self.timeout, verify=False
            )
            response.raise_for_status()

            content = response.text.strip()
            nodes = self.parse_node_text(content)

            # 如果没有找到节点，尝试base64解码
            if not nodes:
                try:
                    # 玩转迷可能使用base64编码
                    decoded_content = base64.b64decode(content).decode(
                        "utf-8", errors="ignore"
                    )
                    self.logger.info("检测到base64编码，已解码内容")
                    nodes = self.parse_node_text(decoded_content)
                except Exception as e:
                    self.logger.warning(f"base64解码失败: {str(e)}")
                    # 尝试其他编码方式
                    try:
                        # 移除可能的填充字符后重试
                        padded_content = content + "=" * (-len(content) % 4)
                        decoded_content = base64.b64decode(padded_content).decode(
                            "utf-8", errors="ignore"
                        )
                        nodes = self.parse_node_text(decoded_content)
                        if nodes:
                            self.logger.info("修复填充字符后解码成功")
                    except Exception as e2:
                        self.logger.warning(f"修复base64解码也失败: {str(e2)}")

            self.logger.info(f"从订阅链接获取到 {len(nodes)} 个节点")
            return nodes

        except Exception as e:
            self.logger.error(f"获取订阅链接失败: {str(e)}")
            return []

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
            r"订阅链接[：:]\s*(https?://[^\s\n\r]+)",
            r"配置链接[：:]\s*(https?://[^\s\n\r]+)",
            r"节点订阅[：:]\s*(https?://[^\s\n\r]+)",
        ]

        for pattern in tech_patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # 清理HTML标签
                    clean_url = re.sub(r"<[^>]+>", "", match).strip()
                    if clean_url and clean_url.startswith(("http://", "https://")):
                        links.append(clean_url)
            except Exception as e:
                self.logger.warning(f"技术链接匹配失败: {pattern} - {str(e)}")

        # 查找可能在技术说明中的链接
        description_patterns = [
            r"说明[：:][^。]*?(https?://[^\s\n\r]+)",
            r"使用方法[：:][^。]*?(https?://[^\s\n\r]+)",
            r"教程[：:][^。]*?(https?://[^\s\n\r]+)",
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
            r"步骤\d*[：:][^。]*?(vmess://[^\s\n\r]+)",
            r"步骤\d*[：:][^。]*?(vless://[^\s\n\r]+)",
            r"步骤\d*[：:][^。]*?(trojan://[^\s\n\r]+)",
            r"配置\d*[：:][^。]*?(vmess://[^\s\n\r]+)",
            r"配置\d*[：:][^。]*?(vless://[^\s\n\r]+)",
            r"配置\d*[：:][^。]*?(trojan://[^\s\n\r]+)",
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
