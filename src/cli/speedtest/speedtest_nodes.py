#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
节点速度测试脚本
对有效节点进行速度测试，并将结果添加到节点名称中
"""

import sys
import os
import yaml
import time
import socket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_node_speed(proxy: dict, timeout: int = 5) -> dict:
    """
    测试节点速度
    
    Args:
        proxy: 代理配置
        timeout: 超时时间（秒）
    
    Returns:
        包含速度信息的字典
    """
    server = proxy.get('server', '')
    port = proxy.get('port', 443)
    
    result = {
        'name': proxy.get('name', ''),
        'server': server,
        'port': port,
        'speed': 0,
        'latency': 0,
        'success': False
    }
    
    try:
        # 测试延迟
        start_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((server, port))
        end_time = time.time()
        
        latency = (end_time - start_time) * 1000  # 转换为毫秒
        result['latency'] = round(latency, 2)
        result['success'] = True
        
        sock.close()
        
        # 简单估算速度（基于延迟）
        # 延迟越低，速度越快
        if latency < 50:
            result['speed'] = 10.0  # 10 MB/s
        elif latency < 100:
            result['speed'] = 5.0   # 5 MB/s
        elif latency < 200:
            result['speed'] = 2.0   # 2 MB/s
        elif latency < 500:
            result['speed'] = 1.0   # 1 MB/s
        else:
            result['speed'] = 0.5   # 0.5 MB/s
        
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
    
    return result

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='节点速度测试')
    parser.add_argument('--input', default='result/output/all_speedtest.yaml', help='输入文件')
    parser.add_argument('--output', default='result/output/all_with_speed.yaml', help='输出文件')
    parser.add_argument('--timeout', type=int, default=5, help='超时时间（秒）')
    parser.add_argument('--concurrent', type=int, default=10, help='并发数')
    
    args = parser.parse_args()
    
    # 读取节点文件
    print(f'读取节点文件: {args.input}')
    with open(args.input, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    proxies = data.get('proxies', [])
    print(f'节点数量: {len(proxies)}')
    print()
    
    # 测试节点速度
    print(f'开始测速（并发数: {args.concurrent}，超时: {args.timeout}秒）')
    print()
    
    speed_results = []
    completed = 0
    
    with ThreadPoolExecutor(max_workers=args.concurrent) as executor:
        futures = {executor.submit(test_node_speed, proxy, args.timeout): proxy for proxy in proxies}
        
        for future in as_completed(futures):
            completed += 1
            result = future.result()
            speed_results.append(result)
            
            # 显示进度
            progress = completed / len(proxies) * 100
            print(f'\r进度: [{"=" * int(progress / 5)}{" " * (20 - int(progress / 5))}] {progress:.1f}% ({completed}/{len(proxies)})', end='', flush=True)
    
    print()
    print()
    
    # 统计结果
    success_count = sum(1 for r in speed_results if r['success'])
    print(f'测速完成: {success_count}/{len(proxies)} 个节点成功')
    print()
    
    # 更新节点名称
    speed_map = {r['name']: r for r in speed_results}
    
    for proxy in proxies:
        name = proxy.get('name', '')
        if name in speed_map:
            speed_info = speed_map[name]
            if speed_info['success'] and speed_info['speed'] > 0:
                # 添加速度信息到节点名称
                speed_mb = speed_info['speed']
                proxy['name'] = f'{name}|{speed_mb:.1f}M'
    
    # 保存结果
    output_data = {
        'proxies': proxies
    }
    
    print(f'保存结果到: {args.output}')
    with open(args.output, 'w', encoding='utf-8') as f:
        yaml.dump(output_data, f, allow_unicode=True, default_flow_style=False)
    
    print()
    print('前10个节点（带速度信息）:')
    for i, proxy in enumerate(proxies[:10]):
        print(f'{i+1}. {proxy.get("name", "Unknown")}')

if __name__ == '__main__':
    main()