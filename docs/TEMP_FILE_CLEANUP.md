# 临时文件清理说明

## 🎯 清理目标

删除项目中的临时文件和不需要的文件，保持目录整洁。

## 📋 已删除的文件

### 1. 临时配置文件
```
result/clash_subscription.yaml
```
- **用途**: 测速过程中临时生成的Clash配置文件
- **生成原因**: subs-check工具需要从Clash格式读取节点
- **清理原因**: 测速完成后，结果已保存到nodelist.txt，此文件不再需要
- **文件大小**: 约74KB

## 🔄 文件用途说明

### 测速流程中的文件生成

```
📦 收集阶段
    ↓
📄 nodetotal.txt (收集到的所有节点)
    ↓
🔄 转换为Clash格式 (临时)
    ↓
📄 clash_subscription.yaml (临时文件) ← 已删除
    ↓
🧪 subs-check测试
    ↓
📄 nodelist.txt (测试后的有效节点)
```

### 文件作用

#### clash_subscription.yaml
- **生命周期**: 测速过程中临时存在
- **内容格式**: Clash配置格式，包含所有待测速节点
- **使用者**: subs-check工具
- **后续处理**: 测速完成后被忽略，结果保存到nodelist.txt

## ✅ 清理效果

### 优点
1. **减少目录混乱**: 删除不再需要的临时文件
2. **节省存储空间**: 释放约74KB存储
3. **避免混淆**: 用户不会误使用临时文件
4. **保持简洁**: result目录只保留最终结果文件

### 保留的文件

#### result/目录结构
```
result/
├── nodetotal.txt          # 收集完成的所有节点
├── nodelist.txt           # 测速后的有效节点
├── {date}/               # 按日期归档
│   ├── nodetotal.txt     # 历史收集节点
│   ├── nodelist.txt      # 历史测速节点
│   └── *_info.txt       # 网站信息文件
└── (已删除) clash_subscription.yaml
```

## 🔧 相关代码说明

### 测速脚本中的文件处理

#### 转换阶段
```python
# src/cli/utils/convert_nodes_to_subscription.py
# 将V2Ray节点转换为Clash格式，输出到clash_subscription.yaml
python3 -m src.cli.utils.convert_nodes_to_subscription \
    --input result/nodetotal.txt \
    --output result/clash_subscription.yaml
```

#### 测速阶段
```bash
# 启动HTTP服务器提供clash_subscription.yaml
python3 -m src.cli.utils.progress_server \
    --port 8888 \
    --file result/clash_subscription.yaml

# subs-check读取并测试
./tools/subscheck/bin/subs-check \
    -config tools/subscheck/config/config.yaml
```

#### 结果保存
```python
# 测速完成后，结果保存到nodelist.txt
# clash_subscription.yaml不再需要
```

## 📈 最佳实践

### 1. 自动清理
- 测速脚本完成后自动删除临时文件
- GitHub Actions工作流不包含临时文件

### 2. 用户指南
- 用户应使用`nodetotal.txt`(收集阶段)或`nodelist.txt`(测速阶段)
- 不应手动使用`clash_subscription.yaml`

### 3. 存储管理
- 定期清理旧的临时文件
- 保留重要的历史记录

## 🎯 总结

- **已清理**: `result/clash_subscription.yaml`临时文件
- **文件用途**: 测速过程中的临时Clash配置
- **清理理由**: 测速完成，结果已保存，不再需要临时文件
- **效果**: 保持result目录简洁，只保留有用的最终文件

---

*临时文件清理完成，项目目录更加整洁。*