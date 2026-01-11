#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础测试器 - 定义测试器接口和通用功能
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from src.utils.logger import get_logger


class BaseTester(ABC):
    """测试器基类"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def test_node(self, node: str) -> Tuple[bool, Dict]:
        """
        测试单个节点
        
        Args:
            node: 节点字符串
            
        Returns:
            (is_valid, result_info): 是否有效和结果信息
        """
        pass
    
    @abstractmethod
    def test_nodes(self, nodes: List[str]) -> List[str]:
        """
        批量测试节点
        
        Args:
            nodes: 节点列表
            
        Returns:
            valid_nodes: 有效节点列表
        """
        pass
    
    def extract_host_port(self, node: str) -> Tuple[Optional[str], Optional[int]]:
        """
        从节点中提取主机和端口
        
        Args:
            node: 节点字符串
            
        Returns:
            (host, port): 主机和端口
        """
        try:
            from urllib.parse import urlparse
            import base64
            import json
            
            if node.startswith('vmess://'):
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
    
    def get_node_type(self, node: str) -> str:
        """
        从节点中提取传输类型
        
        Args:
            node: 节点字符串
            
        Returns:
            node_type: 节点传输类型
        """
        try:
            from urllib.parse import urlparse
            import base64
            import json
            
            node_type = None
            
            if node.startswith('vmess://'):
                data = node[8:]
                data += '=' * (-len(data) % 4)
                decoded = base64.b64decode(data).decode('utf-8')
                config = json.loads(decoded)
                node_type = config.get('net', 'tcp')
                
            elif node.startswith('vless://') or node.startswith('trojan://') or node.startswith('ss://'):
                parsed = urlparse(node)
                if parsed.query:
                    params = {}
                    for param in parsed.query.split('&'):
                        if '=' in param:
                            key, value = param.split('=', 1)
                            params[key] = value
                    node_type = params.get('type', 'tcp')
            
            return node_type.lower() if node_type else 'tcp'
            
        except Exception as e:
            self.logger.error(f"提取节点类型失败: {str(e)}")
            return 'tcp'
