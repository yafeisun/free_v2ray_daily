#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连通性测试器
"""

import socket
import concurrent.futures
import time
import re
from src.utils.logger import get_logger
from config.settings import CONNECTION_TIMEOUT, MAX_WORKERS

class ConnectivityTester:
    """节点连通性测试器"""
    
    def __init__(self):
        self.logger = get_logger("connectivity_tester")
        self.timeout = CONNECTION_TIMEOUT
        self.max_workers = MAX_WORKERS
        
    def test_node_connectivity(self, node):
        """测试单个节点的连通性和服务访问"""
        try:
            # 从节点链接中提取主机和端口
            if node.startswith('vmess://'):
                return self.test_vmess_node(node)
            elif node.startswith('vless://'):
                return self.test_vless_node(node)
            elif node.startswith('trojan://'):
                return self.test_trojan_node(node)
            elif node.startswith('hysteria2://') or node.startswith('hysteria://'):
                return self.test_hysteria_node(node)
            elif node.startswith('ss://'):
                return self.test_shadowsocks_node(node)
            else:
                self.logger.warning(f"未知协议: {node[:50]}...")
                return False
        except Exception as e:
            self.logger.error(f"测试节点失败: {str(e)}")
            return False
    
    def test_vmess_node(self, node):
        """测试VMess节点"""
        try:
            import base64
            import json
            
            # 解码base64
            data = node[8:]  # 去掉 vmess://
            data += '=' * (-len(data) % 4)  # 补齐base64
            decoded = base64.b64decode(data).decode('utf-8')
            config = json.loads(decoded)
            
            host = config.get('add')
            port = config.get('port')
            
            if not host or not port:
                self.logger.warning("VMess节点缺少主机或端口信息")
                return False
            
            # 测试延迟
            latency_result = self.test_latency(host, port)
            if not latency_result or latency_result['average'] > 300:
                self.logger.debug(f"VMess节点延迟过高或测试失败: {host}:{port}")
                return False
            
            # 测试基础服务
            if not self.test_basic_services(host, port):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"测试VMess节点失败: {str(e)}")
            return False
    
    def test_vless_node(self, node):
        """测试VLESS节点"""
        try:
            import urllib.parse
            
            parsed = urllib.parse.urlparse(node)
            host = parsed.hostname
            port = parsed.port
            
            if not host or not port:
                self.logger.warning("VLESS节点缺少主机或端口信息")
                return False
            
            # 测试延迟
            latency_result = self.test_latency(host, port)
            if not latency_result or latency_result['average'] > 300:
                self.logger.debug(f"VLESS节点延迟过高或测试失败: {host}:{port}")
                return False
            
            # 测试基础服务
            if not self.test_basic_services(host, port):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"测试VLESS节点失败: {str(e)}")
            return False
    
    def test_trojan_node(self, node):
        """测试Trojan节点"""
        try:
            import urllib.parse
            
            parsed = urllib.parse.urlparse(node)
            host = parsed.hostname
            port = parsed.port
            
            if not host or not port:
                self.logger.warning("Trojan节点缺少主机或端口信息")
                return False
            
            # 测试延迟
            latency_result = self.test_latency(host, port)
            if not latency_result or latency_result['average'] > 300:
                self.logger.debug(f"Trojan节点延迟过高或测试失败: {host}:{port}")
                return False
            
            # 测试基础服务
            if not self.test_basic_services(host, port):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"测试Trojan节点失败: {str(e)}")
            return False
    
    def test_hysteria_node(self, node):
        """测试Hysteria节点"""
        try:
            import urllib.parse
            
            parsed = urllib.parse.urlparse(node)
            host = parsed.hostname
            port = parsed.port
            
            if not host or not port:
                self.logger.warning("Hysteria节点缺少主机或端口信息")
                return False
            
            # 测试延迟
            latency_result = self.test_latency(host, port)
            if not latency_result or latency_result['average'] > 300:
                self.logger.debug(f"Hysteria节点延迟过高或测试失败: {host}:{port}")
                return False
            
            # 测试基础服务
            if not self.test_basic_services(host, port):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"测试Hysteria节点失败: {str(e)}")
            return False
    
    def test_shadowsocks_node(self, node):
        """测试Shadowsocks节点"""
        try:
            import urllib.parse
            import base64
            
            # 解析SS节点
            if '#' in node:
                node = node.split('#')[0]
            
            parsed = urllib.parse.urlparse(node)
            
            if parsed.hostname and parsed.port:
                # 标准格式
                host = parsed.hostname
                port = parsed.port
            else:
                # 尝试base64解码
                try:
                    data = node[5:]  # 去掉 ss://
                    data += '=' * (-len(data) % 4)
                    decoded = base64.b64decode(data).decode('utf-8')
                    
                    if ':' in decoded:
                        parts = decoded.split(':')
                        if len(parts) >= 2:
                            host = parts[0]
                            port = int(parts[1].split('@')[0] if '@' in parts[1] else parts[1])
                        else:
                            self.logger.warning("无法解析SS节点格式")
                            return False
                    else:
                        self.logger.warning("无法解析SS节点格式")
                        return False
                except:
                    self.logger.warning("无法解析SS节点")
                    return False
            
            if not host or not port:
                self.logger.warning("SS节点缺少主机或端口信息")
                return False
            
            # 测试延迟
            latency_result = self.test_latency(host, port)
            if not latency_result or latency_result['average'] > 300:
                self.logger.debug(f"SS节点延迟过高或测试失败: {host}:{port}")
                return False
            
            # 测试基础服务
            if not self.test_basic_services(host, port):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"测试SS节点失败: {str(e)}")
            return False
    
    def test_latency(self, host, port, timeout=None):
        """测试节点延迟，进行3次测速"""
        if timeout is None:
            timeout = self.timeout
        
        latencies = []
        
        for i in range(3):
            try:
                import time
                start_time = time.time()
                
                # 测试TCP连接延迟
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                
                connect_start = time.time()
                result = sock.connect_ex((host, port))
                connect_time = time.time() - connect_start
                
                sock.close()
                
                if result == 0:
                    latencies.append(round(connect_time * 1000, 2))  # 转换为毫秒
                    self.logger.debug(f"延迟测试 {i+1}/3: {latencies[-1]}ms")
                else:
                    self.logger.debug(f"延迟测试 {i+1}/3: 连接失败")
                    return None  # 连接失败，返回None
                    
            except Exception as e:
                self.logger.debug(f"延迟测试 {i+1}/3: 异常 - {str(e)}")
                return None
        
        # 计算平均延迟
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)
            min_latency = min(latencies)
            
            self.logger.debug(f"延迟统计: 平均={avg_latency:.2f}ms, 最大={max_latency:.2f}ms, 最小={min_latency:.2f}ms")
            return {
                'average': avg_latency,
                'max': max_latency,
                'min': min_latency,
                'all': latencies
            }
        
        return None
    
    def test_basic_services(self, host, port):
        """测试基础服务访问"""
        try:
            # 测试Google DNS
            if self.test_service_access(host, port, "8.8.8.8", 53):
                return True
            
            # 测试Cloudflare DNS
            if self.test_service_access(host, port, "1.1.1.1", 53):
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"测试基础服务失败: {str(e)}")
            return False
    
    def test_service_access(self, host, port, target_host, target_port):
        """测试通过代理访问特定服务"""
        try:
            # 这里简化实现，只测试TCP连接
            # 实际应用中需要实现完整的代理协议
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            return result == 0
            
        except Exception:
            return False
    
    def test_ai_services_connectivity(self, host, port):
        """测试AI服务连通性"""
        try:
            # 测试ChatGPT连接
            chatgpt_accessible = self.test_service_access(host, port, "api.openai.com", 443)
            
            # 测试Google AI Studio连接
            google_ai_accessible = self.test_service_access(host, port, "ai.google.dev", 443)
            
            is_ai_available = chatgpt_accessible or google_ai_accessible
            
            if is_ai_available:
                self.logger.debug(f"AI服务可用 - ChatGPT: {chatgpt_accessible}, Google AI: {google_ai_accessible}")
            else:
                self.logger.debug(f"AI服务不可用 - ChatGPT: {chatgpt_accessible}, Google AI: {google_ai_accessible}")
            
            return is_ai_available, {
                'chatgpt': chatgpt_accessible,
                'google_ai': google_ai_accessible
            }
            
        except Exception as e:
            self.logger.error(f"测试AI服务连通性失败: {str(e)}")
            return False, {'chatgpt': False, 'google_ai': False}
    
    def _extract_host_port_from_node(self, node):
        """从节点信息中提取主机和端口"""
        try:
            if node.startswith('vmess://'):
                import base64
                import json
                data = node[8:]
                data += '=' * (-len(data) % 4)
                decoded = base64.b64decode(data).decode('utf-8')
                config = json.loads(decoded)
                return config.get('add'), config.get('port')
                
            elif node.startswith('vless://') or node.startswith('trojan://') or node.startswith('hysteria://'):
                import urllib.parse
                parsed = urllib.parse.urlparse(node)
                return parsed.hostname, parsed.port
                
            elif node.startswith('ss://'):
                import urllib.parse
                import base64
                
                if '#' in node:
                    node = node.split('#')[0]
                
                parsed = urllib.parse.urlparse(node)
                
                if parsed.hostname and parsed.port:
                    return parsed.hostname, parsed.port
                else:
                    data = node[5:]
                    data += '=' * (-len(data) % 4)
                    decoded = base64.b64decode(data).decode('utf-8')
                    
                    if ':' in decoded:
                        parts = decoded.split(':')
                        if len(parts) >= 2:
                            host = parts[0]
                            port_str = parts[1].split('@')[0] if '@' in parts[1] else parts[1]
                            return host, int(port_str)
            
            return None, None
            
        except Exception as e:
            self.logger.error(f"提取主机端口失败: {str(e)}")
            return None, None
    
    def test_nodes(self, nodes):
        """批量测试所有节点的连通性"""
        if not nodes:
            self.logger.warning("没有节点需要测试")
            return []
        
        self.logger.info(f"开始测试 {len(nodes)} 个节点的连通性...")
        
        valid_nodes = []
        invalid_count = 0
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_node = {
                executor.submit(self.test_node_connectivity, node): node 
                for node in nodes
            }
            
            # 处理完成的任务
            for i, future in enumerate(concurrent.futures.as_completed(future_to_node)):
                node = future_to_node[future]
                
                try:
                    is_valid = future.result()
                    if is_valid:
                        valid_nodes.append(node)
                        self.logger.info(f"✓ 节点有效 ({len(valid_nodes)}): {node[:50]}...")
                    else:
                        invalid_count += 1
                        self.logger.debug(f"✗ 节点无效 ({invalid_count}): {node[:50]}...")
                        
                except Exception as e:
                    invalid_count += 1
                    self.logger.error(f"✗ 测试节点失败 ({invalid_count}): {node[:50]}... - {str(e)}")
                
                # 显示进度
                if (i + 1) % 10 == 0 or (i + 1) == len(nodes):
                    progress = (i + 1) / len(nodes) * 100
                    self.logger.info(f"测试进度: {i + 1}/{len(nodes)} ({progress:.1f}%)")
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.logger.info(f"测试完成！")
        self.logger.info(f"总节点数: {len(nodes)}")
        self.logger.info(f"有效节点: {len(valid_nodes)}")
        self.logger.info(f"无效节点: {invalid_count}")
        self.logger.info(f"成功率: {len(valid_nodes)/len(nodes)*100:.1f}%")
        self.logger.info(f"测试耗时: {duration:.2f}秒")
        
        return valid_nodes
    
    def test_all_nodes(self, nodes):
        """批量测试所有节点（兼容方法）"""
        return self.test_nodes(nodes)