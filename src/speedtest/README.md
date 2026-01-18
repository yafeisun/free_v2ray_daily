# SpeedTest 测速工具

## 📁 目录结构

```
src/speedtest/
├── test_nodes_with_subscheck.py    # 主要测速脚本（使用subscheck）
├── intelligent_timeout.py          # 智能超时管理
├── test_nodes_batch.py             # 批量测试
├── test_nodes.py                   # 单节点测试
├── test_smart_timeout.py           # 智能超时测试
├── simple_timeout_test.py          # 简单超时测试
├── intelligent_timeout_fixed.py    # 修复版智能超时
├── run_collector.py                # 运行收集器
└── speedtest_nodes.py              # 节点测速
```

## 🚀 使用方法

### 使用subscheck进行测速

```bash
# 运行主要的测速脚本
python3 src/speedtest/test_nodes_with_subscheck.py
```

### 批量测试

```bash
# 批量测试节点
python3 src/speedtest/test_nodes_batch.py
```

## 📋 功能特性

- **多种测速方式**：
  - subscheck（推荐）：专业的代理测速工具
  - 内置TCP测试：简单的连通性测试
  - 媒体流测试：Netflix、YouTube等

- **智能超时管理**：根据网络状况动态调整超时时间
- **批量处理**：支持大量节点的并发测试
- **性能监控**：实时监控测试进度和性能指标
- **结果分析**：生成详细的测试报告和统计信息

## ⚙️ 配置说明

### 主要配置项

- **测试超时**：默认30秒，可根据网络调整
- **并发数量**：默认根据CPU核心数自动调整
- **测速服务器**：支持自定义测速服务器列表
- **输出格式**：支持JSON、YAML等多种格式

### 智能超时参数

```python
# 在intelligent_timeout.py中配置
TIMEOUT_BASE = 10          # 基础超时时间
TIMEOUT_MULTIPLIER = 2     # 超时倍数
MAX_TIMEOUT = 60          # 最大超时时间
```

## 🔧 集成说明

### GitHub Actions

```yaml
- name: 节点测速
  run: |
    python3 src/speedtest/test_nodes_with_subscheck.py
```

### 本地运行

```bash
# 确保subscheck已安装
python3 tools/subscheck/bin/download_subscheck.py

# 运行测速
python3 src/speedtest/test_nodes_with_subscheck.py
```

## 📊 输出结果

测速完成后会生成：
- `result/speedtest_results.json` - 详细测速结果
- `result/filtered_nodes.txt` - 筛选后的优质节点
- `result/speedtest_report.md` - 测速报告