#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Subs-Check 管理器 - 管理subs-check内核的运行和配置
"""

import os
import sys
import subprocess
import time
from typing import List, Optional, Tuple
from src.subscheck.config import SubsCheckConfig
from src.utils.logger import get_logger


class SubsCheckManager:
    """Subs-Check 管理器"""
    
    def __init__(self, project_root: str = None):
        """
        初始化管理器
        
        Args:
            project_root: 项目根目录
        """
        self.logger = get_logger("subscheck_manager")
        
        # 设置项目根目录
        if project_root is None:
            self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        else:
            self.project_root = project_root
        
        # 子目录路径
        self.subscheck_dir = os.path.join(self.project_root, 'subscheck')
        self.config_dir = os.path.join(self.subscheck_dir, 'config')
        self.binary_dir = os.path.join(self.subscheck_dir, 'bin')
        
        # 配置管理器
        self.config_file = os.path.join(self.config_dir, 'config.yaml')
        self.config_mgr = SubsCheckConfig(self.config_file)
        
        # subs-check二进制文件
        self.binary_name = 'subs-check'
        self.binary_path = os.path.join(self.binary_dir, self.binary_name)
        
        # 进程
        self.process = None
    
    def check_binary(self) -> bool:
        """
        检查subs-check二进制文件是否存在
        
        Returns:
            exists: 是否存在
        """
        return os.path.exists(self.binary_path)
    
    def download_binary(self) -> bool:
        """
        下载subs-check二进制文件
        
        Returns:
            success: 是否下载成功
        """
        try:
            self.logger.info("开始下载subs-check二进制文件...")
            
            # 确保目录存在
            os.makedirs(self.binary_dir, exist_ok=True)
            
            # 确定下载URL
            platform = sys.platform
            if platform == 'linux':
                download_url = 'https://github.com/beck-8/subs-check/releases/latest/download/subs-check_Linux_x86_64.tar.gz'
            elif platform == 'darwin':
                download_url = 'https://github.com/beck-8/subs-check/releases/latest/download/subs-check_Darwin_x86_64.tar.gz'
            elif platform == 'win32':
                download_url = 'https://github.com/beck-8/subs-check/releases/latest/download/subs-check_Windows_x86_64.zip'
            else:
                raise Exception(f"不支持的操作系统: {platform}")
            
            # 下载文件
            import requests
            tar_file = os.path.join(self.binary_dir, 'subs-check.tar.gz')
            
            self.logger.info(f"从 {download_url} 下载...")
            response = requests.get(download_url, stream=True, timeout=300)
            response.raise_for_status()
            
            with open(tar_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 解压文件
            self.logger.info("解压文件...")
            if platform in ['linux', 'darwin']:
                import tarfile
                with tarfile.open(tar_file, 'r:gz') as tar:
                    tar.extractall(self.binary_dir)
            elif platform == 'win32':
                import zipfile
                with zipfile.ZipFile(tar_file, 'r') as zip_ref:
                    zip_ref.extractall(self.binary_dir)
            
            # 设置执行权限
            if platform != 'win32':
                os.chmod(self.binary_path, 0o755)
            
            # 清理临时文件
            os.remove(tar_file)
            
            self.logger.info(f"subs-check二进制文件下载成功: {self.binary_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"下载subs-check二进制文件失败: {str(e)}")
            return False
    
    def ensure_binary(self) -> bool:
        """
        确保subs-check二进制文件存在
        
        Returns:
            success: 是否成功
        """
        if self.check_binary():
            return True
        
        self.logger.warning("subs-check二进制文件不存在，开始下载...")
        return self.download_binary()
    
    def ensure_config(self, sub_urls: List[str] = None) -> bool:
        """
        确保配置文件存在
        
        Args:
            sub_urls: 订阅链接列表
            
        Returns:
            success: 是否成功
        """
        try:
            if not os.path.exists(self.config_file):
                self.logger.info("创建默认配置文件...")
                self.config_mgr.create_default_config(self.config_file, self.project_root)
            
            # 如果提供了订阅链接，更新配置
            if sub_urls:
                self.config_mgr.update_sub_urls(sub_urls)
            
            return True
        except Exception as e:
            self.logger.error(f"确保配置文件失败: {str(e)}")
            return False
    
    def run(self, sub_urls: List[str] = None, timeout: int = 600) -> Tuple[bool, str]:
        """
        运行subs-check
        
        Args:
            sub_urls: 订阅链接列表
            timeout: 超时时间（秒）
            
        Returns:
            (success, message): 是否成功和消息
        """
        try:
            # 确保二进制文件存在
            if not self.ensure_binary():
                return False, "subs-check二进制文件下载失败"
            
            # 确保配置文件存在
            if not self.ensure_config(sub_urls):
                return False, "配置文件创建失败"
            
            # 检查是否已经有进程在运行
            if self.process and self.process.poll() is None:
                self.logger.warning("subs-check已经在运行中")
                return True, "subs-check已经在运行中"
            
            # 运行subs-check
            self.logger.info("启动subs-check...")
            
            cmd = [self.binary_path, '-f', self.config_file]
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.subscheck_dir
            )
            
            # 等待进程完成
            try:
                stdout, stderr = self.process.communicate(timeout=timeout)
                
                if self.process.returncode == 0:
                    self.logger.info("subs-check运行成功")
                    return True, "subs-check运行成功"
                else:
                    error_msg = stderr.decode('utf-8') if stderr else "未知错误"
                    self.logger.error(f"subs-check运行失败: {error_msg}")
                    return False, f"subs-check运行失败: {error_msg}"
            
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
                return False, "subs-check运行超时"
        
        except Exception as e:
            self.logger.error(f"运行subs-check失败: {str(e)}")
            return False, f"运行subs-check失败: {str(e)}"
    
    def get_output_file(self) -> Optional[str]:
        """
        获取输出文件路径
        
        Returns:
            output_file: 输出文件路径
        """
        try:
            output_dir = self.config_mgr.get('output-dir')
            return os.path.join(output_dir, 'all.yaml')
        except Exception as e:
            self.logger.error(f"获取输出文件路径失败: {str(e)}")
            return None
    
    def parse_output_file(self) -> List[str]:
        """
        解析输出文件，提取节点
        
        Returns:
            nodes: 节点列表
        """
        try:
            output_file = self.get_output_file()
            
            if not output_file or not os.path.exists(output_file):
                self.logger.warning("输出文件不存在")
                return []
            
            import yaml
            
            with open(output_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # 提取节点
            nodes = []
            if data and 'proxies' in data:
                for proxy in data['proxies']:
                    # 将节点转换为字符串格式
                    # 这里需要根据不同的协议类型进行转换
                    # 简化处理，直接返回原始数据
                    nodes.append(str(proxy))
            
            self.logger.info(f"从输出文件中提取到 {len(nodes)} 个节点")
            return nodes
        
        except Exception as e:
            self.logger.error(f"解析输出文件失败: {str(e)}")
            return []
    
    def stop(self) -> bool:
        """
        停止subs-check
        
        Returns:
            success: 是否停止成功
        """
        try:
            if self.process and self.process.poll() is None:
                self.logger.info("停止subs-check...")
                self.process.terminate()
                self.process.wait(timeout=10)
                self.logger.info("subs-check已停止")
                return True
            return True
        except Exception as e:
            self.logger.error(f"停止subs-check失败: {str(e)}")
            return False
