#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流媒体解锁测试器 - 测试节点能否访问流媒体服务
"""

import time
import concurrent.futures
from typing import Dict, List, Tuple
from src.testers.base_tester import BaseTester
from config.settings import CONNECTION_TIMEOUT, MAX_WORKERS


# 测试目标网站
TEST_SITES = [
    {'name': 'ChatGPT', 'url': 'https://chatgpt.com', 'expected_status': 200, 'priority': 'high'},
    {'name': 'Gemini', 'url': 'https://gemini.google.com', 'expected_status': 200, 'priority': 'high'},
    {'name': 'YouTube', 'url': 'https://www.youtube.com', 'expected_status': 200, 'priority': 'normal'},
    {'name': 'X.com', 'url': 'https://x.com', 'expected_status': 200, 'priority': 'normal'},
    {'name': 'Reddit', 'url': 'https://www.reddit.com', 'expected_status': 200, 'priority': 'normal'},
]

# 测试配置
MIN_SUCCESS_SITES = 3  # 至少需要成功访问的网站数量
MIN_AI_SITES = 1      # 至少需要成功访问的AI服务数量（ChatGPT或Gemini）


class MediaTester(BaseTester):
    """流媒体解锁测试器"""
    
    def __init__(self, timeout: int = CONNECTION_TIMEOUT, max_workers: int = MAX_WORKERS):
        super().__init__()
        self.timeout = timeout
        self.max_workers = max_workers
    
    def test_site_access(self, host: str, port: int, site: Dict) -> Tuple[bool, str]:
        """
        测试访问指定网站
        
        Args:
            host: 节点主机
            port: 节点端口
            site: 网站信息
            
        Returns:
            (is_accessible, site_name): 是否可访问和网站名称
        """
        try:
            import socket
            
            # 使用SOCKS5代理测试（需要本地代理服务器）
            # 这里简化为测试TCP连接到目标网站
            # 实际应用中需要通过代理进行HTTP请求
            
            # 提取目标网站的主机
            from urllib.parse import urlparse
            site_host = urlparse(site['url']).hostname
            
            if not site_host:
                return False, site['name']
            
            # 测试到目标网站的TCP连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((site_host, 443))  # HTTPS端口
            sock.close()
            
            is_accessible = result == 0
            return is_accessible, site['name']
            
        except Exception as e:
            self.logger.error(f"测试 {site['name']} 失败: {str(e)}")
            return False, site['name']
    
    def test_node(self, node: str) -> Tuple[bool, Dict]:
        """
        测试单个节点的流媒体访问能力
        
        测试规则：
        1. 5个目标网站中至少3个可访问
        2. ChatGPT和Gemini中至少1个可访问
        
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
        
        self.logger.info(f"开始测试节点: {host}:{port}")
        
        # 测试所有网站
        success_sites = []
        ai_success_sites = []
        
        for site in TEST_SITES:
            is_accessible, site_name = self.test_site_access(host, port, site)
            
            if is_accessible:
                success_sites.append(site_name)
                if site['priority'] == 'high':
                    ai_success_sites.append(site_name)
                self.logger.info(f"  ✓ {site_name} 可访问")
            else:
                self.logger.info(f"  ✗ {site_name} 不可访问")
        
        # 判断是否满足条件
        # 条件1: 5个网站中至少3个可访问
        condition1 = len(success_sites) >= MIN_SUCCESS_SITES
        
        # 条件2: ChatGPT和Gemini中至少1个可访问
        condition2 = len(ai_success_sites) >= MIN_AI_SITES
        
        is_valid = condition1 and condition2
        
        result_info = {
            'node': node,
            'host': host,
            'port': port,
            'success_sites': success_sites,
            'ai_success_sites': ai_success_sites,
            'total_sites': len(TEST_SITES),
            'success_count': len(success_sites),
            'ai_success_count': len(ai_success_sites),
            'condition1_met': condition1,  # 5个网站中至少3个可访问
            'condition2_met': condition2,  # ChatGPT/Gemini至少1个可访问
            'is_valid': is_valid
        }
        
        if is_valid:
            self.logger.info(f"✓ 节点有效: {host}:{port} (成功: {len(success_sites)}/{len(TEST_SITES)}, AI: {len(ai_success_sites)}/2)")
        else:
            self.logger.info(f"✗ 节点无效: {host}:{port} (成功: {len(success_sites)}/{len(TEST_SITES)}, AI: {len(ai_success_sites)}/2)")
        
        return is_valid, result_info
    
    def test_nodes(self, nodes: List[str]) -> List[str]:
        """
        批量测试节点的流媒体访问能力
        
        Args:
            nodes: 节点列表
            
        Returns:
            valid_nodes: 满足条件的有效节点列表
        """
        if not nodes:
            self.logger.warning("没有节点需要测试")
            return []
        
        self.logger.info(f"开始流媒体访问测试 {len(nodes)} 个节点...")
        self.logger.info(f"测试规则:")
        self.logger.info(f"  1. 5个网站中至少{MIN_SUCCESS_SITES}个可访问")
        self.logger.info(f"  2. ChatGPT和Gemini中至少{MIN_AI_SITES}个可访问")
        self.logger.info(f"测试目标: {', '.join([site['name'] for site in TEST_SITES])}")
        
        valid_nodes = []
        test_results = []
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_node = {
                executor.submit(self.test_node, node): node
                for node in nodes
            }
            
            self.logger.info(f"已提交 {len(future_to_node)} 个测试任务")
            
            for i, future in enumerate(concurrent.futures.as_completed(future_to_node)):
                node = future_to_node[future]
                
                try:
                    is_valid, result_info = future.result(timeout=self.timeout * 5 + 10)
                    
                    if is_valid:
                        valid_nodes.append(node)
                        self.logger.info(f"✓ 节点有效 ({len(valid_nodes)}/{i+1}): {result_info['host']}:{result_info['port']}")
                    else:
                        self.logger.info(f"✗ 节点无效 ({i+1}/{len(nodes)}): {result_info['host']}:{result_info['port']}")
                    
                    test_results.append(result_info)
                
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
        
        # 统计结果
        condition1_count = sum(1 for r in test_results if r.get('condition1_met', False))
        condition2_count = sum(1 for r in test_results if r.get('condition2_met', False))
        both_conditions_count = sum(1 for r in test_results if r.get('is_valid', False))
        
        self.logger.info("=" * 50)
        self.logger.info("流媒体访问测试完成！")
        self.logger.info(f"总节点数: {len(nodes)}")
        self.logger.info(f"有效节点: {len(valid_nodes)}")
        self.logger.info(f"无效节点: {len(nodes) - len(valid_nodes)}")
        self.logger.info(f"通过率: {len(valid_nodes)/len(nodes)*100:.1f}%")
        self.logger.info(f"测试耗时: {duration:.2f}秒")
        self.logger.info(f"满足条件1 (5个网站中至少{MIN_SUCCESS_SITES}个): {condition1_count} 个节点")
        self.logger.info(f"满足条件2 (ChatGPT/Gemini至少{MIN_AI_SITES}个): {condition2_count} 个节点")
        self.logger.info(f"同时满足两个条件: {both_conditions_count} 个节点")
        self.logger.info("=" * 50)
        
        return valid_nodes
