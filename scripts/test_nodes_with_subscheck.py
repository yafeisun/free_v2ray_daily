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
    
    def create_config(self, subscription_file: str) -> bool:
        """创建subs-check配置文件"""
        try:
            self.logger.info("创建subs-check配置文件...")
            
            config = {
                # 基本配置
                'print-progress': True,
                'concurrent': 30,
                'check-interval': 120,
                'timeout': 3000,
                
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
                'platforms': [
                    'youtube',
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
                    f'http://127.0.0.1:{self.http_server_port}/result/clash_subscription.yaml'
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
    
    def run_test(self, timeout: int = 1800) -> Tuple[bool, str]:
        """运行测试"""
        try:
            # 启动HTTP服务器
            if not self.start_http_server():
                return False, "HTTP服务器启动失败"
            
            self.logger.info("开始运行subs-check测试...")
            
            # 检查二进制文件
            if not os.path.exists(self.binary_path):
                self.logger.warning("subs-check不存在，开始安装...")
                if not self.install_subscheck():
                    return False, "subs-check安装失败"
            
            # 运行subs-check
            cmd = [self.binary_path, '-f', self.config_file]
            
            self.logger.info(f"执行命令: {' '.join(cmd)}")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 合并 stderr 到 stdout
                cwd=self.project_root,  # 使用项目根目录作为工作目录
                universal_newlines=False,  # 使用二进制模式避免缓冲
                bufsize=0  # 完全无缓冲
            )
            
            # 实时输出日志
            start_time = time.time()
            last_progress_time = start_time
            line_count = 0
            last_line = ""
            stderr_lines = []
            
            while True:
                # 检查超时
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    self.logger.error("测试超时")
                    self.process.terminate()
                    self.process.wait(timeout=10)
                    return False, "测试超时"
                
                # 读取输出（按字节读取以避免行缓冲）
                try:
                    byte = self.process.stdout.read(1)
                    if byte:
                        # 将字节解码为字符
                        char = byte.decode('utf-8', errors='ignore')
                        if char == '\n':
                            # 打印完整行
                            if last_line.strip():
                                print(last_line.strip(), flush=True)
                                stderr_lines.append(last_line.strip())
                                line_count += 1
                            last_line = ""
                        elif char == '\r':
                            # 处理进度条（\r表示行首，用于更新进度条）
                            if last_line.strip():
                                print(last_line.strip(), flush=True)
                                stderr_lines.append(last_line.strip())
                                line_count += 1
                            last_line = ""
                        else:
                            last_line += char
                            # 定期刷新输出（每100个字符）
                            if len(last_line) >= 100:
                                print(last_line, end='', flush=True)
                                last_line = ""
                except:
                    break
                
                # 定期打印进度（每30秒）
                if time.time() - last_progress_time >= 30:
                    if last_line.strip():
                        print(last_line.strip(), flush=True)
                    self.logger.info(f"测试进行中... 已运行 {int(time.time() - start_time)} 秒，已读取 {line_count} 行输出")
                    last_progress_time = time.time()
                
                # 检查进程是否结束
                if self.process.poll() is not None:
                    break
                
                time.sleep(0.01)  # 更频繁的检查
            
            # 等待进程结束
            return_code = self.process.wait()
            
            # 停止HTTP服务器
            self.stop_http_server()
            
            if return_code == 0:
                self.logger.info("测试成功完成")
                return True, "测试成功"
            else:
                error_msg = f"测试失败，返回码: {return_code}"
                if stderr_lines:
                    error_msg += f"\n错误信息:\n" + "\n".join(stderr_lines[-10:])  # 只显示最后10行
                self.logger.error(error_msg)
                return False, error_msg
            
        except Exception as e:
            # 确保停止HTTP服务器
            self.stop_http_server()
            self.logger.error(f"运行测试失败: {str(e)}")
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
            if data and 'proxies' in data:
                for proxy in data['proxies']:
                    # 提取地区信息
                    region = self._extract_region(proxy)
                    
                    # 提取地区编号
                    region_number = self._extract_region_number(proxy)
                    
                    # 提取测试结果
                    media_info = self._extract_media_info(proxy)
                    
                    # 计算通过的测试数量
                    passed_tests = sum([media_info['gpt'], media_info['gemini'], media_info['youtube']])
                    
                    # 3选1规则：至少通过2个测试才能保留
                    if passed_tests < 2:
                        continue
                    
                    # 生成新名称
                    new_name = self._generate_node_name(region, region_number, media_info)
                    
                    # 将Clash节点转换回V2Ray URI格式
                    v2ray_uri = self._convert_proxy_to_uri(proxy, new_name)
                    if v2ray_uri:
                        renamed_nodes.append(v2ray_uri)
            
            self.logger.info(f"从测试结果中提取并重命名 {len(renamed_nodes)} 个有效节点")
            return renamed_nodes
            
        except Exception as e:
            self.logger.error(f"解析测试结果失败: {str(e)}")
            return []
    
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
                            params.append(f"path={ws_opts['path']}")
                
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
    parser.add_argument('--timeout', type=int, default=1800, help='测试超时时间（秒）')
    
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
    
    # 创建配置
    if not tester.create_config(subscription_file):
        logger.error("创建配置文件失败")
        sys.exit(1)
    
    # 运行测试
    success, message = tester.run_test(timeout=args.timeout)
    
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