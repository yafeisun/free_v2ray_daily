#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenProxyList V2Ray节点收集器
从OpenProxyList获取高质量的V2Ray节点
"""

import requests
import base64
import re
import time
import random
from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs

from .base_collector import BaseCollector
from src.utils.logger import get_logger


class OpenProxyListCollector(BaseCollector):
    """OpenProxyList节点收集器"""

    def __init__(self, site_config):
        super().__init__(site_config)

        # OpenProxyList特定配置
        self.base_url = "https://openproxylist.com"
        self.subscription_url = "https://openproxylist.com/v2ray/rawlist/text"

        # 增强请求头，模拟真实浏览器
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/plain,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "DNT": "1",
                "Connection": "keep-alive",
            }
        )

        # 请求间隔控制（避免被限流）
        self.request_delay = (1, 3)  # 1-3秒随机延迟

    def collect(self) -> List[str]:
        """收集OpenProxyList节点"""
        all_nodes = []

        try:
            self.logger.info(f"开始收集 {self.site_name} 的节点...")

            # 获取主页面信息
            main_info = self._get_main_info()
            if main_info:
                all_nodes.extend(main_info)

            # 获取订阅文件内容
            subscription_nodes = self._get_subscription_nodes()
            if subscription_nodes:
                all_nodes.extend(subscription_nodes)

            # 尝试获取备用端点
            backup_nodes = self._get_backup_nodes()
            if backup_nodes:
                all_nodes.extend(backup_nodes)

            # 去重并返回
            unique_nodes = list(set(all_nodes))
            self.logger.info(f"{self.site_name}: 收集到 {len(unique_nodes)} 个节点")

            # 保存原始数据
            self.save_raw_data(self.subscription_url)

            return unique_nodes

        except Exception as e:
            self.logger.error(f"收集 {self.site_name} 失败: {str(e)}")
            return []

    def _get_main_info(self) -> List[str]:
        """获取主页面信息"""
        try:
            self.logger.info(f"访问主页面: {self.base_url}")
            time.sleep(random.uniform(*self.request_delay))

            response = self.session.get(self.base_url, timeout=self.timeout)
            response.raise_for_status()

            content = response.text
            nodes = []

            # 从主页面提取订阅链接
            subscription_patterns = [
                r'href=["\']([^"\']*v2ray[^"\']*\.txt[^"\']*)["\']',
                r'href=["\']([^"\']*rawlist[^"\']*)["\']',
                r'href=["\']([^"\']*subscription[^"\']*)["\']',
                r'(https://openproxylist\.com/[^\s\'"]*\.txt[^\s\'"]*)',
            ]

            for pattern in subscription_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if "openproxylist.com" in match.lower():
                        self.logger.info(f"主页面发现订阅链接: {match}")
                        sub_nodes = self._fetch_subscription_content(match)
                        if sub_nodes:
                            nodes.extend(sub_nodes)

            if nodes:
                self.logger.info(f"主页面获取到 {len(nodes)} 个节点")

            return nodes

        except Exception as e:
            self.logger.error(f"获取主页面信息失败: {str(e)}")
            return []

    def _get_subscription_nodes(self) -> List[str]:
        """获取订阅文件节点"""
        try:
            self.logger.info(f"获取主要订阅内容: {self.subscription_url}")
            time.sleep(random.uniform(*self.request_delay))

            response = self.session.get(self.subscription_url, timeout=self.timeout)
            response.raise_for_status()

            content = response.text.strip()

            if not content:
                self.logger.warning("订阅内容为空")
                return []

            nodes = self._parse_node_content(content)
            self.logger.info(f"主要订阅获取到 {len(nodes)} 个节点")

            return nodes

        except Exception as e:
            self.logger.error(f"获取订阅内容失败: {str(e)}")
            return []

    def _get_backup_nodes(self) -> List[str]:
        """获取备用端点节点"""
        backup_endpoints = [
            "https://openproxylist.com/v2ray/rawlist",
            "https://openproxylist.com/v2ray/text",
            "https://openproxylist.com/v2ray/nodes",
            "https://openproxylist.com/v2ray/subscribe",
        ]

        all_nodes = []

        for endpoint in backup_endpoints:
            if endpoint == self.subscription_url:
                continue  # 已经请求过

            try:
                self.logger.info(f"尝试备用端点: {endpoint}")
                time.sleep(random.uniform(*self.request_delay))

                response = self.session.get(endpoint, timeout=10)  # 较短超时
                response.raise_for_status()

                content = response.text.strip()
                if content:
                    nodes = self._parse_node_content(content)
                    if nodes:
                        all_nodes.extend(nodes)
                        self.logger.info(f"备用端点获取到 {len(nodes)} 个节点")
                        break  # 找到有效节点就停止

            except Exception as e:
                self.logger.debug(f"备用端点 {endpoint} 失败: {str(e)}")
                continue

        return all_nodes

    def _fetch_subscription_content(self, url: str) -> List[str]:
        """获取特定订阅链接的内容"""
        try:
            time.sleep(random.uniform(*self.request_delay))

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            content = response.text.strip()
            if content:
                return self._parse_node_content(content)

            return []

        except Exception as e:
            self.logger.error(f"获取订阅链接 {url} 失败: {str(e)}")
            return []

    def _parse_node_content(self, content: str) -> List[str]:
        """解析节点内容（支持多种格式）"""
        if not content:
            return []

        nodes = []

        # 检查是否为Base64编码
        if self._is_base64_content(content):
            try:
                self.logger.debug("检测到Base64编码，尝试解码")
                decoded_content = base64.b64decode(content).decode(
                    "utf-8", errors="ignore"
                )
                nodes.extend(self._extract_nodes_from_text(decoded_content))
            except Exception as e:
                self.logger.debug(f"Base64解码失败: {str(e)}")
                # 如果解码失败，尝试直接解析
                nodes.extend(self._extract_nodes_from_text(content))
        else:
            # 直接解析文本内容
            nodes.extend(self._extract_nodes_from_text(content))

        return nodes

    def _is_base64_content(self, content: str) -> bool:
        """判断是否为Base64编码内容"""
        try:
            # 检查是否为有效的Base64格式
            # 移除空白字符
            clean_content = re.sub(r"\s+", "", content)

            # 长度检查（Base64通常较长）
            if len(clean_content) < 100:
                return False

            # 尝试解码
            decoded = base64.b64decode(clean_content + "==")  # 补全padding
            decoded_text = decoded.decode("utf-8", errors="ignore")

            # 检查解码后是否包含节点协议
            protocols = ["vmess://", "vless://", "ss://", "trojan://", "hysteria"]
            return any(proto in decoded_text for proto in protocols)

        except:
            return False

    def _extract_nodes_from_text(self, text: str) -> List[str]:
        """从文本中提取节点"""
        nodes = []

        # 多协议匹配模式
        patterns = [
            r"(vmess://[^\s\n\r]+)",
            r"(vless://[^\s\n\r]+)",
            r"(trojan://[^\s\n\r]+)",
            r"(hysteria2?://[^\s\n\r]+)",
            r"(ss://[^\s\n\r]+)",
            r"(ssr://[^\s\n\r]+)",
            # Reality VLESS模式（常见格式）
            r"(vless://[a-f0-9-]+@[^\s\n\r]+\?security=reality[^\s\n\r]+)",
            # 混合内容中的Base64编码节点
            r"([A-Za-z0-9+/]{100,}={0,2}(?:.*?(?:vmess|vless|trojan|ss|hysteria).*?))",
        ]

        for line_num, line in enumerate(text.split("\n"), 1):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("//"):
                continue

            for pattern in patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                for match in matches:
                    clean_node = self._clean_node(match)
                    if clean_node and len(clean_node) > 20:  # 基本长度检查
                        nodes.append(clean_node)
                        self.logger.debug(
                            f"第{line_num}行匹配节点: {clean_node[:50]}..."
                        )

        return nodes

    def _clean_node(self, node: str) -> str:
        """清理和验证节点"""
        try:
            # 移除多余空白
            node = re.sub(r"\s+", "", node.strip())

            # 验证协议格式
            if node.startswith("vmess://"):
                return self._validate_vmess(node)
            elif node.startswith("vless://"):
                return self._validate_vless(node)
            elif node.startswith("trojan://"):
                return self._validate_trojan(node)
            elif node.startswith("ss://"):
                return self._validate_ss(node)
            elif node.startswith("hysteria") and "://" in node:
                return self._validate_hysteria(node)
            else:
                return node if len(node) > 20 else None

        except Exception as e:
            self.logger.debug(f"节点清理失败: {str(e)}")
            return None

    def _validate_vmess(self, node: str) -> str:
        """验证VMess节点"""
        try:
            if len(node.split("vmess://")[1]) < 10:
                return None

            # VMess格式通常为base64编码的JSON
            b64_part = node.split("vmess://")[1]
            base64.b64decode(b64_part + "==")
            return node
        except:
            return None

    def _validate_vless(self, node: str) -> str:
        """验证VLESS节点"""
        try:
            # VLESS格式: vless://uuid@host:port?params
            if not re.match(r"vless://[a-f0-9-]+@[^\s:]+:\d+", node):
                return None
            return node
        except:
            return None

    def _validate_trojan(self, node: str) -> str:
        """验证Trojan节点"""
        try:
            # Trojan格式: trojan://password@host:port?sni=xxx
            if not re.match(r"trojan://[^@]+@[^\s:]+:\d+", node):
                return None
            return node
        except:
            return None

    def _validate_ss(self, node: str) -> str:
        """验证Shadowsocks节点"""
        try:
            # SS格式: ss://base64(method:password@host:port)
            if len(node.split("ss://")[1]) < 10:
                return None
            base64.b64decode(node.split("ss://")[1] + "==")
            return node
        except:
            return None

    def _validate_hysteria(self, node: str) -> str:
        """验证Hysteria节点"""
        try:
            # Hysteria格式: hysteria://host:port?auth=xxx
            if "://" not in node or len(node.split("://")[1]) < 10:
                return None
            return node
        except:
            return None
