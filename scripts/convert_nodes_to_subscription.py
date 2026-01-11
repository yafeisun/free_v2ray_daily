#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将V2Ray节点列表转换为Clash订阅格式
"""

import sys
import os
import base64
import json
import yaml
from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs, unquote

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def parse_vmess(vmess_uri: str) -> Dict[str, Any]:
    """解析 vmess:// 节点"""
    try:
        # vmess URI 可能是 Base64 编码的 JSON
        if vmess_uri.startswith('vmess://'):
            encoded = vmess_uri[8:]
            try:
                decoded = base64.b64decode(encoded).decode('utf-8')
                config = json.loads(decoded)
                
                return {
                    'name': config.get('ps', 'VMess'),
                    'type': 'vmess',
                    'server': config.get('add', ''),
                    'port': int(config.get('port', 443)),
                    'uuid': config.get('id', ''),
                    'alterId': config.get('aid', 0),
                    'cipher': config.get('scy', 'auto'),
                    'udp': True,
                    'network': config.get('net', 'tcp'),
                    'tls': config.get('tls', '') == 'tls',
                    'skip-cert-verify': True,
                    'ws-opts': {
                        'path': config.get('path', ''),
                        'headers': {
                            'Host': config.get('host', '')
                        }
                    } if config.get('net') == 'ws' else None
                }
            except:
                pass
    except Exception as e:
        print(f"解析 vmess 节点失败: {e}")
    return None


def parse_vless(vless_uri: str) -> Dict[str, Any]:
    """解析 vless:// 节点"""
    try:
        if not vless_uri.startswith('vless://'):
            return None
        
        # 移除 vless:// 前缀
        uri = vless_uri[8:]
        
        # 分割 UUID 和参数
        if '?' in uri:
            uuid_part, params_part = uri.split('?', 1)
        else:
            uuid_part = uri
            params_part = ''
        
        # 分割 UUID 和地址
        if '@' in uuid_part:
            uuid, addr_port = uuid_part.split('@', 1)
        else:
            return None
        
        # 分割地址和端口
        if ':' in addr_port:
            server, port = addr_port.rsplit(':', 1)
        else:
            return None
        
        # 分割端口和名称
        if '#' in port:
            port, name = port.split('#', 1)
            name = unquote(name)
        else:
            name = 'VLESS'
        
        # 解析参数
        params = parse_qs(params_part)
        
        network = params.get('type', ['tcp'])[0]
        security = params.get('security', ['none'])[0]
        
        proxy = {
            'name': name,
            'type': 'vless',
            'server': server,
            'port': int(port),
            'uuid': uuid,
            'udp': True,
            'network': network,
            'tls': security == 'tls' or security == 'reality',
            'skip-cert-verify': params.get('insecure', ['0'])[0] == '1',
            'flow': params.get('flow', [''])[0] if security == 'reality' else '',
            'servername': params.get('sni', [''])[0],
            'client-fingerprint': params.get('fp', ['chrome'])[0],
            'reality-opts': {
                'public-key': params.get('pbk', [''])[0],
                'short-id': params.get('sid', [''])[0]
            } if security == 'reality' else None,
            'ws-opts': {
                'path': params.get('path', [''])[0],
                'headers': {
                    'Host': params.get('host', [''])[0]
                }
            } if network == 'ws' else None,
            'grpc-opts': {
                'grpc-service-name': params.get('serviceName', [''])[0]
            } if network == 'grpc' else None
        }
        
        return proxy
    except Exception as e:
        print(f"解析 vless 节点失败: {e}")
        return None


def parse_trojan(trojan_uri: str) -> Dict[str, Any]:
    """解析 trojan:// 节点"""
    try:
        if not trojan_uri.startswith('trojan://'):
            return None
        
        # 移除 trojan:// 前缀
        uri = trojan_uri[9:]
        
        # 分割密码和地址
        if '@' in uri:
            password, addr_port = uri.split('@', 1)
        else:
            return None
        
        # 分割地址和端口
        if ':' in addr_port:
            server, port = addr_port.rsplit(':', 1)
        else:
            return None
        
        # 分割端口和名称
        if '#' in port:
            port, name = port.split('#', 1)
            name = unquote(name)
        else:
            name = 'Trojan'
        
        # 解析参数
        if '?' in port:
            port, params_part = port.split('?', 1)
        else:
            params_part = ''
        
        params = parse_qs(params_part)
        
        proxy = {
            'name': name,
            'type': 'trojan',
            'server': server,
            'port': int(port),
            'password': password,
            'udp': True,
            'skip-cert-verify': params.get('insecure', ['0'])[0] == '1',
            'sni': params.get('sni', [''])[0]
        }
        
        return proxy
    except Exception as e:
        print(f"解析 trojan 节点失败: {e}")
        return None


def parse_ss(ss_uri: str) -> Dict[str, Any]:
    """解析 ss:// 节点"""
    try:
        if not ss_uri.startswith('ss://'):
            return None
        
        # 移除 ss:// 前缀
        uri = ss_uri[5:]
        
        # 分离名称
        if '#' in uri:
            encoded, name = uri.rsplit('#', 1)
            name = unquote(name)
        else:
            encoded = uri
            name = 'SS'
        
        # 分离参数
        if '?' in encoded:
            encoded, params_part = encoded.split('?', 1)
        else:
            params_part = ''
        
        # 解析参数
        params = parse_qs(params_part)
        
        # 尝试多种解码方式
        decoded = None
        
        # 方法1: UUID 格式 (ss://uuid@server:port)
        if not decoded and '@' in encoded and '-' in encoded.split('@')[0]:
            try:
                uuid_part, server_port = encoded.split('@', 1)
                # 检查是否是 UUID 格式
                if len(uuid_part) == 36 and uuid_part.count('-') == 4:
                    # 这是 UUID 格式，使用默认配置
                    if ':' in server_port:
                        server, port = server_port.split(':', 1)
                        proxy = {
                            'name': name,
                            'type': 'ss',
                            'server': server,
                            'port': int(port),
                            'cipher': 'aes-256-gcm',
                            'password': uuid_part,
                            'udp': True
                        }
                        return proxy
            except:
                pass
        
        # 方法2: JSON 格式 (ss://base64({"add":"...","ps":"...",...}))
        if not decoded:
            try:
                padding = 4 - len(encoded) % 4
                if padding != 4:
                    encoded += '=' * padding
                decoded = base64.b64decode(encoded).decode('utf-8')
                if decoded.startswith('{'):
                    # JSON 格式
                    config = json.loads(decoded)
                    proxy = {
                        'name': config.get('ps', name),
                        'type': 'ss',
                        'server': config.get('add', ''),
                        'port': int(config.get('port', 8388)),
                        'cipher': config.get('method', 'aes-256-gcm'),
                        'password': config.get('password', ''),
                        'udp': True
                    }
                    return proxy
            except:
                decoded = None
        
        # 方法3: 标准 Base64 解码
        if not decoded:
            try:
                padding = 4 - len(encoded) % 4
                if padding != 4:
                    encoded += '=' * padding
                decoded = base64.b64decode(encoded).decode('utf-8')
            except:
                pass
        
        # 方法4: 尝试 URL 解码后再 Base64
        if not decoded:
            try:
                url_decoded = unquote(encoded)
                padding = 4 - len(url_decoded) % 4
                if padding != 4:
                    url_decoded += '=' * padding
                decoded = base64.b64decode(url_decoded).decode('utf-8')
            except:
                pass
        
        # 方法5: 尝试直接解析（URL 格式: base64(method:password)@server:port）
        if not decoded and '@' in encoded:
            try:
                credentials, server_port = encoded.split('@', 1)
                padding = 4 - len(credentials) % 4
                if padding != 4:
                    credentials += '=' * padding
                method_password = base64.b64decode(credentials).decode('utf-8')
                if ':' in method_password:
                    method, password = method_password.split(':', 1)
                    decoded = f"{method}:{password}@{server_port}"
            except:
                pass
        
        # 方法6: 尝试旧格式 (server:port:method:password)
        if not decoded:
            try:
                padding = 4 - len(encoded) % 4
                if padding != 4:
                    encoded += '=' * padding
                decoded = base64.b64decode(encoded).decode('utf-8')
                parts = decoded.split(':')
                if len(parts) == 4:
                    server, port, method, password = parts
                    decoded = f"{method}:{password}@{server}:{port}"
            except:
                pass
        
        if not decoded:
            return None
        
        # 解析解码后的内容
        if '@' in decoded:
            method_password, server_port = decoded.rsplit('@', 1)
        else:
            return None
        
        if ':' in method_password:
            method, password = method_password.split(':', 1)
        else:
            return None
        
        if ':' in server_port:
            server, port = server_port.rsplit(':', 1)
        else:
            return None
        
        proxy = {
            'name': name,
            'type': 'ss',
            'server': server,
            'port': int(port),
            'cipher': method,
            'password': password,
            'udp': True
        }
        
        # 添加插件配置
        if 'plugin' in params:
            proxy['plugin'] = params['plugin'][0]
            if 'plugin-opts' in params:
                proxy['plugin-opts'] = params['plugin-opts'][0]
        
        # 添加 TLS 配置
        if 'security' in params and params['security'][0] == 'tls':
            proxy['udp'] = True
            proxy['tls'] = True
            proxy['skip-cert-verify'] = params.get('insecure', ['0'])[0] == '1'
            proxy['sni'] = params.get('sni', [''])[0]
            
            if params.get('type', [''])[0] == 'ws':
                proxy['network'] = 'ws'
                proxy['ws-opts'] = {
                    'path': params.get('path', [''])[0],
                    'headers': {
                        'Host': params.get('host', [''])[0]
                    }
                }
        
        return proxy
    except Exception as e:
        return None


def parse_hysteria2(hysteria2_uri: str) -> Dict[str, Any]:
    """解析 hysteria2:// 节点"""
    try:
        if not hysteria2_uri.startswith('hysteria2://'):
            return None
        
        # 移除 hysteria2:// 前缀
        uri = hysteria2_uri[12:]
        
        # 分割 UUID 和地址
        if '@' in uri:
            uuid, addr_port = uri.split('@', 1)
        else:
            return None
        
        # 分割地址和端口
        if ':' in addr_port:
            server, port = addr_port.rsplit(':', 1)
        else:
            return None
        
        # 分割端口和名称
        if '#' in port:
            port, name = port.split('#', 1)
            name = unquote(name)
        else:
            name = 'Hysteria2'
        
        # 解析参数
        if '?' in port:
            port, params_part = port.split('?', 1)
        else:
            params_part = ''
        
        params = parse_qs(params_part)
        
        proxy = {
            'name': name,
            'type': 'hysteria2',
            'server': server,
            'port': int(port),
            'password': uuid,
            'udp': True,
            'skip-cert-verify': params.get('insecure', ['0'])[0] == '1',
            'sni': params.get('sni', [''])[0]
        }
        
        return proxy
    except Exception as e:
        print(f"解析 hysteria2 节点失败: {e}")
        return None


def convert_nodes_to_clash(nodes: List[str]) -> Dict[str, Any]:
    """
    将V2Ray节点列表转换为Clash订阅格式
    
    Args:
        nodes: 节点列表
        
    Returns:
        clash_config: Clash配置字典
    """
    proxies = []
    failed_count = 0
    
    for i, node in enumerate(nodes):
        node = node.strip()
        if not node:
            continue
        
        proxy = None
        
        # 根据协议类型解析节点
        if node.startswith('vmess://'):
            proxy = parse_vmess(node)
        elif node.startswith('vless://'):
            proxy = parse_vless(node)
        elif node.startswith('trojan://'):
            proxy = parse_trojan(node)
        elif node.startswith('ss://'):
            proxy = parse_ss(node)
        elif node.startswith('hysteria2://'):
            proxy = parse_hysteria2(node)
        
        if proxy:
            proxies.append(proxy)
        else:
            failed_count += 1
    
    # 每100个失败打印一次统计
    if failed_count > 0 and failed_count % 100 == 0:
        print(f"已处理 {len(nodes)} 个节点，成功 {len(proxies)} 个，失败 {failed_count} 个")
    
    # 创建 Clash 配置
    clash_config = {
        'port': 7890,
        'socks-port': 7891,
        'allow-lan': True,
        'mode': 'rule',
        'log-level': 'info',
        'proxies': proxies,
        'proxy-groups': [
            {
                'name': 'Proxy',
                'type': 'select',
                'proxies': [p['name'] for p in proxies] if len(proxies) > 0 else ['DIRECT']
            }
        ],
        'rules': [
            'MATCH,Proxy'
        ]
    }
    
    return clash_config


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='将V2Ray节点列表转换为Clash订阅格式')
    parser.add_argument('--input', default='result/nodetotal.txt', help='输入节点文件')
    parser.add_argument('--output', default='result/clash_subscription.yaml', help='输出Clash订阅文件')
    
    args = parser.parse_args()
    
    # 读取节点
    print(f"读取节点文件: {args.input}")
    with open(args.input, 'r', encoding='utf-8') as f:
        nodes = [line.strip() for line in f if line.strip()]
    
    print(f"读取到 {len(nodes)} 个节点")
    
    # 转换为 Clash 格式
    print("转换为 Clash 格式...")
    clash_config = convert_nodes_to_clash(nodes)
    
    print(f"成功转换 {len(clash_config['proxies'])} 个节点")
    
    # 保存 Clash 配置
    print(f"保存到: {args.output}")
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        yaml.dump(clash_config, f, allow_unicode=True, default_flow_style=False)
    
    print("✓ 转换完成")


if __name__ == "__main__":
    main()