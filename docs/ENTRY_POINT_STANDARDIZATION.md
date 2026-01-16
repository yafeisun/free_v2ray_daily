# 入口文件规范化说明

## 🎯 优化目标

解决项目中的main.py文件重复问题，建立清晰的入口文件结构，确保默认收集所有网站。

## 📁 文件结构对比

### ❌ 优化前
```
free_v2ray_daily/
├── main.py              # 简单包装器，功能有限
├── src/
│   └── main.py         # 完整主程序，功能丰富
└── .github/workflows/
    └── update_nodes.yml # 使用根目录main.py
```

### ✅ 优化后
```
free_v2ray_daily/
├── collect.py           # 用户友好的入口脚本
├── src/main.py         # 完整主程序（实际逻辑）
├── scripts/
│   └── run.py          # 旧的启动脚本（保留备用）
└── .github/workflows/
    └── update_nodes.yml # 使用模块方式运行
```

## 🔧 文件说明

### 🚀 collect.py (主入口)

**用途**: 项目的统一入口点，用户友好的CLI界面

**特点**:
- ✅ 用户友好的启动信息
- ✅ 自动设置Python路径
- ✅ 简单的错误处理
- ✅ 调用真正的主程序

**代码结构**:
```python
#!/usr/bin/env python3
"""
V2Ray节点收集器 - 简单入口脚本
这是项目的统一入口点，提供用户友好的命令行界面。
实际的主程序在 src/main.py 中。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """主入口函数"""
    print("🌐 V2Ray Daily Node Collector")
    print("📍 正在启动主程序...")
    print()
    
    # 导入并运行主程序
    try:
        from src.main import main as main_program
        main_program()
    except ImportError as e:
        print(f"❌ 导入主程序失败: {e}")
        print("请确保已安装所有依赖：")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 运行程序失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 🛠️ src/main.py (主程序)

**用途**: 完整的主程序，包含所有业务逻辑

**特点**:
- ✅ 完整的节点收集逻辑
- ✅ 13个网站的收集器
- ✅ 双阶段处理（收集+去重）
- ✅ GitHub Actions集成
- ✅ 默认收集所有网站

**默认行为**:
```python
# 不带参数运行时，默认收集所有网站
python3 -m src.main

# 等同于
python3 -m src.main --sites freeclashnode mibei77 ... (所有13个网站)
```

### 🔄 scripts/run.py (备用入口)

**用途**: 旧的启动脚本，保留作为备用

**特点**:
- ✅ 简单的调用方式
- ✅ 向后兼容
- ✅ 可作为备用方案

## 📋 使用方式

### 推荐方式 (使用collect.py)

```bash
# 用户友好的入口（推荐）
python3 collect.py

# 等价于模块运行
python3 -m src.main
```

### 直接模块方式

```bash
# 直接运行主程序
python3 -m src.main

# 运行特定网站
python3 -m src.main --sites freeclashnode mibei77

# 查看帮助
python3 -m src.main --help
```

### GitHub Actions方式

```yaml
# 使用模块方式（已更新）
- name: Run node collector
  run: |
    python3 -m src.main --collect
```

## 🎯 默认行为确认

### ✅ 默认收集所有网站

当不提供`--sites`参数时，程序默认：

1. **启用所有13个网站**:
   - freeclashnode
   - mibei77
   - clashnodev2ray
   - proxyqueen
   - wanzhuanmi
   - cfmem
   - clashnodecc
   - datiya
   - telegeam
   - clashgithub
   - freev2raynode
   - oneclash
   - 85la

2. **输出详细日志**:
   ```
   [INFO] 运行所有网站
   [INFO] 开始收集 freeclashnode 的节点...
   [INFO] 开始收集 mibei77 的节点...
   ...
   ```

3. **生成完整结果**:
   - `result/nodetotal.txt` (所有收集到的节点)
   - `result/{date}/nodetotal.txt` (按日期归档)

### 📊 参数支持

```bash
# 收集所有网站（默认）
python3 collect.py

# 收集特定网站
python3 collect.py --sites freeclashnode mibei77

# 收集特定日期的数据
python3 collect.py --date 2026-01-15

# 收集最近几天的数据
python3 collect.py --days 7

# 收集并提交到GitHub
python3 collect.py --update-github
```

## ✅ 优化效果

### 1. 解决文件重复
- ❌ **删除**: 根目录的重复`main.py`
- ✅ **保留**: `src/main.py`作为唯一的真正主程序
- ✅ **新增**: `collect.py`作为用户友好的入口

### 2. 统一入口方式
- ✅ **用户使用**: `python3 collect.py`
- ✅ **GitHub Actions**: `python3 -m src.main`
- ✅ **开发调试**: `python3 -m src.main`

### 3. 保持功能完整
- ✅ **默认行为**: 默认收集所有13个网站
- ✅ **参数支持**: 支持所有原有的命令行参数
- ✅ **向后兼容**: 旧的脚本仍然可用

### 4. 提升用户体验
- ✅ **清晰的启动信息**: 用户知道程序正在启动
- ✅ **友好的错误提示**: 依赖问题和运行错误
- ✅ **一致的路径处理**: 自动设置Python路径

## 🔄 迁移指南

### 对于用户
```bash
# 旧方式（不再推荐）
python3 main.py

# 新方式（推荐）
python3 collect.py

# 或者直接使用模块
python3 -m src.main
```

### 对于开发者
```python
# 直接运行主程序
python3 -m src.main --sites freeclashnode

# 调试模式
python3 -m src.main --sites telegeam --debug
```

### 对于CI/CD
```yaml
# GitHub Actions（已更新）
- name: Run collector
  run: python3 -m src.main --collect
```

## 📈 项目结构优势

1. **清晰的职责分离**:
   - `collect.py`: 用户入口
   - `src/main.py`: 业务逻辑
   - `scripts/`: 辅助工具

2. **易于维护**:
   - 主要逻辑集中在`src/main.py`
   - 入口脚本简单明了
   - 减少文件混乱

3. **用户友好**:
   - 简单的启动命令
   - 清晰的错误信息
   - 默认收集所有网站

4. **开发友好**:
   - 模块化结构便于测试
   - 清晰的Python路径
   - 保持完整的参数支持

---

*入口文件规范化完成，项目结构更加清晰，默认收集所有网站！*