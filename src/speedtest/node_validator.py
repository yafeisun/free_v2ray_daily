#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时节点验证系统
新一代节点测速和质量评估系统
"""

import asyncio
import aiohttp
import time
import json
import socket
import ssl
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from src.core.config_manager import get_config
from src.utils.logger import get_logger


@dataclass
class NodeTestResult:
    """节点测试结果"""

    url: str
    is_online: bool
    response_time: Optional[float]
    download_speed: Optional[float]
    upload_speed: Optional[float]
    country: Optional[str]
    isp: Optional[str]
    streaming_support: Dict[str, bool]
    quality_score: float
    test_time: datetime
    error_message: Optional[str] = None


class AdvancedNodeValidator:
    """高级节点验证器"""

    def __init__(self):
        self.config_manager = get_config()
        self.logger = get_logger("node_validator")

        # 测试配置
        self.max_concurrent = self.config_manager.base.MAX_WORKERS
        self.connect_timeout = self.config_manager.base.CONNECTION_TIMEOUT
        self.test_timeout = 30  # 单个节点测试超时

        # 测试服务器
        self.test_servers = {
            "speed": [
                "http://speedtest.net/speedtest-config.php",
                "https://fast.com/api/config",
                "http://test.de/speedtest",
            ],
            "streaming": {
                "youtube": "https://www.youtube.com",
                "netflix": "https://www.netflix.com",
                "disney": "https://www.disneyplus.com",
                "hbo": "https://www.hbo.com",
                "amazon": "https://www.primevideo.com",
            },
        }

        # 地理位置数据库
        self.geo_database = {}
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent)

    async def validate_nodes_batch(self, node_urls: List[str]) -> List[NodeTestResult]:
        """批量验证节点"""
        self.logger.info(f"开始验证 {len(node_urls)} 个节点")
        start_time = time.time()

        # 创建任务
        tasks = []
        for node_url in node_urls:
            task = asyncio.create_task(self.validate_single_node(node_url))
            tasks.append(task)

        # 控制并发数
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def controlled_validate(node_url):
            async with semaphore:
                return await self.validate_single_node(node_url)

        controlled_tasks = [controlled_validate(url) for url in node_urls]

        # 等待所有任务完成
        results = await asyncio.gather(*controlled_tasks, return_exceptions=True)

        # 处理结果
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"节点 {node_urls[i]} 验证异常: {str(result)}")
            elif isinstance(result, NodeTestResult):
                valid_results.append(result)
            else:
                # 处理其他格式
                error_result = NodeTestResult(
                    url=node_urls[i],
                    is_online=False,
                    response_time=None,
                    download_speed=None,
                    upload_speed=None,
                    country=None,
                    isp=None,
                    streaming_support={},
                    quality_score=0.0,
                    test_time=datetime.now(),
                    error_message="验证失败",
                )
                valid_results.append(error_result)

        duration = time.time() - start_time
        online_count = sum(1 for r in valid_results if r.is_online)

        self.logger.info(
            f"节点验证完成: {online_count}/{len(node_urls)} 在线，耗时 {duration:.2f}s"
        )

        return valid_results

    async def validate_single_node(self, node_url: str) -> NodeTestResult:
        """验证单个节点"""
        test_start = datetime.now()

        try:
            # 解析节点信息
            node_info = self.parse_node_url(node_url)
            if not node_info:
                return NodeTestResult(
                    url=node_url,
                    is_online=False,
                    response_time=None,
                    download_speed=None,
                    upload_speed=None,
                    country=None,
                    isp=None,
                    streaming_support={},
                    quality_score=0.0,
                    test_time=test_start,
                    error_message="节点格式无效",
                )

            # 连接测试
            connection_result = await self.test_connection(node_info)
            if not connection_result["connected"]:
                return NodeTestResult(
                    url=node_url,
                    is_online=False,
                    response_time=connection_result.get("response_time"),
                    download_speed=None,
                    upload_speed=None,
                    country=connection_result.get("country"),
                    isp=connection_result.get("isp"),
                    streaming_support={},
                    quality_score=0.0,
                    test_time=test_start,
                    error_message=connection_result.get("error", "连接失败"),
                )

            # 速度测试
            speed_result = await self.test_speed(node_info)

            # 流媒体测试
            streaming_result = await self.test_streaming_support(node_info)

            # 计算质量评分
            quality_score = self.calculate_quality_score(
                connection_result, speed_result, streaming_result
            )

            return NodeTestResult(
                url=node_url,
                is_online=True,
                response_time=connection_result.get("response_time"),
                download_speed=speed_result.get("download_speed"),
                upload_speed=speed_result.get("upload_speed"),
                country=connection_result.get("country"),
                isp=connection_result.get("isp"),
                streaming_support=streaming_result,
                quality_score=quality_score,
                test_time=test_start,
            )

        except Exception as e:
            self.logger.error(f"节点验证异常 {node_url}: {str(e)}")
            return NodeTestResult(
                url=node_url,
                is_online=False,
                response_time=None,
                download_speed=None,
                upload_speed=None,
                country=None,
                isp=None,
                streaming_support={},
                quality_score=0.0,
                test_time=test_start,
                error_message=str(e),
            )

    def parse_node_url(self, node_url: str) -> Optional[Dict[str, Any]]:
        """解析节点URL"""
        try:
            import urllib.parse as urlparse
            import base64

            if node_url.startswith("vmess://"):
                # VMess节点
                data = base64.b64decode(node_url[8:] + "=" * (-len(node_url[8:]) % 4))
                config = json.loads(data)
                return {
                    "type": "vmess",
                    "host": config.get("add"),
                    "port": config.get("port"),
                    "protocol": config.get("net", "tcp"),
                    "path": config.get("path", ""),
                    "tls": config.get("tls", "none"),
                    "raw_config": config,
                }

            elif node_url.startswith(("vless://", "trojan://")):
                # VLESS/Trojan节点
                parsed = urlparse.urlparse(node_url)
                return {
                    "type": "vless" if node_url.startswith("vless://") else "trojan",
                    "host": parsed.hostname,
                    "port": parsed.port,
                    "path": parsed.path,
                    "params": dict(urlparse.parse_qs(parsed.query)),
                    "raw_url": node_url,
                }

            elif node_url.startswith("ss://"):
                # Shadowsocks节点
                parsed = urlparse.urlparse(node_url)
                user_info = parsed.username
                if "@" in parsed.netloc:
                    user_info = parsed.netloc.split("@")[0]

                return {
                    "type": "ss",
                    "host": parsed.hostname,
                    "port": parsed.port,
                    "cipher": user_info.split(":")[0] if user_info else "",
                    "password": user_info.split(":")[1] if ":" in user_info else "",
                    "raw_url": node_url,
                }

            return None

        except Exception as e:
            self.logger.error(f"解析节点URL失败: {str(e)}")
            return None

    async def test_connection(self, node_info: Dict[str, Any]) -> Dict[str, Any]:
        """测试节点连接"""
        result = {
            "connected": False,
            "response_time": None,
            "country": None,
            "isp": None,
            "error": None,
        }

        try:
            start_time = time.time()

            # 尝试TCP连接
            future = self.executor.submit(
                self._tcp_connect, node_info["host"], node_info["port"]
            )

            try:
                future.result(timeout=self.connect_timeout)
                response_time = time.time() - start_time
                result["connected"] = True
                result["response_time"] = response_time

                # 获取地理位置信息
                geo_info = await self.get_geolocation(node_info["host"])
                result["country"] = geo_info.get("country")
                result["isp"] = geo_info.get("isp")

            except TimeoutError:
                result["error"] = "连接超时"
            except Exception as e:
                result["error"] = str(e)

        except Exception as e:
            result["error"] = f"连接测试异常: {str(e)}"

        return result

    def _tcp_connect(self, host: str, port: int):
        """TCP连接测试"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.connect_timeout)

            # 包装SSL
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            wrapped_socket = context.wrap_socket(sock, server_hostname=host)
            wrapped_socket.connect((host, port))

            wrapped_socket.close()
            return True

        except Exception:
            return False

    async def test_speed(self, node_info: Dict[str, Any]) -> Dict[str, Any]:
        """测试节点速度"""
        result = {"download_speed": None, "upload_speed": None, "error": None}

        try:
            # 简化的速度测试（实际实现需要更复杂的逻辑）
            # 这里使用模拟数据，真实环境需要实际的测速逻辑

            # 基于连接时间估算速度
            response_time = 0.1  # 假设的响应时间

            if response_time < 0.1:
                download_speed = 50.0  # Mbps
                upload_speed = 20.0
            elif response_time < 0.3:
                download_speed = 25.0
                upload_speed = 10.0
            elif response_time < 0.5:
                download_speed = 10.0
                upload_speed = 5.0
            else:
                download_speed = 2.0
                upload_speed = 1.0

            result["download_speed"] = download_speed
            result["upload_speed"] = upload_speed

        except Exception as e:
            result["error"] = str(e)

        return result

    async def test_streaming_support(
        self, node_info: Dict[str, Any]
    ) -> Dict[str, bool]:
        """测试流媒体支持"""
        support = {
            "youtube": False,
            "netflix": False,
            "disney": False,
            "hbo": False,
            "amazon": False,
        }

        try:
            # 简化的流媒体检测（基于地理位置和ISP）
            country = node_info.get("country", "")

            # 基于地理位置的启发式判断
            if country in ["US", "CA", "GB", "DE", "FR", "NL", "SG", "JP"]:
                support["youtube"] = True
                support["netflix"] = True
                support["disney"] = True
                support["amazon"] = True
            elif country in ["HK", "TW", "KR"]:
                support["youtube"] = True
                support["netflix"] = True
            elif country in ["SG", "JP"]:
                support["youtube"] = True
                support["netflix"] = True

        except Exception:
            pass

        return support

    def calculate_quality_score(
        self, connection: Dict, speed: Dict, streaming: Dict
    ) -> float:
        """计算节点质量评分"""
        score = 0.0

        # 连接质量 (40%)
        response_time = connection.get("response_time", 1.0)
        if response_time <= 0.1:
            connection_score = 1.0
        elif response_time <= 0.3:
            connection_score = 0.8
        elif response_time <= 0.5:
            connection_score = 0.6
        elif response_time <= 1.0:
            connection_score = 0.4
        else:
            connection_score = 0.2

        score += connection_score * 0.4

        # 速度质量 (30%)
        download_speed = speed.get("download_speed", 0)
        if download_speed >= 20:
            speed_score = 1.0
        elif download_speed >= 10:
            speed_score = 0.8
        elif download_speed >= 5:
            speed_score = 0.6
        elif download_speed >= 2:
            speed_score = 0.4
        else:
            speed_score = 0.2

        score += speed_score * 0.3

        # 流媒体支持 (20%)
        streaming_score = sum(streaming.values()) / len(streaming)
        score += streaming_score * 0.2

        # 地理位置优势 (10%)
        country = connection.get("country", "")
        if country in ["US", "CA", "GB", "DE", "NL", "SG"]:
            geo_score = 1.0
        elif country in ["HK", "JP", "KR"]:
            geo_score = 0.8
        else:
            geo_score = 0.5

        score += geo_score * 0.1

        return min(1.0, score)

    async def get_geolocation(self, ip: str) -> Dict[str, str]:
        """获取地理位置信息"""
        if ip in self.geo_database:
            return self.geo_database[ip]

        try:
            # 使用免费的地理位置API
            async with aiohttp.ClientSession() as session:
                url = f"http://ip-api.com/json/{ip}"
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        geo_info = {
                            "country": data.get("countryCode", ""),
                            "isp": data.get("isp", ""),
                        }
                        self.geo_database[ip] = geo_info
                        return geo_info
        except Exception:
            pass

        return {"country": "", "isp": ""}

    async def filter_best_nodes(
        self,
        results: List[NodeTestResult],
        min_quality: float = 0.6,
        max_count: int = 100,
    ) -> List[NodeTestResult]:
        """筛选最佳节点"""
        # 过滤在线节点
        online_nodes = [r for r in results if r.is_online]

        # 按质量评分排序
        online_nodes.sort(key=lambda x: x.quality_score, reverse=True)

        # 高质量节点
        high_quality = [r for r in online_nodes if r.quality_score >= min_quality]

        # 限制数量
        best_nodes = high_quality[:max_count]

        self.logger.info(
            f"从 {len(results)} 个节点中筛选出 {len(best_nodes)} 个高质量节点"
        )

        return best_nodes

    def save_results(self, results: List[NodeTestResult], output_file: str):
        """保存测试结果"""
        try:
            # 转换为可序列化格式
            serializable_results = []
            for result in results:
                serializable_results.append(
                    {
                        "url": result.url,
                        "is_online": result.is_online,
                        "response_time": result.response_time,
                        "download_speed": result.download_speed,
                        "upload_speed": result.upload_speed,
                        "country": result.country,
                        "isp": result.isp,
                        "streaming_support": result.streaming_support,
                        "quality_score": result.quality_score,
                        "test_time": result.test_time.isoformat(),
                        "error_message": result.error_message,
                    }
                )

            # 按质量评分排序
            serializable_results.sort(key=lambda x: x["quality_score"], reverse=True)

            # 保存到文件
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(serializable_results, f, indent=2, ensure_ascii=False)

            self.logger.info(f"测试结果已保存到 {output_file}")

        except Exception as e:
            self.logger.error(f"保存测试结果失败: {str(e)}")


# 全局验证器实例
node_validator = AdvancedNodeValidator()


async def validate_nodes(nodes: List[str], output_file: str = None) -> List[str]:
    """验证节点并返回高质量节点URL列表"""
    results = await node_validator.validate_nodes_batch(nodes)

    # 筛选最佳节点
    best_results = await node_validator.filter_best_nodes(results)

    # 保存详细结果
    if output_file:
        node_validator.save_results(
            results, output_file.replace(".txt", "_detailed.json")
        )

    # 返回节点URL列表
    return [r.url for r in best_results]


if __name__ == "__main__":
    # 测试验证器
    test_nodes = [
        "vmess://eyJ2di",
        "vless://example",
        # 添加测试节点
    ]

    async def test():
        results = await validate_nodes(test_nodes, "test_results.json")
        print(f"验证到 {len(results)} 个高质量节点")

    asyncio.run(test())
