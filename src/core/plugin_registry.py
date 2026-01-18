#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插件注册器 - 实现可插拔的收集器架构
"""

import os
import importlib
import inspect
from typing import Dict, Type, List
from src.core.base_collector import BaseCollector
from src.utils.logger import get_logger


class PluginRegistry:
    """插件注册器 - 管理所有收集器插件"""

    def __init__(self):
        self.logger = get_logger("plugin_registry")
        self._collectors: Dict[str, Type[BaseCollector]] = {}
        self._metadata: Dict[str, Dict] = {}

    def discover_collectors(self, collectors_dir: str = "src.collectors") -> None:
        """自动发现并注册所有收集器"""
        self.logger.info("开始发现收集器插件...")

        # 获取collectors目录路径
        collectors_path = collectors_dir.replace(".", os.sep)

        # 遍历collectors目录下的所有Python文件
        for filename in os.listdir(collectors_path):
            if (
                filename.endswith(".py")
                and filename != "__init__.py"
                and filename != "base_collector.py"
                and not filename.startswith("_")
            ):
                module_name = filename[:-3]  # 移除.py扩展名
                full_module_name = f"{collectors_dir}.{module_name}"

                try:
                    self._load_collectors_from_module(full_module_name, module_name)
                except Exception as e:
                    self.logger.error(f"加载模块 {module_name} 失败: {str(e)}")

        self.logger.info(
            f"发现并注册了 {len(self._collectors)} 个收集器: {list(self._collectors.keys())}"
        )

    def _load_collectors_from_module(self, module_name: str, site_key: str) -> None:
        """从模块中加载收集器类"""
        try:
            # 动态导入模块
            module = importlib.import_module(module_name)

            # 查找模块中的所有类
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # 检查是否继承自BaseCollector且不是BaseCollector本身
                if (
                    issubclass(obj, BaseCollector)
                    and obj != BaseCollector
                    and obj.__module__ == module_name
                ):
                    # 注册收集器
                    self._collectors[site_key] = obj

                    # 提取元数据
                    self._metadata[site_key] = {
                        "class_name": name,
                        "module": module_name,
                        "site_key": site_key,
                        "description": obj.__doc__ or f"{site_key} 收集器",
                    }

                    self.logger.info(f"注册收集器: {site_key} -> {name}")
                    break  # 每个模块只注册一个收集器

        except ImportError as e:
            self.logger.error(f"导入模块 {module_name} 失败: {str(e)}")
        except Exception as e:
            self.logger.error(f"处理模块 {module_name} 时出错: {str(e)}")

    def get_collector(self, site_key: str) -> Type[BaseCollector]:
        """获取指定网站的收集器类"""
        if site_key not in self._collectors:
            raise ValueError(f"未找到网站 '{site_key}' 的收集器")
        return self._collectors[site_key]

    def get_all_collectors(self) -> Dict[str, Type[BaseCollector]]:
        """获取所有已注册的收集器"""
        return self._collectors.copy()

    def get_available_sites(self) -> List[str]:
        """获取所有可用的网站列表"""
        return list(self._collectors.keys())

    def get_collector_metadata(self, site_key: str) -> Dict:
        """获取收集器元数据"""
        return self._metadata.get(site_key, {})

    def is_collector_available(self, site_key: str) -> bool:
        """检查收集器是否可用"""
        return site_key in self._collectors

    def create_collector_instance(
        self, site_key: str, site_config: Dict
    ) -> BaseCollector:
        """创建收集器实例"""
        collector_class = self.get_collector(site_key)
        return collector_class(site_config)


# 全局注册器实例
_registry = None


def get_registry() -> PluginRegistry:
    """获取全局注册器实例"""
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
        _registry.discover_collectors()
    return _registry


def register_collector(site_key: str, collector_class: Type[BaseCollector]) -> None:
    """手动注册收集器（装饰器模式）"""

    def decorator(cls):
        registry = get_registry()
        registry._collectors[site_key] = cls
        registry._metadata[site_key] = {
            "class_name": cls.__name__,
            "module": cls.__module__,
            "site_key": site_key,
            "description": cls.__doc__ or f"{site_key} 收集器",
        }
        return cls

    return decorator


# 装饰器示例用法
# @register_collector('example_site')
# class ExampleSiteCollector(BaseCollector):
#     """示例网站收集器"""
#     pass
