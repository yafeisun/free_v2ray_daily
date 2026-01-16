#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram API节点收集器
从Telegram频道和群组自动获取VPN节点
"""

import asyncio

try:
    import aiohttp
except ImportError:
    print("⚠️ aiohttp not installed, some features will be limited")
    aiohttp = None
import json
import re
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import quote

from src.utils.logger import get_logger

try:
    from .multi_source_collector import MultiSourceCollector
except ImportError:
    print("⚠️ MultiSourceCollector not available")
    MultiSourceCollector = None

try:
    from src.utils.logger import get_logger
except ImportError:
    print("⚠️ utils.logger not available")
    get_logger = None


class TelegramCollector(MultiSourceCollector):
    """Telegram节点收集器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # Telegram API配置
        self.bot_token = config.get("bot_token")
        self.channels = config.get("channels", [])
        self.keywords = config.get(
            "keywords", ["vmess", "vless", "trojan", "hysteria", "ss://", "ssr://"]
        )

        # API限制
        self.api_delay = config.get("api_delay", 1.0)  # 秒
        self.max_messages = config.get("max_messages", 100)  # 每次最大消息数
        self.download_timeout = config.get("download_timeout", 30)

        # 正则表达式模式
        self.node_patterns = [
            r"(vmess://[^\s\n\r]+)",
            r"(vless://[^\s\n\r]+)",
            r"(trojan://[^\s\n\r]+)",
            r"(hysteria2?://[^\s\n\r]+)",
            r"(ss://[^\s\n\r]+)",
            r"(ssr://[^\s\n\r]+)",
            # Base64编码的节点
            r"([A-Za-z0-9+/]{100,}={0,2})",
            # 短链接（可能包含节点）
            r"(https?://[^\s\n\r]*\.(?:txt|raw|v2ray|sub)[^\s\n\r]*)",
        ]

        # 会话管理
        self.session = None
        self.last_update = {}

    def validate_source(self) -> bool:
        """验证Telegram API是否可用"""
        if not self.bot_token:
            self.logger.error("Telegram bot token未配置")
            return False

        return True

    async def collect_nodes(self) -> List[Dict[str, Any]]:
        """从多个频道收集节点"""
        if not self.validate_source():
            return []

        all_nodes = []

        try:
            # 使用 TelegramClient (如果可用) 或 fallback HTTP
            if hasattr(self, "client") and self.client:
                # 使用 TelegramClient
                await self.client.start()

                # 并发获取所有频道的节点
                tasks = []
                for channel in self.channels:
                    task = asyncio.create_task(
                        self.collect_from_channel_telethon(channel)
                    )
                    tasks.append(task)

                # 等待所有任务完成
                channel_results = await asyncio.gather(*tasks, return_exceptions=True)

                for i, result in enumerate(channel_results):
                    if isinstance(result, Exception):
                        self.logger.error(
                            f"频道 {self.channels[i]} 收集失败: {str(result)}"
                        )
                    elif result:
                        all_nodes.extend(result)
                        self.logger.info(
                            f"频道 {self.channels[i]}: {len(result)} 个节点"
                        )

                # 关闭连接
                await self.client.disconnect()

            else:
                # Fallback 使用 HTTP 会话
                session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.download_timeout),
                    headers={"User-Agent": "TelegramBot/1.0"},
                )

                # 并发获取所有频道的节点
                tasks = []
                for channel in self.channels:
                    task = asyncio.create_task(
                        self.collect_from_channel_http(channel, session)
                    )
                    tasks.append(task)

                # 等待所有任务完成
                channel_results = await asyncio.gather(*tasks, return_exceptions=True)

                for i, result in enumerate(channel_results):
                    if isinstance(result, Exception):
                        self.logger.error(
                            f"频道 {self.channels[i]} 收集失败: {str(result)}"
                        )
                    elif result:
                        all_nodes.extend(result)
                        self.logger.info(
                            f"频道 {self.channels[i]}: {len(result)} 个节点"
                        )

                # 清理
                await session.close()

            return list(set(all_nodes))  # 去重

        except Exception as e:
            self.logger.error(f"Telegram收集异常: {str(e)}")
            return []

        self.logger.info(f"开始从Telegram收集节点，频道数: {len(self.channels)}")

        all_nodes = []

        try:
            # 创建会话
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.download_timeout),
                headers={"User-Agent": "TelegramBot/1.0"},
            )

            # 并发获取所有频道的节点
            tasks = []
            for channel in self.channels:
                task = asyncio.create_task(self.collect_from_channel(channel))
                tasks.append(task)

            # 等待所有任务完成
            channel_results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(channel_results):
                if isinstance(result, Exception):
                    self.logger.error(
                        f"频道 {self.channels[i]} 收集失败: {str(result)}"
                    )
                elif result:
                    all_nodes.extend(result)
                    self.logger.info(f"频道 {self.channels[i]}: {len(result)} 个节点")

        except Exception as e:
            self.logger.error(f"Telegram收集异常: {str(e)}")
            return []
        finally:
            # 清理
            await self.session.close()

    async def collect_from_channel(self, channel: str) -> List[Dict[str, Any]]:
        """从单个频道收集节点"""
        nodes = []

        if not self.validate_source():
            self.logger.error("Telegram客户端未初始化")
            return nodes

        # 检查频道是否需要更新
        if not self.should_update_channel(channel):
            self.logger.debug(f"频道 {channel} 暂无需更新")
            return nodes

        # 设置截止日期
        cutoff_date = datetime.now() - timedelta(days=self.update_interval)

        try:
            # 获取频道历史消息
            async for message in self.client.iter_messages(channel, limit=500):
                if message.date and message.date.date() < cutoff_date.date():
                    break

                if not hasattr(message, "message") or not message.message:
                    continue

                text = message.message

                # 提取各协议配置
                for protocol, pattern in self.v2ray_patterns.items():
                    matches = re.findall(pattern, text)
                    nodes.extend(matches)

                # 检查文件附件
                if message.document:
                    file_nodes = await self._download_and_parse(message.document)
                    if file_nodes:
                        nodes.extend(file_nodes)

            return list(set(nodes))  # 去重

        except Exception as e:
            self.logger.error(f"从频道 {channel} 收集失败: {str(e)}")
            return []

    def calculate_freshness(self, timestamp: int) -> float:
        """计算新鲜度评分"""
        if not timestamp:
            return 0.5

        age_hours = (
            datetime.now() - datetime.fromtimestamp(timestamp)
        ).total_seconds() / 3600

        if age_hours < 1:
            return 1.0
        elif age_hours < 6:
            return 0.8
        elif age_hours < 24:
            return 0.6
        elif age_hours < 72:
            return 0.4
        else:
            return 0.2

    def should_update_channel(self, channel: str) -> bool:
        """检查频道是否需要更新"""
        if channel not in self.last_update:
            return True

        time_since_update = datetime.now() - self.last_update[channel]
        return time_since_update.total_seconds() > self.update_interval


# 注册Telegram收集器的工厂函数
def create_telegram_collector(config: Dict[str, Any]) -> TelegramCollector:
    """创建Telegram收集器实例"""
    return TelegramCollector(config)


    def collect(self):  # type: ignore
        """简化收集方法"""
        try:
            # 尝试调用现有的节点获取方法
            if hasattr(self, 'get_v2ray_subscription_links') and hasattr(self, 'last_article_url'):
                links = self.get_v2ray_subscription_links(getattr(self, 'last_article_url', ''))
                nodes = []
                for link in links:
                    try:
                        nodes_from_link = self.get_nodes_from_subscription(link)
                        nodes.extend(nodes_from_link)
                    except:
                        pass
                
                return nodes
            
            # 如果有直接节点提取方法
            if hasattr(self, 'extract_direct_nodes'):
                page_content = getattr(self, 'fetch_page', lambda x: "")(self.base_url) if hasattr(self, 'base_url') else ""
                direct_nodes = self.extract_direct_nodes(page_content)
                return direct_nodes
                
        except Exception:
            return []
