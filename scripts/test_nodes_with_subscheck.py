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
from typing import List, Dict, Any

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
                'concurrent': 20,
                'check-interval': 120,
                'timeout': 5000,
                
                # 测速配置
                'alive-test-url': 'http://gstatic.com/generate_204',
                'speed-test-url': 'https://github.com/AaronFeng753/Waifu2x-Extension-GUI/releases/download/v2.21.12/Waifu2x-Extension-GUI-v2.21.12-Portable.7z',
                'min-speed': 512,
                'download-timeout': 10,
                'download-mb': 20,
                'total-speed-limit': 0,
                
                # 流媒体检测
                'media-check': True,
                'media-check-timeout': 10,
                'platforms': [
                    'iprisk',
                    'youtube',
                    'netflix',
                    'openai',
                    'gemini'
                ],
                
                # 节点配置
                'rename-node': True,
                'node-prefix': '',
                'success-limit': 0,
                
                # 输出配置
                'output-dir': self.output_dir,
                'listen-port': ':8199',
                'save-method': 'local',
                
                # Web UI
                'enable-web-ui': False,
                'api-key': '',
                
                # Sub-Store
                'sub-store-port': ':8299',
                'sub-store-path': '',
                'mihomo-overwrite-url': 'http://127.0.0.1:8199/sub/ACL4SSR_Online_Full.yaml',
                
                # 代理配置
                'github-proxy': '',
                'proxy': '',
                
                # 其他
                'keep-success-proxies': False,
                'sub-urls-retry': 3,
                'sub-urls-get-ua': 'clash.meta (https://github.com/beck-8/subs-check)',
                
                # 使用本地文件
                'local-path': subscription_file
            }
            
            # 保存配置
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
                stderr=subprocess.STDOUT,
                cwd=self.subscheck_dir,
                universal_newlines=True
            )
            
            # 实时输出日志
            start_time = time.time()
            
            while True:
                # 检查超时
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    self.logger.error("测试超时")
                    self.process.terminate()
                    self.process.wait(timeout=10)
                    return False, "测试超时"
                
                # 读取输出
                try:
                    line = self.process.stdout.readline()
                    if line:
                        print(line.strip())
                except:
                    break
                
                # 检查进程是否结束
                if self.process.poll() is not None:
                    break
                
                time.sleep(0.1)
            
            # 等待进程结束
            return_code = self.process.wait()
            
            if return_code == 0:
                self.logger.info("测试成功完成")
                return True, "测试成功"
            else:
                self.logger.error(f"测试失败，返回码: {return_code}")
                return False, f"测试失败，返回码: {return_code}"
            
        except Exception as e:
            self.logger.error(f"运行测试失败: {str(e)}")
            return False, str(e)
    
    def parse_results(self) -> List[str]:
        """解析测试结果"""
        try:
            if not os.path.exists(self.output_file):
                self.logger.warning("输出文件不存在")
                return []
            
            self.logger.info(f"解析输出文件: {self.output_file}")
            
            with open(self.output_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # 提取节点
            nodes = []
            if data and 'proxies' in data:
                for proxy in data['proxies']:
                    # 这里需要将Clash节点转换回V2Ray URI格式
                    # 暂时保存节点名称
                    nodes.append(proxy.get('name', 'Unknown'))
            
            self.logger.info(f"从测试结果中提取到 {len(nodes)} 个有效节点")
            return nodes
            
        except Exception as e:
            self.logger.error(f"解析测试结果失败: {str(e)}")
            return []


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
    import convert_nodes_to_subscription
    subscription_file = os.path.join(os.path.dirname(args.output), 'clash_subscription.yaml')
    
    # 导入转换函数
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from convert_nodes_to_subscription import convert_nodes_to_clash
    
    clash_config = convert_nodes_to_clash(nodes)
    
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
    
    # 将Clash结果转换回V2Ray格式
    if os.path.exists(tester.output_file):
        if convert_nodes_to_vless_yaml(tester.output_file, args.output):
            logger.info(f"有效节点已保存到: {args.output}")
        else:
            logger.warning("转换节点失败，使用Clash格式输出")
            # 直接复制Clash输出
            import shutil
            shutil.copy(tester.output_file, args.output)
    else:
        logger.warning("输出文件不存在")
    
    logger.info("✓ 测试完成")
    sys.exit(0)


if __name__ == "__main__":
    main()