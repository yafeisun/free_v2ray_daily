#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
节点自测系统
独立验证节点质量，不依赖外部服务
"""

import sys
import asyncio
import socket
import ssl
import time
import json
import re
import base64
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse, parse_qs
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.utils.logger import get_logger
except ImportError:
    import logging

    def get_logger(name):
        return logging.getLogger(name)


class NodeTester:
    """节点测试器 - 独立验证节点质量"""

    def __init__(self):
        self.logger = get_logger("node_tester")
        self.test_results = []

        # 测试配置
        self.connect_timeout = 5.0
        self.test_timeout = 10.0
        self.max_concurrent = 20

        # 质量评分权重
        self.quality_weights = {
            "connectivity": 0.4,  # 连接性
            "response_time": 0.3,  # 响应时间
            "protocol_support": 0.2,  # 协议支持
            "format_valid": 0.1,  # 格式有效性
        }

    def parse_node(self, node_url: str) -> Optional[Dict[str, Any]]:
        """解析节点URL"""
        try:
            if node_url.startswith("vmess://"):
                return self._parse_vmess(node_url)
            elif node_url.startswith("vless://"):
                return self._parse_vless(node_url)
            elif node_url.startswith("trojan://"):
                return self._parse_trojan(node_url)
            elif node_url.startswith("ss://"):
                return self._parse_shadowsocks(node_url)
            elif node_url.startswith("ssr://"):
                return self._parse_shadowsocksr(node_url)
            else:
                return None
        except Exception as e:
            self.logger.error(f"解析节点失败 {node_url}: {str(e)}")
            return None

    def _parse_vmess(self, vmess_url: str) -> Optional[Dict[str, Any]]:
        """解析VMess节点"""
        try:
            # 移除vmess://前缀
            encoded = vmess_url[8:]

            # 修复base64填充
            missing_padding = len(encoded) % 4
            if missing_padding:
                encoded += "=" * (4 - missing_padding)

            # 解码JSON
            decoded = base64.b64decode(encoded).decode("utf-8")
            config = json.loads(decoded)

            return {
                "type": "vmess",
                "host": config.get("add"),
                "port": int(config.get("port", 443)),
                "uuid": config.get("id"),
                "alterId": int(config.get("aid", 0)),
                "security": config.get("tls", "none"),
                "network": config.get("net", "tcp"),
                "path": config.get("path", "/"),
                "host_header": config.get("host", ""),
                "ps": config.get("ps", ""),
                "raw_config": config,
            }
        except Exception as e:
            self.logger.error(f"VMess解析失败: {str(e)}")
            return None

    def _parse_vless(self, vless_url: str) -> Optional[Dict[str, Any]]:
        """解析VLESS节点"""
        try:
            parsed = urlparse(vless_url)

            return {
                "type": "vless",
                "host": parsed.hostname,
                "port": parsed.port or 443,
                "uuid": parsed.username,
                "security": parsed.query.get("security", "none"),
                "network": parsed.query.get("type", "tcp"),
                "path": parsed.path or "/",
                "host_header": parsed.query.get("host", ""),
                "ps": parsed.fragment or "",
                "raw_url": vless_url,
            }
        except Exception as e:
            self.logger.error(f"VLESS解析失败: {str(e)}")
            return None

    def _parse_trojan(self, trojan_url: str) -> Optional[Dict[str, Any]]:
        """解析Trojan节点"""
        try:
            parsed = urlparse(trojan_url)

            return {
                "type": "trojan",
                "host": parsed.hostname,
                "port": parsed.port or 443,
                "password": parsed.username,
                "security": "tls",
                "network": "tcp",
                "path": parsed.path or "/",
                "host_header": parsed.query.get("sni", ""),
                "ps": parsed.fragment or "",
                "raw_url": trojan_url,
            }
        except Exception as e:
            self.logger.error(f"Trojan解析失败: {str(e)}")
            return None

    def _parse_shadowsocks(self, ss_url: str) -> Optional[Dict[str, Any]]:
        """解析Shadowsocks节点"""
        try:
            # 处理base64编码的SS
            if "@" in ss_url:
                # userinfo@host:port 格式
                parsed = urlparse(ss_url)
                method = parsed.username
                password = parsed.password
                host = parsed.hostname
                port = parsed.port
            else:
                # base64编码格式
                encoded = ss_url[5:]  # 移除ss://
                missing_padding = len(encoded) % 4
                if missing_padding:
                    encoded += "=" * (4 - missing_padding)

                decoded = base64.b64decode(encoded).decode("utf-8")
                if "@" in decoded:
                    method_password, host_port = decoded.split("@")
                    method, password = method_password.split(":")
                    host, port = host_port.split(":")
                else:
                    return None

            return {
                "type": "ss",
                "host": host,
                "port": int(port),
                "method": method,
                "password": password,
                "security": "none",
                "network": "tcp",
                "path": "/",
                "host_header": "",
                "ps": "",
                "raw_url": ss_url,
            }
        except Exception as e:
            self.logger.error(f"Shadowsocks解析失败: {str(e)}")
            return None

    def _parse_shadowsocksr(self, ssr_url: str) -> Optional[Dict[str, Any]]:
        """解析ShadowsocksR节点"""
        try:
            # SSR格式: ssr://base64(info)
            encoded = ssr_url[6:]  # 移除ssr://
            missing_padding = len(encoded) % 4
            if missing_padding:
                encoded += "=" * (4 - missing_padding)

            decoded = base64.b64decode(encoded).decode("utf-8")
            parts = decoded.split("/")

            if len(parts) < 6:
                return None

            server = parts[0]
            port = int(parts[1])
            protocol = parts[2]
            method = parts[3]
            obfs = parts[4]
            password = base64.b64decode(parts[5] + "==").decode("utf-8")

            return {
                "type": "ssr",
                "host": server,
                "port": port,
                "protocol": protocol,
                "method": method,
                "obfs": obfs,
                "password": password,
                "security": "none",
                "network": "tcp",
                "path": "/",
                "host_header": "",
                "ps": "",
                "raw_url": ssr_url,
            }
        except Exception as e:
            self.logger.error(f"ShadowsocksR解析失败: {str(e)}")
            return None

    async def test_node_connectivity(self, node_info: Dict[str, Any]) -> Dict[str, Any]:
        """测试节点连接性"""
        host = node_info.get("host")
        port = node_info.get("port")

        if not host or not port:
            return {
                "connected": False,
                "error": "Invalid host or port",
                "response_time": None,
            }

        start_time = time.time()

        try:
            # 创建socket连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.connect_timeout)

            # 对于TLS连接，使用SSL包装
            if node_info.get("security") == "tls":
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=host)

            # 尝试连接
            result = sock.connect_ex((host, port))
            response_time = (time.time() - start_time) * 1000  # 毫秒

            sock.close()

            if result == 0:
                return {
                    "connected": True,
                    "response_time": response_time,
                    "error": None,
                }
            else:
                return {
                    "connected": False,
                    "response_time": response_time,
                    "error": f"Connection failed (code: {result})",
                }

        except socket.timeout:
            return {
                "connected": False,
                "response_time": self.connect_timeout * 1000,
                "error": "Connection timeout",
            }
        except Exception as e:
            return {
                "connected": False,
                "response_time": (time.time() - start_time) * 1000,
                "error": str(e),
            }

    def validate_node_format(self, node_info: Dict[str, Any]) -> Dict[str, Any]:
        """验证节点格式"""
        errors = []

        # 检查必需字段
        required_fields = ["type", "host", "port"]
        for field in required_fields:
            if not node_info.get(field):
                errors.append(f"Missing required field: {field}")

        # 检查端口范围
        port = node_info.get("port")
        if port and (port < 1 or port > 65535):
            errors.append(f"Invalid port: {port}")

        # 检查主机名格式
        host = node_info.get("host")
        if host:
            if not re.match(r"^[a-zA-Z0-9.-]+$", host):
                errors.append(f"Invalid host format: {host}")

        # 协议特定验证
        node_type = node_info.get("type")
        if node_type == "vmess":
            if not node_info.get("uuid"):
                errors.append("VMess missing UUID")
        elif node_type == "vless":
            if not node_info.get("uuid"):
                errors.append("VLESS missing UUID")
        elif node_type == "trojan":
            if not node_info.get("password"):
                errors.append("Trojan missing password")
        elif node_type == "ss":
            if not node_info.get("method") or not node_info.get("password"):
                errors.append("Shadowsocks missing method or password")

        return {"valid": len(errors) == 0, "errors": errors}

    def calculate_quality_score(
        self,
        node_info: Dict[str, Any],
        connectivity_result: Dict[str, Any],
        format_result: Dict[str, Any],
    ) -> float:
        """计算节点质量评分"""
        scores = {}

        # 连接性评分 (40%)
        if connectivity_result.get("connected"):
            response_time = connectivity_result.get("response_time", 1000)
            if response_time <= 100:
                scores["connectivity"] = 1.0
            elif response_time <= 300:
                scores["connectivity"] = 0.8
            elif response_time <= 1000:
                scores["connectivity"] = 0.6
            else:
                scores["connectivity"] = 0.4
        else:
            scores["connectivity"] = 0.0

        # 响应时间评分 (30%)
        response_time = connectivity_result.get("response_time", 1000)
        if response_time <= 50:
            scores["response_time"] = 1.0
        elif response_time <= 150:
            scores["response_time"] = 0.8
        elif response_time <= 500:
            scores["response_time"] = 0.6
        else:
            scores["response_time"] = 0.3

        # 协议支持评分 (20%)
        node_type = node_info.get("type")
        protocol_scores = {
            "vmess": 0.9,
            "vless": 0.9,
            "trojan": 0.8,
            "ss": 0.7,
            "ssr": 0.6,
        }
        scores["protocol_support"] = protocol_scores.get(node_type, 0.5)

        # 格式有效性评分 (10%)
        scores["format_valid"] = 1.0 if format_result.get("valid") else 0.0

        # 加权平均
        final_score = 0.0
        for metric, score in scores.items():
            weight = self.quality_weights.get(metric, 0.25)
            final_score += score * weight

        return min(1.0, final_score)

    async def test_single_node(self, node_url: str) -> Dict[str, Any]:
        """测试单个节点"""
        test_start = datetime.now()

        # 解析节点
        node_info = self.parse_node(node_url)
        if not node_info:
            return {
                "url": node_url,
                "success": False,
                "error": "Failed to parse node",
                "quality_score": 0.0,
                "test_time": test_start.isoformat(),
            }

        # 验证格式
        format_result = self.validate_node_format(node_info)

        # 测试连接性
        connectivity_result = await self.test_node_connectivity(node_info)

        # 计算质量评分
        quality_score = self.calculate_quality_score(
            node_info, connectivity_result, format_result
        )

        # 构建结果
        result = {
            "url": node_url,
            "success": connectivity_result.get("connected", False),
            "node_info": node_info,
            "connectivity": connectivity_result,
            "format_validation": format_result,
            "quality_score": quality_score,
            "test_time": test_start.isoformat(),
            "test_duration": (datetime.now() - test_start).total_seconds(),
        }

        return result

    async def test_nodes_batch(self, node_urls: List[str]) -> List[Dict[str, Any]]:
        """批量测试节点"""
        self.logger.info(f"开始批量测试 {len(node_urls)} 个节点")
        start_time = time.time()

        # 创建信号量限制并发
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def test_with_semaphore(node_url):
            async with semaphore:
                return await self.test_single_node(node_url)

        # 创建所有任务
        tasks = [test_with_semaphore(url) for url in node_urls]

        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"节点 {node_urls[i]} 测试异常: {str(result)}")
            else:
                valid_results.append(result)

        duration = time.time() - start_time
        success_count = sum(1 for r in valid_results if r.get("success", False))

        self.logger.info(
            f"批量测试完成: {success_count}/{len(node_urls)} 成功，耗时 {duration:.2f}s"
        )

        return valid_results

    def filter_high_quality_nodes(
        self, results: List[Dict[str, Any]], min_score: float = 0.6
    ) -> List[Dict[str, Any]]:
        """筛选高质量节点"""
        high_quality = []

        for result in results:
            if (
                result.get("success", False)
                and result.get("quality_score", 0) >= min_score
            ):
                high_quality.append(result)

        # 按质量评分排序
        high_quality.sort(key=lambda x: x.get("quality_score", 0), reverse=True)

        self.logger.info(
            f"从 {len(results)} 个节点中筛选出 {len(high_quality)} 个高质量节点"
        )

        return high_quality

    def save_results(self, results: List[Dict[str, Any]], output_file: str):
        """保存测试结果"""
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)

            self.logger.info(f"测试结果已保存到 {output_file}")

        except Exception as e:
            self.logger.error(f"保存测试结果失败: {str(e)}")

    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """生成测试报告"""
        total = len(results)
        success = sum(1 for r in results if r.get("success", False))
        failed = total - success

        if success > 0:
            avg_score = (
                sum(
                    r.get("quality_score", 0)
                    for r in results
                    if r.get("success", False)
                )
                / success
            )
            avg_response_time = (
                sum(
                    r.get("connectivity", {}).get("response_time", 0)
                    for r in results
                    if r.get("success", False)
                )
                / success
            )
        else:
            avg_score = 0
            avg_response_time = 0

        # 协议统计
        protocol_stats = {}
        for result in results:
            if result.get("success", False):
                node_type = result.get("node_info", {}).get("type", "unknown")
                protocol_stats[node_type] = protocol_stats.get(node_type, 0) + 1

        report = f"""
📊 节点测试报告
================
总节点数: {total}
成功连接: {success}
连接失败: {failed}
成功率: {(success / total * 100):.1f}%

📈 质量统计:
平均质量评分: {avg_score:.3f}
平均响应时间: {avg_response_time:.1f}ms

🔧 协议分布:
"""

        for protocol, count in sorted(
            protocol_stats.items(), key=lambda x: x[1], reverse=True
        ):
            report += f"  {protocol}: {count} 个\n"

        # 高质量节点
        high_quality = [r for r in results if r.get("quality_score", 0) >= 0.8]
        if high_quality:
            report += f"\n🏆 高质量节点 (评分≥0.8): {len(high_quality)} 个\n"
            report += "最佳节点:\n"
            for i, node in enumerate(high_quality[:5]):
                report += f"  {i + 1}. {node.get('url', 'N/A')} (评分: {node.get('quality_score', 0):.3f})\n"

        return report


# 全局测试器实例
node_tester = NodeTester()


async def test_nodes(
    node_urls: List[str], output_file: str = None, min_quality: float = 0.6
) -> List[str]:
    """测试节点并返回高质量节点URL列表"""
    results = await node_tester.test_nodes_batch(node_urls)

    # 筛选高质量节点
    high_quality_results = node_tester.filter_high_quality_nodes(results, min_quality)

    # 保存详细结果
    if output_file:
        node_tester.save_results(results, output_file.replace(".txt", "_detailed.json"))

        # 保存高质量节点
        high_quality_file = output_file.replace(".txt", "_high_quality.txt")
        with open(high_quality_file, "w", encoding="utf-8") as f:
            for result in high_quality_results:
                f.write(f"{result['url']}\n")

    # 生成报告
    report = node_tester.generate_report(results)
    print(report)

    # 返回节点URL列表
    return [r["url"] for r in high_quality_results]


if __name__ == "__main__":
    # 测试示例
    sample_nodes = [
        "vmess://eyJ2diZXIiOiAiYWRkcmVzcyIsICJwb3J0IjogNDQzLCAiaWQiOiAiYXV0byIsICJhaWQiOiAiMCIsICJzZWN1cml0eSI6ICJhdXRvIiwgIm5ldCI6ICJ3cyIsICJwYXRoIjogIi8iLCAiaG9zdCI6ICJleGFtcGxlLmNvbSIsICJwcyI6ICJUZXN0In0=",
        "vless://your-uuid@example.com:443?encryption=none&security=tls&type=ws&host=example.com#Test",
        "trojan://password@example.com:443?security=tls&type=tcp#Test",
        "ss://method:password@example.com:8388#Test",
    ]

    async def main():
        results = await test_nodes(sample_nodes, "test_results.txt")
        print(f"\n✅ 测试完成，发现 {len(results)} 个高质量节点")

    asyncio.run(main())
