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
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logger import get_logger

# 测试目标网站
TEST_SITES = [
    {'name': 'ChatGPT', 'url': 'https://chatgpt.com', 'expected_status': 200},
    {'name': 'Gemini', 'url': 'https://gemini.google.com', 'expected_status': 200},
    {'name': 'YouTube', 'url': 'https://www.youtube.com', 'expected_status': 200},
    {'name': 'X.com', 'url': 'https://x.com', 'expected_status': 200},
    {'name': 'Reddit', 'url': 'https://www.reddit.com', 'expected_status': 200},
]

# 测试配置
TIMEOUT = 10  # 每个请求的超时时间（秒）
MAX_WORKERS = 50  # 最大并发数（提高并发数以加快测速速度）
MIN_SUCCESS_SITES = 5  # 至少需要成功访问的网站数量（所有网站都要能访问）

class NodeTester:
    """节点测速器"""
    
    def __init__(self):
        self.logger = get_logger("node_tester")
        
    def extract_host_port(self, node):
        """从节点中提取主机和端口"""
        try:
            if node.startswith('vmess://'):
                import base64
                import json
                data = node[8:]
                data += '=' * (-len(data) % 4)
                decoded = base64.b64decode(data).decode('utf-8')
                config = json.loads(decoded)
                return config.get('add'), config.get('port')
            elif node.startswith('vless://') or node.startswith('trojan://'):
                parsed = urlparse(node)
                return parsed.hostname, parsed.port
            elif node.startswith('ss://'):
                parsed = urlparse(node)
                if parsed.hostname and parsed.port:
                    return parsed.hostname, parsed.port
                # 尝试 base64 解码
                try:
                    import base64
                    data = node[5:]
                    data += '=' * (-len(data) % 4)
                    decoded = base64.b64decode(data).decode('utf-8')
                    if '@' in decoded:
                        _, server_part = decoded.rsplit('@', 1)
                        if ':' in server_part:
                            host, port_str = server_part.rsplit(':', 1)
                            return host, int(port_str)
                except:
                    pass
            return None, None
        except Exception as e:
            self.logger.error(f"提取主机端口失败: {str(e)}")
            return None, None
    
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
    
    def test_node(self, node):
        """测试单个节点能否访问目标网站"""
        try:
            # 提取主机和端口
            host, port = self.extract_host_port(node)
            if not host or not port:
                return False, 0, []
            
            # 先测试TCP连接
            if not self.test_tcp_connectivity(host, port):
                return False, 0, []
            
            # 测试目标网站
            success_sites = []
            
            for site in TEST_SITES:
                try:
                    # 使用代理请求
                    proxies = {
                        'http': f'http://{host}:{port}',
                        'https': f'http://{host}:{port}',
                    }
                    
                    response = requests.get(
                        site['url'],
                        proxies=proxies,
                        timeout=TIMEOUT,
                        allow_redirects=True,
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        }
                    )
                    
                    if response.status_code == site['expected_status']:
                        success_sites.append(site['name'])
                        self.logger.debug(f"✓ {site['name']} 访问成功")
                    else:
                        self.logger.debug(f"✗ {site['name']} 访问失败: {response.status_code}")
                        
                except RequestException as e:
                    self.logger.debug(f"✗ {site['name']} 访问异常: {str(e)}")
                except Exception as e:
                    self.logger.debug(f"✗ {site['name']} 测试异常: {str(e)}")
            
            # 判断是否通过测试
            is_valid = len(success_sites) >= MIN_SUCCESS_SITES
            
            return is_valid, len(success_sites), success_sites
            
        except Exception as e:
            self.logger.error(f"测试节点失败: {str(e)}")
            return False, 0, []
    
    def test_all_nodes(self, nodes):
        """批量测试所有节点"""
        if not nodes:
            self.logger.warning("没有节点需要测试")
            return []
        
        self.logger.info(f"开始测试 {len(nodes)} 个节点...")
        self.logger.info(f"测试目标: {', '.join([site['name'] for site in TEST_SITES])}")
        self.logger.info(f"通过标准: 至少成功访问 {MIN_SUCCESS_SITES} 个网站")
        
        valid_nodes = []
        test_results = []
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # 提交所有任务
            future_to_node = {
                executor.submit(self.test_node, node): node 
                for node in nodes
            }
            
            # 处理完成的任务
            for i, future in enumerate(concurrent.futures.as_completed(future_to_node)):
                node = future_to_node[future]
                
                try:
                    is_valid, success_count, success_sites = future.result()
                    
                    if is_valid:
                        valid_nodes.append(node)
                        self.logger.info(f"✓ 节点有效 ({len(valid_nodes)}): 成功访问 {success_count} 个网站 - {', '.join(success_sites)}")
                    else:
                        self.logger.debug(f"✗ 节点无效: 成功访问 {success_count} 个网站")
                    
                    test_results.append({
                        'node': node[:50] + '...',
                        'is_valid': is_valid,
                        'success_count': success_count,
                        'success_sites': success_sites
                    })
                    
                except Exception as e:
                    self.logger.error(f"✗ 测试节点失败: {node[:50]}... - {str(e)}")
                
                # 显示进度
                if (i + 1) % 10 == 0 or (i + 1) == len(nodes):
                    progress = (i + 1) / len(nodes) * 100
                    self.logger.info(f"测试进度: {i + 1}/{len(nodes)} ({progress:.1f}%)")
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.logger.info("=" * 50)
        self.logger.info("测试完成！")
        self.logger.info(f"总节点数: {len(nodes)}")
        self.logger.info(f"有效节点: {len(valid_nodes)}")
        self.logger.info(f"无效节点: {len(nodes) - len(valid_nodes)}")
        self.logger.info(f"成功率: {len(valid_nodes)/len(nodes)*100:.1f}%")
        self.logger.info(f"测试耗时: {duration:.2f}秒")
        self.logger.info("=" * 50)
        
        return valid_nodes

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="节点测速脚本")
    parser.add_argument("--input", default="result/nodetotal.txt", help="输入节点文件")
    parser.add_argument("--output", default="result/nodelist.txt", help="输出节点文件")
    parser.add_argument("--min-sites", type=int, default=MIN_SUCCESS_SITES, help="至少需要成功访问的网站数量")
    
    args = parser.parse_args()
    
    # 更新全局配置
    global MIN_SUCCESS_SITES
    MIN_SUCCESS_SITES = args.min_sites
    
    logger = get_logger("main")
    
    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        logger.error(f"输入文件不存在: {args.input}")
        sys.exit(1)
    
    # 读取节点
    logger.info(f"读取节点文件: {args.input}")
    with open(args.input, 'r', encoding='utf-8') as f:
        nodes = [line.strip() for line in f if line.strip()]
    
    logger.info(f"读取到 {len(nodes)} 个节点")
    
    # 测试节点
    tester = NodeTester()
    valid_nodes = tester.test_all_nodes(nodes)
    
    # 保存结果
    if valid_nodes:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            for node in valid_nodes:
                f.write(f"{node}\n")
        logger.info(f"有效节点已保存到: {args.output}")
    else:
        logger.warning("没有有效的节点，不生成输出文件")
    
    logger.info("✓ 测试完成")
    sys.exit(0)

if __name__ == "__main__":
    main()