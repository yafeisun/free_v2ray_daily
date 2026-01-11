#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TCP连通性测试器 - 测试节点的TCP连接能力
"""

import socket
import time
import concurrent.futures
from typing import Dict, List, Tuple
from src.testers.base_tester import BaseTester
from config.settings import CONNECTION_TIMEOUT, MAX_WORKERS


class TCPTester(BaseTester):
    """TCP连通性测试器"""
    
    def __init__(self, timeout: int = CONNECTION_TIMEOUT, max_workers: int = MAX_WORKERS):
        super().__init__()
        self.timeout = timeout
        self.max_workers = max_workers
    
    def test_tcp_connectivity(self, host: str, port: int) -> bool:
        """
        测试TCP连接
        
        Args:
            host: 主机地址
            port: 端口号
            
        Returns:
            is_connected: 是否连接成功
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def test_node(self, node: str) -> Tuple[bool, Dict]:
        """
        测试单个节点的TCP连通性
        
        Args:
            node: 节点字符串
            
        Returns:
            (is_valid, result_info): 是否有效和结果信息
        """
        host, port = self.extract_host_port(node)
        
        if not host or not port:
            return False, {
                'node': node,
                'host': host,
                'port': port,
                'error': '无法提取主机和端口'
            }
        
        is_connected = self.test_tcp_connectivity(host, port)
        
        return is_connected, {
            'node': node,
            'host': host,
            'port': port,
            'is_connected': is_connected
        }
    
    def test_nodes(self, nodes: List[str]) -> List[str]:
        """
        批量测试节点的TCP连通性
        
        Args:
            nodes: 节点列表
            
        Returns:
            valid_nodes: TCP连通的节点列表
        """
        if not nodes:
            self.logger.warning("没有节点需要测试")
            return []
        
        self.logger.info(f"开始TCP连通性测试 {len(nodes)} 个节点...")
        
        valid_nodes = []
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_node = {
                executor.submit(self.test_node, node): node
                for node in nodes
            }
            
            for i, future in enumerate(concurrent.futures.as_completed(future_to_node)):
                node = future_to_node[future]
                
                try:
                    is_valid, result_info = future.result(timeout=self.timeout * 2 + 10)
                    
                    if is_valid:
                        valid_nodes.append(node)
                        self.logger.info(f"✓ TCP连通 ({len(valid_nodes)}/{i+1}): {result_info['host']}:{result_info['port']}")
                    else:
                        self.logger.info(f"✗ TCP不通 ({i+1}/{len(nodes)}): {result_info.get('host', 'N/A')}:{result_info.get('port', 'N/A')}")
                
                except concurrent.futures.TimeoutError:
                    self.logger.error(f"✗ 测试超时 ({i+1}/{len(nodes)}): {node[:50]}...")
                except Exception as e:
                    self.logger.error(f"✗ 测试失败 ({i+1}/{len(nodes)}): {node[:50]}... - {str(e)}")
                
                # 显示进度
                if (i + 1) % 10 == 0 or (i + 1) == len(nodes):
                    progress = (i + 1) / len(nodes) * 100
                    elapsed = time.time() - start_time
                    self.logger.info(f"测试进度: {i + 1}/{len(nodes)} ({progress:.1f}%), 已用时间: {elapsed:.1f}秒")
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.logger.info("=" * 50)
        self.logger.info("TCP连通性测试完成！")
        self.logger.info(f"总节点数: {len(nodes)}")
        self.logger.info(f"有效节点: {len(valid_nodes)}")
        self.logger.info(f"无效节点: {len(nodes) - len(valid_nodes)}")
        self.logger.info(f"通过率: {len(valid_nodes)/len(nodes)*100:.1f}%")
        self.logger.info(f"测试耗时: {duration:.2f}秒")
        self.logger.info("=" * 50)
        
        return valid_nodes
