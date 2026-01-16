# GitHub Actions 工作流优化说明

## 🎯 优化目标

将节点收集和测速流程分离，确保收集完成后立即提交`nodetotal.txt`，然后触发测速工作流处理`nodelist.txt`。

## 📋 修改内容

### 1. update_nodes.yml (收集工作流)

#### ✨ 新增功能
- **分离检查逻辑**: 将文件检查分为收集和测速两个独立阶段
- **收集完成提交**: 只在收集有更新时提交`result/nodetotal.txt`
- **自动触发测速**: 收集成功后自动触发`test_nodes.yml`工作流
- **详细摘要**: 区分收集状态和测速触发状态

#### 🔧 修改详情
```yaml
# 新增检查步骤
- name: Check for collection changes
  id: collection_changes
  # 检查nodetotal.txt变更

# 新增提交步骤
- name: Commit nodetotal.txt (collection complete)
  if: steps.collection_changes.outputs.has_nodetotal_changes == 'true'

# 新增触发步骤
- name: Trigger speed test workflow
  if: steps.collection_changes.outputs.has_nodetotal_changes == 'true' && steps.collector.outcome == 'success'
```

### 2. test_nodes.yml (测速工作流)

#### ✨ 新增功能
- **触发来源识别**: 支持收集工作流触发的参数传递
- **工作流输入**: 添加`trigger_collection`、`collection_commit`、`total_nodes`输入
- **摘要增强**: 显示触发来源和收集统计信息

#### 🔧 修改详情
```yaml
workflow_dispatch:
  inputs:
    trigger_collection:
      description: '是否由收集工作流触发'
      type: boolean
    collection_commit:
      description: '收集工作流的提交SHA'
      type: string
    total_nodes:
      description: '收集到的总节点数'
      type: string
```

## 🔄 工作流程

### 新的工作流程

```
📦 收集阶段 (update_nodes.yml)
    ↓
1. 收集13个网站节点
    ↓
2. 生成 result/nodetotal.txt
    ↓
3. 检查是否有更新
    ↓
4. 提交 nodetotal.txt ✅
    ↓
5. 自动触发测速工作流 🚀

🧪 测速阶段 (test_nodes.yml)
    ↓
1. 读取 nodetotal.txt
    ↓
2. 转换为Clash格式
    ↓
3. 执行两阶段测速
    ↓
4. 生成 result/nodelist.txt
    ↓
5. 提交 nodelist.txt ✅
```

### 触发条件

| 触发方式 | 提交文件 | 后续动作 |
|---------|---------|---------|
| 定时收集 | nodetotal.txt | 自动触发测速 |
| 手动收集 | nodetotal.txt | 自动触发测速 |
| 定时测速 | nodelist.txt | 无 |
| 手动测速 | nodelist.txt | 无 |

## 📊 优势

### ✅ 流程清晰
- 收集和测速完全分离
- 每个阶段职责明确
- 易于调试和维护

### ✅ 实时性
- 收集完成后立即可用
- 无需等待测速完成
- 用户可以更快获取新节点

### ✅ 错误隔离
- 收集失败不影响测速
- 测速失败不影响收集
- 独立的错误处理

### ✅ 可追溯性
- 清晰的提交信息
- 区分收集和测速状态
- 完整的工作流日志

## 🚦 提交信息格式

### 收集提交
```
Collect nodes - 2026-01-16 22:30:00 (2234 total nodes)
```

### 测速提交
```
Test nodes - 2026-01-16 23:45:00 (1567 valid nodes)
```

## 📈 监控和日志

### GitHub Actions 摘要
- **收集摘要**: 显示总节点数和触发状态
- **测速摘要**: 显示有效节点数和触发来源

### 工作流关联
- 收集工作流完成后自动触发测速
- 保留工作流间的关联信息
- 便于问题追踪和调试

---

这些优化确保了节点收集完成后立即提交，同时保持了完整的工作流自动化。