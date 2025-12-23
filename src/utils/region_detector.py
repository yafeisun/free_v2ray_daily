#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地区识别工具
"""

import re
import base64
import json
from .logger import get_logger

class RegionDetector:
    """节点地区识别器"""
    
    def __init__(self):
        self.logger = get_logger("region_detector")
        
        # 香港相关关键词
        self.hk_keywords = [
            'hk', 'hongkong', 'hong kong', '香港', 'hkg', 'hongkong',
            '港', 'HK', 'HKG', 'HongKong', 'Hong Kong'
        ]
        
        # 香港IP段（常见）
        self.hk_ip_patterns = [
            r'103\.2\d{1,2}\.',  # 103.20-29.x.x
            r'104\.2\d{1,2}\.',  # 104.20-29.x.x
            r'1\.2\d{1,2}\.',    # 1.20-29.x.x
            r'202\.6[4-9]\.',     # 202.64-69.x.x
            r'203\.8[0-9]\.',     # 203.80-89.x.x
            r'210\.1[7-9]\.',     # 210.17-19.x.x
            r'218\.2[5-6]\.',     # 218.25-26.x.x
            r'223\.1[6-9]\.',     # 223.16-19.x.x
            r'45\.1[2-5]\.',      # 45.12-15.x.x
        ]
        
        # 香港域名后缀
        self.hk_domains = [
            '.hk', '.com.hk', '.org.hk', '.net.hk'
        ]
    
    def detect_region(self, node):
        """
        检测节点地区
        
        Args:
            node: 节点字符串
            
        Returns:
            str: 地区代码 ('HK' 表示香港, 'OTHER' 表示其他)
        """
        try:
            if self.is_hk_node(node):
                return 'HK'
            else:
                return 'OTHER'
        except Exception as e:
            self.logger.warning(f"地区检测失败: {str(e)}")
            return 'OTHER'
    
    def is_hk_node(self, node):
        """
        判断是否为香港节点
        
        Args:
            node: 节点字符串
            
        Returns:
            bool: 是否为香港节点
        """
        try:
            # 1. 从节点信息中提取主机名
            host = self.extract_host_from_node(node)
            if not host:
                return False
            
            # 2. 检查主机名中是否包含香港关键词
            if self.contains_hk_keywords(host):
                return True
            
            # 3. 检查是否为香港IP
            if self.is_hk_ip(host):
                return True
            
            # 4. 检查是否为香港域名
            if self.is_hk_domain(host):
                return True
            
            # 5. 从节点备注中检查
            remarks = self.extract_remarks_from_node(node)
            if remarks and self.contains_hk_keywords(remarks):
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"香港节点检测失败: {str(e)}")
            return False
    
    def extract_host_from_node(self, node):
        """从节点中提取主机名"""
        try:
            if node.startswith('vmess://'):
                return self.extract_vmess_host(node)
            elif node.startswith('vless://'):
                return self.extract_vless_host(node)
            elif node.startswith('trojan://'):
                return self.extract_trojan_host(node)
            elif node.startswith('hysteria2://') or node.startswith('hysteria://'):
                return self.extract_hysteria_host(node)
            elif node.startswith('ss://'):
                return self.extract_ss_host(node)
            else:
                return None
        except Exception as e:
            self.logger.warning(f"提取主机名失败: {str(e)}")
            return None
    
    def extract_vmess_host(self, node):
        """从VMess节点提取主机名"""
        try:
            data = node[8:]  # 去掉 vmess://
            decoded = json.loads(base64.b64decode(data + '==').decode('utf-8'))
            return decoded.get('add', '')
        except:
            return ''
    
    def extract_vless_host(self, node):
        """从VLESS节点提取主机名"""
        try:
            pattern = r'vless://([^@]+)@([^:]+):'
            match = re.search(pattern, node)
            return match.group(2) if match else ''
        except:
            return ''
    
    def extract_trojan_host(self, node):
        """从Trojan节点提取主机名"""
        try:
            pattern = r'trojan://([^@]+)@([^:]+):'
            match = re.search(pattern, node)
            return match.group(2) if match else ''
        except:
            return ''
    
    def extract_hysteria_host(self, node):
        """从Hysteria节点提取主机名"""
        try:
            pattern = r'hysteria2?://[^@]*@([^:]+):'
            match = re.search(pattern, node)
            return match.group(1) if match else ''
        except:
            return ''
    
    def extract_ss_host(self, node):
        """从Shadowsocks节点提取主机名"""
        try:
            data = node[5:]  # 去掉 ss://
            decoded = base64.b64decode(data).decode('utf-8')
            parts = decoded.split('@')
            if len(parts) >= 2:
                host_port = parts[1].split(':')[0]
                if ':' in host_port:
                    host = host_port.rsplit(':', 1)[0]
                    return host
        except:
            pass
        
        # 备用方法：正则提取
        try:
            pattern = r'ss://[^@]*@([^:]+):'
            match = re.search(pattern, node)
            return match.group(1) if match else ''
        except:
            return ''
    
    def extract_remarks_from_node(self, node):
        """从节点中提取备注信息"""
        try:
            if node.startswith('vmess://'):
                data = node[8:]  # 去掉 vmess://
                decoded = json.loads(base64.b64decode(data + '==').decode('utf-8'))
                return decoded.get('ps', '')
            elif node.startswith('vless://'):
                # VLESS格式: vless://uuid@host:port?name=remarks&...
                pattern = r'name=([^&]+)'
                match = re.search(pattern, node)
                return match.group(1) if match else ''
            elif node.startswith('trojan://'):
                # Trojan格式: trojan://password@host:port?name=remarks&...
                pattern = r'name=([^&]+)'
                match = re.search(pattern, node)
                return match.group(1) if match else ''
            else:
                return ''
        except:
            return ''
    
    def contains_hk_keywords(self, text):
        """检查文本是否包含香港关键词"""
        if not text:
            return False
        
        text_lower = text.lower()
        for keyword in self.hk_keywords:
            if keyword.lower() in text_lower:
                return True
        return False
    
    def is_hk_ip(self, host):
        """检查是否为香港IP"""
        try:
            # 检查是否为IP地址
            ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            if not re.match(ip_pattern, host):
                return False
            
            # 检查是否匹配香港IP段
            for pattern in self.hk_ip_patterns:
                if re.match(pattern, host):
                    return True
            
            return False
        except:
            return False
    
    def is_hk_domain(self, host):
        """检查是否为香港域名"""
        try:
            host_lower = host.lower()
            for domain in self.hk_domains:
                if host_lower.endswith(domain):
                    return True
            return False
        except:
            return False
    
    def classify_nodes(self, nodes):
        """
        对节点进行地区分类
        
        Args:
            nodes: 节点列表
            
        Returns:
            dict: 分类结果 {'HK': [hk_nodes], 'OTHER': [other_nodes]}
        """
        classified = {
            'HK': [],
            'OTHER': []
        }
        
        for node in nodes:
            region = self.detect_region(node)
            classified[region].append(node)
        
        self.logger.info(f"节点分类完成: 香港节点 {len(classified['HK'])} 个, 其他节点 {len(classified['OTHER'])} 个")
        return classified