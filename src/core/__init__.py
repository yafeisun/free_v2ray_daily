#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心模块 - 提供插件系统和核心功能
"""

from .plugin_registry import PluginRegistry, get_registry, register_collector

__all__ = ['PluginRegistry', 'get_registry', 'register_collector']