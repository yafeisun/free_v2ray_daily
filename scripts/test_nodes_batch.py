#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
节点测速脚本 - 使用线程池分批测试
"""

import sys
import os
import subprocess
import time
import yaml
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logger import get_logger


class BatchNodeTester:
    """基于线程池的分批节点测试器"""
    
    def __init__(self, project_root: str = None):
        """初始化测试器"""
        self.logger = get_logger("batch_tester")
        
        # 设置项目根目录
        if project_root is None:
            self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.project_root = project_root
        
        # 路径配置
        self.subscheck_dir = os.path.join(self.project_root, 'subscheck')
        self.binary_path = os.path.join(self.subscheck_dir, 'bin', 'subs-check')
        self.config_dir = os.path.join(self.subscheck_dir, 'config')
        self.output_dir = os.path.join(self.project_root, 'output')
        
        # 测试配置
        self.batch_size = 100  # 每批节点数
        self.max_workers = 2  # 并发批次数
        self.concurrent = 5  # 每个批次的并发数（降低以减少失败率）
        
        # 测试超时（每批）
        self.batch_timeout = 1800  # 30分钟
    
    def create_unified_config(self) -> str:
        """创建统一的配置文件（所有批次共享）"""
        config_file = os.path.join(self.config_dir, 'batch_config.yaml')
        
        config = {
            # 基本配置
            'print-progress': True,
            'concurrent': self.concurrent,
            'check-interval': 999999,
            'timeout': 10000,  # 增加到10秒
            
            # 测速配置
            'alive-test-url': 'http://gstatic.com/generate_204',
            'speed-test-url': '',
            'min-speed': 0,
            'download-timeout': 1,
            'download-mb': 0,
            'total-speed-limit': 0,
            
            # 流媒体检测
            'media-check': True,
            'media-check-timeout': 8,
            'platforms': ['youtube', 'openai', 'gemini'],
            
            # 节点配置
            'rename-node': True,
            'node-prefix': '',
            'success-limit': 0,
            
            # 输出配置
            'output-dir': self.output_dir,
            'listen-port': '',
            'save-method': 'local',
            
            # Web UI
            'enable-web-ui': False,
            'api-key': '',
            
            # Sub-Store
            'sub-store-port': '',
            'sub-store-path': '',
            
            # 代理配置
            'github-proxy': '',
            'proxy': '',
            
            # 其他
            'keep-success-proxies': False,
            'sub-urls-retry': 3,
            'sub-urls-get-ua': 'clash.meta (https://github.com/beck-8/subs-check)',
            
            # 订阅链接（统一配置，通过命令行参数覆盖）
            'sub-urls': []
        }
        
        # 保存配置
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        self.logger.info(f"统一配置文件已创建: {config_file}")
        return config_file
    
    def clean_old_configs(self):
        """清理旧的批次配置文件"""
        import glob
        old_configs = glob.glob(os.path.join(self.config_dir, 'batch_*.yaml'))
        for old_config in old_configs:
            try:
                os.remove(old_config)
                self.logger.info(f"清理旧配置文件: {old_config}")
            except Exception as e:
                self.logger.warning(f"清理配置文件失败 {old_config}: {str(e)}")
    
    def run_single_batch(self, batch_nodes: List[str], batch_index: int, http_server_port: int) -> List[str]:
        """运行单个批次的测试"""
        self.logger.info(f"开始测试批次 {batch_index}，节点数: {len(batch_nodes)}")
        
        try:
            # 为当前批次创建独立的订阅文件
            batch_subscription_file = os.path.join(self.project_root, 'result', f'batch_subscription_{batch_index}.yaml')
            from scripts import convert_nodes_to_subscription
            batch_clash_config = convert_nodes_to_subscription.convert_nodes_to_clash(batch_nodes)
            with open(batch_subscription_file, 'w', encoding='utf-8') as f:
                yaml.dump(batch_clash_config, f, allow_unicode=True, default_flow_style=False)
            
            # 使用统一配置文件，通过命令行参数指定订阅URL
            config_file = os.path.join(self.config_dir, 'batch_config.yaml')
            subscription_url = f'http://127.0.0.1:{http_server_port}/result/batch_subscription_{batch_index}.yaml'
            
            # 运行subs-check，使用命令行参数覆盖订阅URL
            cmd = [self.binary_path, '-f', config_file, '--sub-url', subscription_url]
            
            self.logger.info(f"执行命令: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=self.project_root,
                universal_newlines=False,
                bufsize=0
            )
            
            # 实时输出日志
            start_time = time.time()
            last_output_time = start_time
            last_line = ""
            last_progress = 0
            last_progress_time = start_time
            
            while True:
                # 检查超时
                elapsed = time.time() - start_time
                if elapsed > self.batch_timeout:
                    self.logger.error(f"批次 {batch_index} 超时（{self.batch_timeout}秒），强制终止")
                    process.terminate()
                    process.wait(timeout=10)
                    break
                
                # 检查静默超时
                if time.time() - last_output_time > 300:
                    self.logger.info(f"批次 {batch_index} 300秒无输出，认为已完成")
                    break
                
                # 检查进度停滞（超过90%且120秒无变化）
                if last_progress >= 90.0 and (time.time() - last_progress_time) > 120:
                    self.logger.warning(f"批次 {batch_index} 进度停滞在 {last_progress}% 超过120秒，强制终止")
                    process.terminate()
                    process.wait(timeout=10)
                    break
                
                # 读取输出
                try:
                    import select
                    ready, _, _ = select.select([process.stdout], [], [], 1.0)
                    if ready:
                        byte = process.stdout.read(1)
                        if byte:
                            last_output_time = time.time()
                            char = byte.decode('utf-8', errors='ignore')
                            if char == '\n':
                                if last_line.strip():
                                    print(f"[批次{batch_index}] {last_line.strip()}")
                                    # 解析进度
                                    import re
                                    progress_match = re.search(r'\[.*?\]\s+(\d+\.?\d*)%\s+\((\d+)/(\d+)\)', last_line)
                                    if progress_match:
                                        current_progress = float(progress_match.group(1))
                                        if current_progress > last_progress:
                                            last_progress = current_progress
                                            last_progress_time = time.time()
                                last_line = ""
                            elif char == '\r':
                                if last_line.strip():
                                    print(f"[批次{batch_index}] {last_line.strip()}")
                                    # 解析进度（回车符也可能包含进度信息）
                                    import re
                                    progress_match = re.search(r'\[.*?\]\s+(\d+\.?\d*)%\s+\((\d+)/(\d+)\)', last_line)
                                    if progress_match:
                                        current_progress = float(progress_match.group(1))
                                        if current_progress > last_progress:
                                            last_progress = current_progress
                                            last_progress_time = time.time()
                                last_line = ""
                            else:
                                last_line += char
                        else:
                            break
                except (OSError, ValueError):
                    break
                
                # 检查进程是否结束
                if process.poll() is not None:
                    break
                
                time.sleep(0.01)
            
            # 等待进程结束
            return_code = process.wait(timeout=30)
            self.logger.info(f"批次 {batch_index} 完成，返回码: {return_code}")
            
            # 解析结果
            output_file = os.path.join(self.output_dir, 'all.yaml')
            if os.path.exists(output_file):
                results = self.parse_results(output_file)
                self.logger.info(f"批次 {batch_index} 有效节点数: {len(results)}")
                return results
            else:
                self.logger.warning(f"批次 {batch_index} 输出文件不存在")
                return []
            
        except Exception as e:
            self.logger.error(f"批次 {batch_index} 测试失败: {str(e)}")
            return []
    
    def parse_results(self, output_file: str) -> List[str]:
        """解析测试结果"""
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            results = []
            if data and 'proxies' in data:
                for proxy in data['proxies']:
                    # 提取媒体信息
                    media_info = self._extract_media_info(proxy)
                    
                    # 2选1规则：GPT或Gemini至少通过1个
                    if media_info['gpt'] or media_info['gemini']:
                        # 生成新名称
                        region = self._extract_region(proxy)
                        region_number = self._extract_region_number(proxy)
                        new_name = self._generate_node_name(region, region_number, media_info)
                        
                        # 转换为V2Ray URI
                        v2ray_uri = self._convert_proxy_to_uri(proxy, new_name)
                        if v2ray_uri:
                            results.append(v2ray_uri)
            
            return results
        
        except Exception as e:
            self.logger.error(f"解析结果失败: {str(e)}")
            return []
    
    def _extract_region(self, proxy: dict) -> str:
        """提取地区信息"""
        import re
        name = proxy.get('name', '')
        match = re.search(r'[🇦-🇿]{2}([A-Z]{2})_\d+', name)
        if match:
            return match.group(1)
        return 'US'
    
    def _extract_region_number(self, proxy: dict) -> int:
        """提取地区编号"""
        import re
        name = proxy.get('name', '')
        match = re.search(r'[🇦-🇿]{2}[A-Z]{2}_(\d+)', name)
        if match:
            return int(match.group(1))
        return 1
    
    def _extract_media_info(self, proxy: dict) -> dict:
        """提取媒体测试结果"""
        media_info = {'gpt': False, 'gemini': False, 'youtube': False}
        name = proxy.get('name', '')
        
        if 'GPT⁺' in name:
            media_info['gpt'] = True
        if 'GM' in name:
            media_info['gemini'] = True
        if '|YT-' in name:
            media_info['youtube'] = True
        
        return media_info
    
    def _generate_node_name(self, region: str, number: int, media_info: dict) -> str:
        """生成节点名称"""
        flags = {'HK': '🇭🇰', 'US': '🇺🇸', 'JP': '🇯🇵', 'SG': '🇸🇬', 'TW': '🇨🇳', 'KR': '🇰🇷'}
        flag = flags.get(region, '')
        
        ai_tag = ''
        if media_info['gpt'] and media_info['gemini']:
            ai_tag = 'GPT|GM'
        elif media_info['gpt']:
            ai_tag = 'GPT'
        elif media_info['gemini']:
            ai_tag = 'GM'
        
        yt_tag = '|YT' if media_info['youtube'] else ''
        
        return f"{flag}{region}_{number}|{ai_tag}{yt_tag}"
    
    def _convert_proxy_to_uri(self, proxy: dict, new_name: str) -> str:
        """转换Clash节点为V2Ray URI"""
        try:
            proxy_type = proxy.get('type', '')
            
            if proxy_type == 'ss':
                cipher = proxy.get('cipher', 'aes-256-gcm')
                password = proxy.get('password', '')
                server = proxy.get('server', '')
                port = proxy.get('port', 443)
                return f"ss://{cipher}:{password}@{server}:{port}#{new_name}"
            
            elif proxy_type == 'vless':
                uuid = proxy.get('uuid', '')
                server = proxy.get('server', '')
                port = proxy.get('port', 443)
                params = ['encryption=none', 'security=tls', 'type=tcp']
                uri = f"vless://{uuid}@{server}:{port}?{'&'.join(params)}#{new_name}"
                return uri
            
            elif proxy_type == 'trojan':
                password = proxy.get('password', '')
                server = proxy.get('server', '')
                port = proxy.get('port', 443)
                params = ['security=tls']
                uri = f"trojan://{password}@{server}:{port}?{'&'.join(params)}#{new_name}"
                return uri
            
            elif proxy_type == 'hysteria2':
                password = proxy.get('password', '')
                server = proxy.get('server', '')
                port = proxy.get('port', 443)
                uri = f"hysteria2://{password}@{server}:{port}?insecure=1#{new_name}"
                return uri
            
            return ''
        
        except Exception as e:
            self.logger.error(f"转换节点失败: {str(e)}")
            return ''
    
    def test_nodes(self, nodes: List[str]) -> List[str]:
        """使用线程池分批测试节点"""
        self.logger.info(f"开始分批测试，总节点数: {len(nodes)}")
        self.logger.info(f"批次大小: {self.batch_size}, 并发批次数: {self.max_workers}")
        
        # 将节点分成批次
        batches = []
        for i in range(0, len(nodes), self.batch_size):
            batch = nodes[i:i + self.batch_size]
            batches.append(batch)
        
        self.logger.info(f"共 {len(batches)} 个批次")
        
        # 清理旧的批次配置文件
        self.clean_old_configs()
        
        # 创建统一配置文件（所有批次共享）
        self.create_unified_config()
        
        # 启动HTTP服务器
        http_server_port = 8888
        self.logger.info(f"启动HTTP服务器，端口: {http_server_port}")
        http_server_process = subprocess.Popen(
            ['python3', '-m', 'http.server', str(http_server_port), '--directory', self.project_root],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        time.sleep(5)  # 等待服务器启动
        
        try:
            # 使用线程池并发处理批次
            all_results = []
            completed = 0
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {}
                
                # 提交所有批次
                for i, batch in enumerate(batches):
                    future = executor.submit(self.run_single_batch, batch, i, http_server_port)
                    futures[future] = i
                
                # 收集结果
                for future in as_completed(futures):
                    batch_index = futures[future]
                    try:
                        results = future.result()
                        all_results.extend(results)
                        completed += 1
                        self.logger.info(f"批次 {batch_index} 完成，累计有效节点: {len(all_results)}/{completed}/{len(batches)}")
                    except Exception as e:
                        self.logger.error(f"批次 {batch_index} 失败: {str(e)}")
            
            self.logger.info(f"分批测试完成，总有效节点: {len(all_results)}")
            return all_results
        
        finally:
            # 停止HTTP服务器
            if http_server_process:
                http_server_process.terminate()
                http_server_process.wait(timeout=5)
                self.logger.info("HTTP服务器已停止")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='节点测速脚本 - 使用线程池分批测试')
    parser.add_argument('--input', default='result/nodetotal.txt', help='输入节点文件')
    parser.add_argument('--output', default='result/nodelist.txt', help='输出节点文件')
    parser.add_argument('--batch-size', type=int, default=100, help='每批节点数')
    parser.add_argument('--max-workers', type=int, default=2, help='并发批次数')
    
    args = parser.parse_args()
    
    logger = get_logger("main")
    
    # 检查输入文件
    if not os.path.exists(args.input):
        logger.error(f"输入文件不存在: {args.input}")
        sys.exit(1)
    
    # 读取节点
    logger.info(f"读取节点文件: {args.input}")
    with open(args.input, 'r', encoding='utf-8') as f:
        nodes = [line.strip() for line in f if line.strip()]
    
    logger.info(f"读取到 {len(nodes)} 个节点")
    
    # 运行分批测试
    tester = BatchNodeTester()
    tester.batch_size = args.batch_size
    tester.max_workers = args.max_workers
    
    valid_nodes = tester.test_nodes(nodes)
    
    if valid_nodes:
        # 保存结果
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            for node in valid_nodes:
                f.write(f"{node}\n")
        logger.info(f"有效节点已保存到: {args.output}")
    else:
        logger.warning("未找到有效节点")
    
    logger.info("测试完成")


if __name__ == "__main__":
    main()