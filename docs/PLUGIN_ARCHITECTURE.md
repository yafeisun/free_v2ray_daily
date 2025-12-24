# 可插拔架构使用指南

## 架构概述

本项目已重构为可插拔架构，支持动态加载收集器插件。新增网站时只需要添加配置和收集器类，无需修改其他文件。

## 架构优势

### 1. 零代码添加新网站
- 只需创建收集器类和配置文件
- 无需修改主程序或导入文件
- 自动发现和加载新插件

### 2. 配置驱动
- 通过配置文件控制网站启用/禁用
- 配置文件指定收集器插件
- 支持灵活的参数配置

### 3. 统一入口
- 所有网站使用统一的脚本入口
- 支持单个网站或批量运行
- 自动排除失败网站

### 4. 插件隔离
- 每个网站插件相互独立
- 可以独立开发和测试
- 不影响其他网站的功能

## 核心组件

### 1. 插件注册器 (`src/core/plugin_registry.py`)
- 自动发现收集器插件
- 动态导入和实例化
- 提供插件元数据查询

### 2. 基础收集器 (`src/collectors/base_collector.py`)
- 提供通用功能
- 定义标准接口
- 支持方法重写

### 3. 配置管理 (`config/websites.py`)
- 集中管理网站配置
- 指定收集器插件
- 控制启用状态

### 4. 统一脚本 (`scripts/universal_collector.py`)
- 支持所有网站的统一入口
- 命令行参数控制
- 批量运行支持

## 添加新网站步骤

### 1. 创建收集器类
```python
# src/collectors/new_site.py
from src.collectors.base_collector import BaseCollector

class NewSiteCollector(BaseCollector):
    """新网站收集器"""
    
    def __init__(self, site_config):
        super().__init__(site_config)
        # 网站特定的初始化逻辑
    
    def get_latest_article_url(self, target_date=None):
        # 重写方法实现特定逻辑
        return super().get_latest_article_url(target_date)
```

### 2. 添加网站配置
```python
# config/websites.py
"new_site": {
    "name": "新网站",
    "url": "https://newsite.com/",
    "enabled": True,
    "collector_key": "new_site",  # 对应收集器文件名
    "selectors": [...],
    "patterns": [...]
}
```

### 3. 运行新网站
```bash
# 运行单个网站
python3 scripts/universal_collector.py new_site

# 运行所有网站（包括新网站）
python3 scripts/universal_collector.py --all

# 列出所有可用网站
python3 scripts/universal_collector.py --list
```

## 使用示例

### 1. 查看可用网站
```bash
python3 scripts/universal_collector.py --list
```

### 2. 运行指定网站
```bash
python3 scripts/universal_collector.py cfmem
```

### 3. 运行所有网站
```bash
python3 scripts/universal_collector.py --all
```

### 4. 运行所有网站但排除指定网站
```bash
python3 scripts/universal_collector.py --all --exclude example_site
```

### 5. 使用插件化主程序
```bash
python3 src/main_plugin.py --plugin-info
python3 src/main_plugin.py --list-sites
python3 src/main_plugin.py --sites cfmem mibei77
```

## 架构对比

### 原架构问题
- 硬编码导入：需要修改 `__init__.py` 和 `main.py`
- 重复脚本：每个网站都有独立脚本
- 配置分散：配置和类名分离
- 维护成本高：添加网站需要修改4-5个文件

### 新架构优势
- 自动发现：插件注册器自动识别新收集器
- 统一入口：一个脚本支持所有网站
- 配置驱动：通过配置文件控制一切
- 零添加成本：只需要2个文件即可添加新网站

## 最佳实践

### 1. 命名规范
- 收集器文件：`{site_key}.py`
- 收集器类：`{SiteName}Collector`
- 配置键：与文件名一致

### 2. 插件开发
- 继承 `BaseCollector` 基类
- 重写需要自定义的方法
- 使用 `self.logger` 记录日志
- 遵循现有的错误处理模式

### 3. 配置管理
- 使用 `collector_key` 指定插件
- 合理设置选择器和模式
- 默认禁用测试中的网站

### 4. 测试验证
- 先用统一脚本测试单个网站
- 确认收集器正常工作
- 再加入全量运行

## 扩展性

### 1. 新功能添加
- 在 `BaseCollector` 中添加通用方法
- 各收集器可以重写实现特定逻辑
- 保持向后兼容性

### 2. 监控和调试
- 使用 `--plugin-info` 查看插件状态
- 检查日志文件定位问题
- 单独测试有问题的网站

### 3. 性能优化
- 插件注册器缓存机制
- 并行收集支持
- 智能重试和错误恢复

## 总结

可插拔架构大大降低了新网站的开发和维护成本，实现了真正的"添加即用"。开发者只需要专注于特定网站的收集逻辑，无需关心系统架构的其他部分。