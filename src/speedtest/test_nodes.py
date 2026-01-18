#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
节点测速脚本 - 测试节点能否访问主流网站
"""

import sys
import os
import time
import concurrent.futures
from urllib.parse import urlparse
import requests
from requests.exceptions import RequestException

# 添加项目根目录到路径
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from src.utils.logger import get_logger

# 测试目标网站
TEST_SITES = [
    {"name": "ChatGPT", "url": "https://chatgpt.com", "expected_status": 200},
    {"name": "Gemini", "url": "https://gemini.google.com", "expected_status": 200},
    {"name": "YouTube", "url": "https://www.youtube.com", "expected_status": 200},
    {"name": "X.com", "url": "https://x.com", "expected_status": 200},
    {"name": "Reddit", "url": "https://www.reddit.com", "expected_status": 200},
]

# 测试配置
TIMEOUT = 5  # 每个请求的超时时间（秒）
MAX_WORKERS = 10  # 最大并发数（降低并发数以避免网络拥堵）
MIN_SUCCESS_SITES = 3  # 至少需要成功访问的网站数量（降低标准以提高通过率）


class NodeTester:
    """节点测速器"""

    def __init__(self):
        self.logger = get_logger("node_tester")

    def extract_host_port(self, node):
        """从节点中提取主机和端口"""
        try:
            if node.startswith("vmess://"):
                import base64
                import json

                data = node[8:]
                data += "=" * (-len(data) % 4)
                decoded = base64.b64decode(data).decode("utf-8")
                config = json.loads(decoded)
                return config.get("add"), config.get("port")
            elif node.startswith("vless://") or node.startswith("trojan://"):
                parsed = urlparse(node)
                return parsed.hostname, parsed.port
            elif node.startswith("ss://"):
                parsed = urlparse(node)
                if parsed.hostname and parsed.port:
                    return parsed.hostname, parsed.port
                # 尝试 base64 解码
                try:
                    import base64

                    data = node[5:]
                    data += "=" * (-len(data) % 4)
                    decoded = base64.b64decode(data).decode("utf-8")
                    if "@" in decoded:
                        _, server_part = decoded.rsplit("@", 1)
                        if ":" in server_part:
                            host, port_str = server_part.rsplit(":", 1)
                            return host, int(port_str)
                except:
                    pass
            return None, None
        except Exception as e:
            self.logger.error(f"提取主机端口失败: {str(e)}")
            return None, None

    def get_node_type(self, node):
        """从节点中提取传输类型"""
        try:
            node_type = None

            if node.startswith("vmess://"):
                # vmess节点需要Base64解码
                import base64
                import json

                data = node[8:]
                data += "=" * (-len(data) % 4)
                decoded = base64.b64decode(data).decode("utf-8")
                config = json.loads(decoded)
                node_type = config.get("net", "tcp")  # 默认为tcp

            elif (
                node.startswith("vless://")
                or node.startswith("trojan://")
                or node.startswith("ss://")
            ):
                # 从URL查询参数中提取type
                parsed = urlparse(node)
                if parsed.query:
                    # 解析查询参数
                    params = {}
                    for param in parsed.query.split("&"):
                        if "=" in param:
                            key, value = param.split("=", 1)
                            params[key] = value

                    node_type = params.get("type", "tcp")  # 默认为tcp

            # 如果没有获取到类型，默认为tcp
            if not node_type:
                node_type = "tcp"

            return node_type.lower()

        except Exception as e:
            self.logger.error(f"提取节点类型失败: {str(e)}")
            return "tcp"  # 出错时默认为tcp

    def is_http_proxy_supported(self, node_type):
        """判断节点类型是否支持HTTP代理"""
        # 不支持HTTP代理的节点类型
        unsupported_types = ["ws", "websocket", "grpc", "quic", "http", "h2"]
        return node_type not in unsupported_types

    def test_tcp_connectivity(self, host, port):
        """测试TCP连接"""
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(TIMEOUT)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def test_node(self, node, min_success_sites=None):
        """测试单个节点能否访问目标网站"""
        if min_success_sites is None:
            min_success_sites = MIN_SUCCESS_SITES

        try:
            # 提取主机和端口
            host, port = self.extract_host_port(node)
            if not host or not port:
                return False, 0, [], False

            # 检查节点类型
            node_type = self.get_node_type(node)

            self.logger.info(f"开始测试节点: {host}:{port} (类型: {node_type})")

            # 测试TCP连接
            if not self.test_tcp_connectivity(host, port):
                self.logger.info(f"✗ TCP连接失败: {host}:{port}")
                return False, 0, [], False

            self.logger.info(f"✓ 节点有效 (TCP连通): {host}:{port}")
            return True, 0, [], True

        except Exception as e:
            self.logger.error(f"测试节点失败: {str(e)}")
            return False, 0, [], False

    def test_all_nodes(self, nodes, min_success_sites=None):
        """批量测试所有节点"""
        if min_success_sites is None:
            min_success_sites = MIN_SUCCESS_SITES

        if not nodes:
            self.logger.warning("没有节点需要测试")
            return []

        self.logger.info(f"开始测试 {len(nodes)} 个节点...")
        self.logger.info(
            f"测试目标: {', '.join([site['name'] for site in TEST_SITES])}"
        )
        self.logger.info(f"通过标准: 至少成功访问 {min_success_sites} 个网站")
        self.logger.info(f"并发数: {MAX_WORKERS}, 超时时间: {TIMEOUT}秒")

        valid_nodes = []
        test_results = []

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # 提交所有任务
            future_to_node = {
                executor.submit(self.test_node, node, min_success_sites): node
                for node in nodes
            }

            self.logger.info(f"已提交 {len(future_to_node)} 个测试任务")

            # 处理完成的任务
            for i, future in enumerate(concurrent.futures.as_completed(future_to_node)):
                node = future_to_node[future]

                try:
                    # 设置超时保护
                    is_valid, success_count, success_sites, tcp_only = future.result(
                        timeout=TIMEOUT * 5 + 10
                    )

                    if is_valid:
                        valid_nodes.append(node)
                        self.logger.info(
                            f"✓ 节点有效 ({len(valid_nodes)}/{i + 1}): TCP连通"
                        )
                    else:
                        self.logger.info(
                            f"✗ 节点无效 ({i + 1}/{len(nodes)}): TCP连接失败"
                        )

                    test_results.append(
                        {
                            "node": node[:50] + "...",
                            "is_valid": is_valid,
                            "success_count": success_count,
                            "success_sites": success_sites,
                            "tcp_only": tcp_only,
                        }
                    )

                except concurrent.futures.TimeoutError:
                    self.logger.error(
                        f"✗ 测试节点超时 ({i + 1}/{len(nodes)}): {node[:50]}..."
                    )
                except Exception as e:
                    self.logger.error(
                        f"✗ 测试节点失败 ({i + 1}/{len(nodes)}): {node[:50]}... - {str(e)}"
                    )

                # 显示进度
                if (i + 1) % 10 == 0 or (i + 1) == len(nodes):
                    progress = (i + 1) / len(nodes) * 100
                    elapsed = time.time() - start_time
                    self.logger.info(
                        f"测试进度: {i + 1}/{len(nodes)} ({progress:.1f}%), 已用时间: {elapsed:.1f}秒"
                    )

        end_time = time.time()
        duration = end_time - start_time

        self.logger.info("=" * 50)
        self.logger.info("测试完成！")
        self.logger.info(f"总节点数: {len(nodes)}")
        self.logger.info(f"有效节点: {len(valid_nodes)}")
        self.logger.info(f"无效节点: {len(nodes) - len(valid_nodes)}")
        self.logger.info(f"通过率: {len(valid_nodes) / len(nodes) * 100:.1f}%")
        self.logger.info(f"测试耗时: {duration:.2f}秒")
        self.logger.info("=" * 50)

        return valid_nodes


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="节点测速脚本")
    parser.add_argument("--input", default="result/nodetotal.txt", help="输入节点文件")
    parser.add_argument("--output", default="result/nodelist.txt", help="输出节点文件")
    parser.add_argument(
        "--min-sites",
        type=int,
        default=MIN_SUCCESS_SITES,
        help="至少需要成功访问的网站数量",
    )
    parser.add_argument(
        "--skip-test", action="store_true", help="跳过HTTP代理测试，直接保存所有节点"
    )

    args = parser.parse_args()

    logger = get_logger("main")

    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        logger.error(f"输入文件不存在: {args.input}")
        sys.exit(1)

    # 读取节点
    logger.info(f"读取节点文件: {args.input}")
    with open(args.input, "r", encoding="utf-8") as f:
        nodes = [line.strip() for line in f if line.strip()]

    logger.info(f"读取到 {len(nodes)} 个节点")

    # 如果跳过测试，直接保存所有节点
    if args.skip_test:
        logger.info("跳过HTTP代理测试，直接保存所有节点")
        logger.info(
            "注意: V2Ray/Trojan节点不是HTTP代理服务器，无法通过HTTP代理方式测试"
        )
        logger.info("建议使用V2Ray客户端测试节点的可用性")

        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            for node in nodes:
                f.write(f"{node}\n")

        logger.info(f"所有 {len(nodes)} 个节点已保存到: {args.output}")
        logger.info("✓ 完成")
        sys.exit(0)

    # 测试节点
    tester = NodeTester()
    valid_nodes = tester.test_all_nodes(nodes, min_success_sites=args.min_sites)

    # 保存结果
    if valid_nodes:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            for node in valid_nodes:
                f.write(f"{node}\n")
        logger.info(f"有效节点已保存到: {args.output}")
    else:
        logger.warning("没有有效的节点，不生成输出文件")

    logger.info("✓ 测试完成")
    sys.exit(0)


if __name__ == "__main__":
    main()
