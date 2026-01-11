#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Subs-Check 配置管理模块
"""

import os
import yaml
from typing import Dict, List, Optional


class SubsCheckConfig:
    """Subs-Check 配置管理器"""
    
    def __init__(self, config_file: str = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = {}
        
        if config_file and os.path.exists(config_file):
            self.load_config()
    
    def load_config(self) -> Dict:
        """
        加载配置文件
        
        Returns:
            config: 配置字典
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            return self.config
        except Exception as e:
            raise Exception(f"加载配置文件失败: {str(e)}")
    
    def save_config(self, config: Dict = None) -> bool:
        """
        保存配置文件
        
        Args:
            config: 配置字典，如果为None则使用当前配置
            
        Returns:
            success: 是否保存成功
        """
        try:
            config_to_save = config if config is not None else self.config
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_to_save, f, allow_unicode=True, default_flow_style=False)
            
            if config is not None:
                self.config = config
            
            return True
        except Exception as e:
            raise Exception(f"保存配置文件失败: {str(e)}")
    
    def get_default_config(self, project_root: str) -> Dict:
        """
        获取默认配置
        
        Args:
            project_root: 项目根目录
            
        Returns:
            config: 默认配置字典
        """
        return {
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
            'output-dir': os.path.join(project_root, 'output'),
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
            'sub-urls-get-ua': 'clash.meta (https://github.com/beck-8/subs-check)'
        }
    
    def create_default_config(self, config_file: str, project_root: str) -> bool:
        """
        创建默认配置文件
        
        Args:
            config_file: 配置文件路径
            project_root: 项目根目录
            
        Returns:
            success: 是否创建成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            # 获取默认配置
            default_config = self.get_default_config(project_root)
            
            # 保存配置
            self.config_file = config_file
            self.config = default_config
            self.save_config()
            
            return True
        except Exception as e:
            raise Exception(f"创建默认配置文件失败: {str(e)}")
    
    def update_sub_urls(self, sub_urls: List[str]) -> bool:
        """
        更新订阅链接
        
        Args:
            sub_urls: 订阅链接列表
            
        Returns:
            success: 是否更新成功
        """
        try:
            self.config['sub-urls'] = sub_urls
            return self.save_config()
        except Exception as e:
            raise Exception(f"更新订阅链接失败: {str(e)}")
    
    def get(self, key: str, default=None):
        """
        获取配置项
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            value: 配置值
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value) -> bool:
        """
        设置配置项
        
        Args:
            key: 配置键
            value: 配置值
            
        Returns:
            success: 是否设置成功
        """
        try:
            self.config[key] = value
            return self.save_config()
        except Exception as e:
            raise Exception(f"设置配置项失败: {str(e)}")
