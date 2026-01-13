#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
节点测速脚本 - 使用subs-check进行真实的代理测试
"""

import sys
import os
import subprocess
import time
import yaml
from typing import List, Dict, Any, Tuple

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logger import get_logger


class SubsCheckTester:
    """使用subs-check进行节点测试"""
    
    def __init__(self, project_root: str = None):
        """初始化测试器"""
        self.logger = get_logger("subscheck_tester")
        
        # 设置项目根目录
        if project_root is None:
            self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.project_root = project_root
        
        # 路径配置
        self.subscheck_dir = os.path.join(self.project_root, 'subscheck')
        self.binary_path = os.path.join(self.subscheck_dir, 'bin', 'subs-check')
        self.config_file = os.path.join(self.subscheck_dir, 'config', 'config.yaml')
        self.output_dir = os.path.join(self.project_root, 'output')
        self.output_file = os.path.join(self.output_dir, 'all.yaml')
        
        # 进程
        self.process = None
        
        # HTTP服务器
        self.http_server = None
        self.http_server_port = 8888
        self.http_server_process = None
    
    def start_http_server(self) -> bool:
        """启动HTTP服务器"""
        try:
            self.logger.info(f"启动HTTP服务器，端口: {self.http_server_port}")
            
            # 启动HTTP服务器
            self.http_server_process = subprocess.Popen(
                ['python3', '-m', 'http.server', str(self.http_server_port), '--directory', self.project_root],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # 等待服务器启动（增加等待时间确保完全启动）
            import time
            time.sleep(5)
            
            # 检查服务器是否成功启动
            if self.http_server_process.poll() is None:
                self.logger.info(f"HTTP服务器启动成功: http://127.0.0.1:{self.http_server_port}")
                return True
            else:
                self.logger.error("HTTP服务器启动失败")
                return False
                
        except Exception as e:
            self.logger.error(f"启动HTTP服务器失败: {str(e)}")
            return False
    
    def stop_http_server(self):
        """停止HTTP服务器"""
        if self.http_server_process:
            try:
                self.http_server_process.terminate()
                self.http_server_process.wait(timeout=5)
                self.logger.info("HTTP服务器已停止")
            except:
                self.http_server_process.kill()
            self.http_server_process = None
        
        # HTTP服务器
        self.http_server = None
        self.http_server_port = 8888
        self.http_server_process = None
    
    def install_subscheck(self) -> bool:
        """安装subs-check工具"""
        try:
            self.logger.info("开始安装subs-check工具...")
            
            # 创建目录
            os.makedirs(os.path.join(self.subscheck_dir, 'bin'), exist_ok=True)
            os.makedirs(os.path.join(self.subscheck_dir, 'config'), exist_ok=True)
            os.makedirs(self.output_dir, exist_ok=True)
            
            # 检测系统架构
            import platform
            system = platform.system().lower()
            machine = platform.machine().lower()
            
            # 确定下载URL
            if system == 'linux':
                if machine in ['x86_64', 'amd64']:
                    download_url = 'https://github.com/beck-8/subs-check/releases/latest/download/subs-check_Linux_x86_64.tar.gz'
                elif machine in ['aarch64', 'arm64']:
                    download_url = 'https://github.com/beck-8/subs-check/releases/latest/download/subs-check_Linux_arm64.tar.gz'
                else:
                    self.logger.error(f"不支持的架构: {machine}")
                    return False
            else:
                self.logger.error(f"不支持的操作系统: {system}")
                return False
            
            self.logger.info(f"下载URL: {download_url}")
            
            # 下载文件
            tar_file = os.path.join(self.subscheck_dir, 'bin', 'subs-check.tar.gz')
            
            import requests
            self.logger.info("下载subs-check...")
            response = requests.get(download_url, stream=True, timeout=300)
            response.raise_for_status()
            
            with open(tar_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 解压文件
            self.logger.info("解压文件...")
            import tarfile
            with tarfile.open(tar_file, 'r:gz') as tar:
                tar.extractall(os.path.join(self.subscheck_dir, 'bin'))
            
            # 设置执行权限
            os.chmod(self.binary_path, 0o755)
            
            # 清理临时文件
            os.remove(tar_file)
            
            self.logger.info(f"subs-check安装成功: {self.binary_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"安装subs-check失败: {str(e)}")
            return False
    
    def create_config(self, subscription_file: str, concurrent: int = 20, phase: int = 1) -> bool:
        """创建subs-check配置文件

        Args:
            subscription_file: 订阅文件路径
            concurrent: 并发数
            phase: 测试阶段（1=连通性测试，2=媒体检测）
        """
        try:
            self.logger.info(f"创建subs-check配置文件（阶段{phase}）...")

            # 根据阶段设置不同的配置
            if phase == 1:
                # 阶段1: 快速连通性测试（禁用媒体检测，高并发）
                config = {
                    # 基本配置
                    'print-progress': True,
                    'concurrent': 20,  # 高并发
                    'check-interval': 999999,
                    'timeout': 10000,  # 连通性测试超时10秒

                    # 测速配置
                    'alive-test-url': 'http://gstatic.com/generate_204',
                    'speed-test-url': '',
                    'min-speed': 0,
                    'download-timeout': 1,
                    'download-mb': 0,
                    'total-speed-limit': 0,

                    # 流媒体检测（禁用）
                    'media-check': False,
                    'media-check-timeout': 0,
                    'platforms': [],

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

                    # 使用HTTP服务器提供本地文件
                    'sub-urls': [
                        f'http://127.0.0.1:{self.http_server_port}/{subscription_file}'
                    ]
                }
            else:
                # 阶段2: 媒体检测（只检测openai和gemini，低并发）
                config = {
                    # 基本配置
                    'print-progress': True,
                    'concurrent': 5,  # 低并发
                    'check-interval': 999999,
                    'timeout': 15000,  # 连通性测试超时15秒

                    # 测速配置
                    'alive-test-url': 'http://gstatic.com/generate_204',
                    'speed-test-url': '',
                    'min-speed': 0,
                    'download-timeout': 1,
                    'download-mb': 0,
                    'total-speed-limit': 0,

                    # 流媒体检测（只检测openai和gemini，不检测youtube）
                    'media-check': True,
                    'media-check-timeout': 10,  # 增加超时
                    'platforms': [
                        'openai',
                        'gemini'
                    ],

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

                    # 使用HTTP服务器提供本地文件
                    'sub-urls': [
                        f'http://127.0.0.1:{self.http_server_port}/{subscription_file}'
                    ]
                }

            # 保存配置
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

            self.logger.info(f"配置文件创建成功: {self.config_file}")
            return True

        except Exception as e:
            self.logger.error(f"创建配置文件失败: {str(e)}")
            return False
    
    def run_test(self, node_count: int = 0, timeout: int = None) -> Tuple[bool, str]:
        """运行测试（两阶段测试）"""
        try:
            # 启动HTTP服务器
            if not self.start_http_server():
                return False, "HTTP服务器启动失败"

            # 检查二进制文件
            if not os.path.exists(self.binary_path):
                self.logger.warning("subs-check不存在，开始安装...")
                if not self.install_subscheck():
                    return False, "subs-check安装失败"

            # 阶段1: 连通性测试
            self.logger.info("=" * 60)
            self.logger.info("阶段1: 连通性测试（禁用媒体检测，高并发）")
            self.logger.info("=" * 60)
            phase1_success, phase1_message = self.run_phase1(node_count, timeout)

            if not phase1_success:
                self.logger.error(f"阶段1失败: {phase1_message}")
                self.stop_http_server()
                return False, f"阶段1失败: {phase1_message}"

            # 读取阶段1结果
            phase1_nodes = []
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                if data and 'proxies' in data:
                    phase1_nodes = [proxy for proxy in data['proxies']]
                    self.logger.info(f"阶段1可用节点数: {len(phase1_nodes)}")
            except Exception as e:
                self.logger.error(f"读取阶段1结果失败: {str(e)}")
                self.stop_http_server()
                return False, f"读取阶段1结果失败: {str(e)}"

            if not phase1_nodes:
                self.logger.warning("阶段1无可用节点，跳过阶段2")
                self.stop_http_server()
                return True, "阶段1完成，无可用节点"

            # 阶段2: 媒体检测
            self.logger.info("=" * 60)
            self.logger.info(f"阶段2: 媒体检测（节点数: {len(phase1_nodes)}）")
            self.logger.info("=" * 60)
            phase2_success, phase2_message = self.run_phase2(len(phase1_nodes), timeout)

            # 停止HTTP服务器
            self.stop_http_server()

            if not phase2_success:
                self.logger.warning(f"阶段2失败: {phase2_message}")
                # 阶段2失败不影响整体成功，返回阶段1的结果
                return True, f"阶段1完成，阶段2失败: {phase2_message}"

            return True, "两阶段测试完成"

        except Exception as e:
            self.logger.error(f"测试失败: {str(e)}")
            self.stop_http_server()
            return False, f"测试失败: {str(e)}"

    def run_phase1(self, node_count: int = 0, timeout: int = None) -> Tuple[bool, str]:
        """阶段1: 连通性测试（禁用媒体检测，高并发）"""
        try:
            # 创建阶段1配置
            if not self.create_config('result/clash_subscription.yaml', concurrent=20, phase=1):
                return False, "创建阶段1配置失败"

            # 动态计算超时时间
            if timeout is None:
                if node_count > 0:
                    # 阶段1只做连通性测试，速度快
                    base_time = (node_count / 20) * 10  # 每个节点10秒
                    timeout = int(base_time * 1.5)  # 缓冲1.5倍
                    self.logger.info(f"节点数: {node_count}, 动态计算超时时间: {timeout}秒 ({timeout/60:.1f}分钟)")
                else:
                    timeout = 3600  # 默认1小时
                    self.logger.info(f"未提供节点数，使用默认超时: {timeout}秒")

            self.logger.info("开始运行阶段1测试...")

            # 运行subs-check
            cmd = [self.binary_path, '-f', self.config_file]

            self.logger.info(f"执行命令: {' '.join(cmd)}")

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=self.project_root,
                universal_newlines=False,
                bufsize=0
            )

            # 实时输出日志
            return self._monitor_process(timeout, phase=1)

        except Exception as e:
            self.logger.error(f"阶段1测试失败: {str(e)}")
            return False, str(e)

    def run_phase2(self, node_count: int = 0, timeout: int = None) -> Tuple[bool, str]:
        """阶段2: 媒体检测（只检测openai和gemini，低并发）"""
        try:
            # 创建阶段2配置
            if not self.create_config('result/clash_subscription.yaml', concurrent=5, phase=2):
                return False, "创建阶段2配置失败"

            # 动态计算超时时间
            if timeout is None:
                if node_count > 0:
                    # 阶段2只检测2个平台
                    base_time = (node_count / 5) * (2 * 10)  # 每个节点20秒（2个平台×10秒）
                    timeout = int(base_time * 2.0)  # 缓冲2倍
                    self.logger.info(f"节点数: {node_count}, 动态计算超时时间: {timeout}秒 ({timeout/60:.1f}分钟)")
                else:
                    timeout = 3600  # 默认1小时
                    self.logger.info(f"未提供节点数，使用默认超时: {timeout}秒")

            self.logger.info("开始运行阶段2测试...")

            # 运行subs-check
            cmd = [self.binary_path, '-f', self.config_file]

            self.logger.info(f"执行命令: {' '.join(cmd)}")

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=self.project_root,
                universal_newlines=False,
                bufsize=0
            )

            # 实时输出日志
            return self._monitor_process(timeout, phase=2)

        except Exception as e:
            self.logger.error(f"阶段2测试失败: {str(e)}")
            return False, str(e)

    def _monitor_process(self, timeout: int, phase: int = 1) -> Tuple[bool, str]:
        """监控进程输出"""
        try:
            start_time = time.time()
            last_output_time = start_time
            last_line = ""
            line_count = 0

            while True:
                # 检查总超时
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    self.logger.error(f"阶段{phase}超过超时时间 {timeout}秒 ({timeout/60:.1f}分钟)，强制终止")
                    self.process.terminate()
                    self.process.wait(timeout=10)
                    return False, f"阶段{phase}超时"

                # 解析进度
                import re
                progress_match = re.search(r'\[.*?\]\s+(\d+\.?\d*)%\s+\((\d+)/(\d+)\)', last_line)
                current_progress = 0
                if progress_match:
                    current_progress = float(progress_match.group(1))
                    tested_count = int(progress_match.group(2))
                    total_count = int(progress_match.group(3))

                    # 当进度达到90%以上且测试数量接近总数时，认为测试完成
                    if current_progress >= 90.0 and tested_count >= total_count * 0.9:
                        self.logger.info(f"检测到阶段{phase}测试完成（进度: {current_progress}%, 测试: {tested_count}/{total_count}），准备终止进程")
                        break

                # 检查静默超时（3分钟无输出认为结束）
                silent_timeout = 180  # 3分钟
                if time.time() - last_output_time > silent_timeout:
                    self.logger.info(f"检测到{silent_timeout}秒（{silent_timeout/60:.0f}分钟）无新输出（当前进度: {current_progress:.1f}%），认为阶段{phase}测试已完成")
                    break

                # 使用select检查是否有可读数据
                import select
                try:
                    ready, _, _ = select.select([self.process.stdout], [], [], 1.0)
                    if ready:
                        byte = self.process.stdout.read(1)
                        if byte:
                            last_output_time = time.time()
                            char = byte.decode('utf-8', errors='ignore')
                            if char == '\n':
                                if last_line.strip():
                                    print(f"[P{phase}] {last_line.strip()}", flush=True)
                                    line_count += 1
                                last_line = ""
                            elif char == '\r':
                                if last_line.strip():
                                    print(f"[P{phase}] {last_line.strip()}", flush=True)
                                    line_count += 1
                                last_line = ""
                            else:
                                last_line += char
                                if len(last_line) >= 100:
                                    print(f"[P{phase}] {last_line}", end='', flush=True)
                                    last_line = ""
                        else:
                            break
                except (OSError, ValueError):
                    break

                # 检查进程是否结束
                if self.process.poll() is not None:
                    break

                time.sleep(0.01)

            # 等待进程结束
            try:
                return_code = self.process.wait(timeout=30)
                self.logger.info(f"阶段{phase}进程退出，返回码: {return_code}")
            except subprocess.TimeoutExpired:
                self.logger.warning(f"阶段{phase}进程未在30秒内退出，尝试终止...")
                self.process.terminate()
                try:
                    return_code = self.process.wait(timeout=10)
                    self.logger.info(f"阶段{phase}进程已终止，返回码: {return_code}")
                except subprocess.TimeoutExpired:
                    self.logger.error(f"阶段{phase}进程无法终止，强制kill")
                    self.process.kill()
                    return_code = -1

            # 检查输出文件
            tested_node_count = 0
            if os.path.exists(self.output_file):
                try:
                    with open(self.output_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                    if data and 'proxies' in data:
                        tested_node_count = len(data['proxies'])
                        self.logger.info(f"阶段{phase}输出文件有效，包含 {tested_node_count} 个节点")
                except Exception as e:
                    self.logger.warning(f"检查阶段{phase}输出文件失败: {str(e)}")

            # 判断是否成功
            if tested_node_count > 0:
                return True, f"阶段{phase}完成，测试了{tested_node_count}个节点"
            else:
                return False, f"阶段{phase}完成，但无有效节点"

        except Exception as e:
            self.logger.error(f"监控阶段{phase}进程失败: {str(e)}")
            return False, str(e)
    
    def parse_results(self) -> List[str]:
        """解析测试结果并重命名节点"""
        try:
            if not os.path.exists(self.output_file):
                self.logger.warning("输出文件不存在")
                return []
            
            self.logger.info(f"解析输出文件: {self.output_file}")
            
            with open(self.output_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # 提取节点并重命名
            renamed_nodes = []
            total_count = 0
            media_filtered_count = 0
            
            if data and 'proxies' in data:
                for proxy in data['proxies']:
                    total_count += 1
                    
                    # 提取地区信息
                    region = self._extract_region(proxy)
                    
                    # 提取地区编号
                    region_number = self._extract_region_number(proxy)
                    
                    # 提取测试结果
                    media_info = self._extract_media_info(proxy)

                    # 2选1规则：GPT或Gemini至少通过1个才能保留
                    if not (media_info['gpt'] or media_info['gemini']):
                        media_filtered_count += 1
                        continue
                    
                    # 生成新名称
                    new_name = self._generate_node_name(region, region_number, media_info)
                    
                    # 将Clash节点转换回V2Ray URI格式
                    v2ray_uri = self._convert_proxy_to_uri(proxy, new_name)
                    if v2ray_uri:
                        renamed_nodes.append(v2ray_uri)
            
            self.logger.info(f"节点统计: 总数{total_count}, 媒体过滤{media_filtered_count}, 有效{len(renamed_nodes)}")
            self.logger.info(f"从测试结果中提取并重命名 {len(renamed_nodes)} 个有效节点")
            return renamed_nodes
            
        except Exception as e:
            self.logger.error(f"解析测试结果失败: {str(e)}")
            return []
    
    def _extract_delay_from_name(self, name: str) -> int:
        """从节点名称中提取延迟（毫秒）"""
        import re
        # 节点名称格式：FlagRegion_Number|AI|YT
        # 例如：🇺🇸US_5|GPT|YT → 延迟5ms
        match = re.search(r'[🇦-🇿]{2}[A-Z]{2}_(\d+)\|', name)
        if match:
            try:
                return int(match.group(1))
            except:
                return 0
        return 0
    
    def _extract_region(self, proxy: dict) -> str:
        """从节点中提取地区信息"""
        import re
        name = proxy.get('name', '')
        server = proxy.get('server', '')
        
        # 首先尝试从subs-check的节点名称中提取地区代码（格式：FlagRegion_Number）
        match = re.search(r'[🇦-🇿]{2}([A-Z]{2})_\d+', name)
        if match:
            return match.group(1)
        
        # 检查名称中是否包含地区标识
        region_keywords = {
            'HK': 'HK',
            '香港': 'HK',
            'Hong Kong': 'HK',
            'US': 'US',
            '美国': 'US',
            'USA': 'US',
            'JP': 'JP',
            '日本': 'JP',
            'Japan': 'JP',
            'SG': 'SG',
            '新加坡': 'SG',
            'Singapore': 'SG',
            'TW': 'TW',
            '台湾': 'TW',
            'Taiwan': 'TW',
            'KR': 'KR',
            '韩国': 'KR',
            'Korea': 'KR',
            'DE': 'DE',
            '德国': 'DE',
            'Germany': 'DE',
            'GB': 'GB',
            '英国': 'GB',
            'UK': 'GB',
            'FR': 'FR',
            '法国': 'FR',
            'France': 'FR',
            'CA': 'CA',
            '加拿大': 'CA',
            'Canada': 'CA',
        }
        
        for keyword, region in region_keywords.items():
            if keyword in name:
                return region
        
        # 默认返回US
        return 'US'
    
    def _extract_region_number(self, proxy: dict) -> int:
        """从节点中提取地区编号"""
        import re
        name = proxy.get('name', '')
        
        # 从subs-check的节点名称中提取地区编号（格式：FlagRegion_Number）
        match = re.search(r'[🇦-🇿]{2}[A-Z]{2}_(\d+)', name)
        if match:
            return int(match.group(1))
        
        return 1
    
    def _extract_media_info(self, proxy: dict) -> dict:
        """从节点中提取媒体测试结果"""
        media_info = {
            'gpt': False,
            'gemini': False,
            'youtube': False
        }
        
        # subs-check会在节点名称中添加媒体解锁标记
        name = proxy.get('name', '')
        
        # 检查GPT标记（subs-check使用GPT⁺表示ChatGPT可用）
        if 'GPT⁺' in name:
            media_info['gpt'] = True
        
        # 检查Gemini标记（subs-check使用GM表示Gemini可用）
        if 'GM' in name:
            media_info['gemini'] = True
        
        # 检查YouTube标记（subs-check使用YT-{地区代码}格式）
        if '|YT-' in name:
            media_info['youtube'] = True
        
        return media_info
    
    def _generate_node_name(self, region: str, number: int, media_info: dict) -> str:
        """生成节点名称"""
        # 国旗映射
        flags = {
            'HK': '🇭🇰',
            'US': '🇺🇸',
            'JP': '🇯🇵',
            'SG': '🇸🇬',
            'TW': '🇨🇳',
            'KR': '🇰🇷',
            'DE': '🇩🇪',
            'GB': '🇬🇧',
            'FR': '🇫🇷',
            'CA': '🇨🇦',
        }
        
        flag = flags.get(region, '')
        
        # 生成AI标记
        ai_tag = ''
        if media_info['gpt'] and media_info['gemini']:
            ai_tag = 'GPT|GM'
        elif media_info['gpt']:
            ai_tag = 'GPT'
        elif media_info['gemini']:
            ai_tag = 'GM'
        
        # 生成YouTube标记
        if media_info['youtube']:
            if ai_tag:
                # 如果有AI标记，使用|YT
                yt_tag = '|YT'
            else:
                # 如果没有AI标记，直接使用YT
                yt_tag = 'YT'
        else:
            yt_tag = ''
        
        # 组合名称
        return f"{flag}{region}_{number}|{ai_tag}{yt_tag}"
    
    def _convert_proxy_to_uri(self, proxy: dict, new_name: str) -> str:
        """将Clash节点转换回V2Ray URI格式"""
        try:
            proxy_type = proxy.get('type', '')
            
            if proxy_type == 'ss':
                # Shadowsocks节点
                cipher = proxy.get('cipher', 'aes-256-gcm')
                password = proxy.get('password', '')
                server = proxy.get('server', '')
                port = proxy.get('port', 443)
                return f"ss://{cipher}:{password}@{server}:{port}#{new_name}"
            
            elif proxy_type == 'vmess':
                # VMess节点
                return f"vmess://{new_name}"
            
            elif proxy_type == 'vless':
                # VLESS节点
                uuid = proxy.get('uuid', '')
                server = proxy.get('server', '')
                port = proxy.get('port', 443)
                security = proxy.get('tls', False)
                sni = proxy.get('servername', '')
                network = proxy.get('network', 'tcp')
                
                # 构建VLESS URI
                params = []
                params.append(f"encryption=none")
                if security:
                    params.append(f"security=tls")
                    if sni:
                        params.append(f"sni={sni}")
                params.append(f"type={network}")
                
                if network == 'ws':
                    ws_opts = proxy.get('ws-opts', {})
                    if ws_opts:
                        if 'headers' in ws_opts and 'Host' in ws_opts['headers']:
                            params.append(f"host={ws_opts['headers']['Host']}")
                        if 'path' in ws_opts:
                            path = ws_opts['path']
                            # 移除path中包含的旧名称（#后面的内容）
                            if '#' in path:
                                path = path.split('#')[0]
                            # URL编码path中的#符号，避免URI格式错误
                            if '#' in path:
                                import urllib.parse
                                path = urllib.parse.quote(path, safe='')
                            params.append(f"path={path}")
                
                uri = f"vless://{uuid}@{server}:{port}?{'&'.join(params)}#{new_name}"
                return uri
            
            elif proxy_type == 'trojan':
                # Trojan节点
                password = proxy.get('password', '')
                server = proxy.get('server', '')
                port = proxy.get('port', 443)
                sni = proxy.get('sni', '')
                
                params = []
                params.append(f"security=tls")
                if sni:
                    params.append(f"sni={sni}")
                
                uri = f"trojan://{password}@{server}:{port}?{'&'.join(params)}#{new_name}"
                return uri
            
            elif proxy_type == 'hysteria2':
                # Hysteria2节点
                password = proxy.get('password', '')
                server = proxy.get('server', '')
                port = proxy.get('port', 443)
                
                uri = f"hysteria2://{password}@{server}:{port}?insecure=1#{new_name}"
                return uri
            
            else:
                self.logger.warning(f"不支持的节点类型: {proxy_type}")
                return ''
        
        except Exception as e:
            self.logger.error(f"转换节点失败: {str(e)}")
            return ''


def convert_nodes_to_vless_yaml(clash_file: str, output_file: str) -> bool:
    """
    将Clash节点转换为VLESS订阅格式
    
    Args:
        clash_file: Clash配置文件路径
        output_file: 输出文件路径
    """
    try:
        logger = get_logger("converter")
        
        with open(clash_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        proxies = data.get('proxies', [])
        nodes = []
        
        for proxy in proxies:
            # 根据类型转换节点
            if proxy.get('type') == 'ss':
                # Shadowsocks节点
                node = f"ss://{proxy.get('cipher')}:{proxy.get('password')}@{proxy.get('server')}:{proxy.get('port')}#{proxy.get('name', 'SS')}"
                nodes.append(node)
            elif proxy.get('type') == 'vmess':
                # VMess节点
                node = f"vmess://{proxy.get('name', 'VMess')}"
                nodes.append(node)
            elif proxy.get('type') == 'vless':
                # VLESS节点
                node = f"vless://{proxy.get('uuid')}@{proxy.get('server')}:{proxy.get('port')}?encryption=none&security=tls&type=ws&host={proxy.get('ws-opts', {}).get('headers', {}).get('Host', '')}&path={proxy.get('ws-opts', {}).get('path', '')}#{proxy.get('name', 'VLESS')}"
                nodes.append(node)
            elif proxy.get('type') == 'trojan':
                # Trojan节点
                node = f"trojan://{proxy.get('password')}@{proxy.get('server')}:{proxy.get('port')}?security=tls&sni={proxy.get('sni', '')}#{proxy.get('name', 'Trojan')}"
                nodes.append(node)
            elif proxy.get('type') == 'hysteria2':
                # Hysteria2节点
                node = f"hysteria2://{proxy.get('password')}@{proxy.get('server')}:{proxy.get('port')}?insecure=1#{proxy.get('name', 'Hysteria2')}"
                nodes.append(node)
        
        # 保存节点
        with open(output_file, 'w', encoding='utf-8') as f:
            for node in nodes:
                f.write(f"{node}\n")
        
        logger.info(f"成功转换 {len(nodes)} 个节点到: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"转换节点失败: {str(e)}")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='节点测速脚本 - 使用subs-check')
    parser.add_argument('--input', default='result/nodetotal.txt', help='输入节点文件')
    parser.add_argument('--output', default='result/nodelist.txt', help='输出节点文件')
    
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
    
    # 转换为Clash格式
    logger.info("转换为Clash订阅格式...")
    subscription_file = os.path.join(os.path.dirname(args.output), 'clash_subscription.yaml')
    
    # 导入转换函数
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import convert_nodes_to_subscription
    clash_config = convert_nodes_to_subscription.convert_nodes_to_clash(nodes)
    
    # 保存Clash配置
    os.makedirs(os.path.dirname(subscription_file), exist_ok=True)
    with open(subscription_file, 'w', encoding='utf-8') as f:
        yaml.dump(clash_config, f, allow_unicode=True, default_flow_style=False)
    
    logger.info(f"Clash订阅文件已保存: {subscription_file}")
    
    # 运行subs-check测试
    tester = SubsCheckTester()
    
    # 计算并发数（根据CPU核心数）
    cpu_count = os.cpu_count() or 2
    concurrent = max(5, min(cpu_count * 5, 15))
    logger.info(f"系统CPU核心数: {cpu_count}, 动态设置并发数: {concurrent}")
    
    # 创建配置
    if not tester.create_config(subscription_file, concurrent):
        logger.error("创建配置文件失败")
        sys.exit(1)
    
    # 运行测试
    success, message = tester.run_test(node_count=len(nodes))
    
    if not success:
        logger.error(f"测试失败: {message}")
        sys.exit(1)
    
    # 解析结果
    logger.info("解析测试结果...")
    
    # 使用parse_results方法解析结果并重命名节点
    renamed_nodes = tester.parse_results()
    
    if renamed_nodes:
        # 保存重命名后的节点
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            for node in renamed_nodes:
                f.write(f"{node}\n")
        logger.info(f"有效节点已保存到: {args.output}")
    else:
        logger.warning("未找到有效节点")
        # 保留原始Clash输出
        if os.path.exists(tester.output_file):
            import shutil
            shutil.copy(tester.output_file, args.output)
            logger.info(f"使用Clash格式输出: {args.output}")
    
    logger.info("✓ 测试完成")
    sys.exit(0)


if __name__ == "__main__":
    main()