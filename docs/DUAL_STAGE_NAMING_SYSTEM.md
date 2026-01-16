# 节点双阶段命名系统说明

## 🎯 设计目标

实现双阶段节点命名系统，在不同阶段使用不同的命名格式：
- **收集阶段**：简单命名，保存到`nodetotal.txt`
- **测速阶段**：复杂命名，保存到`nodelist.txt`

## 📋 命名格式对比

### 🔍 收集阶段 (nodetotal.txt)

#### 命名格式
```
{国旗}{区域}_{数字}
```

#### 示例
```
🇺🇸US_1
🇭🇰HK_1
🇯🇵JP_1
🇺🇸US_2
🇭🇰HK_2
```

#### 特点
- ✅ 简洁明了
- ✅ 自然数编号
- ✅ 无网站信息
- ✅ 每个地区独立计数

### 🧪 测速阶段 (nodelist.txt)

#### 命名格式
```
{国旗}{区域}_{数字}|{AI标记}{YouTube标记}
```

#### 示例
```
🇺🇸US_1|GPT|YT
🇭🇰HK_3|GPT
🇯🇵JP_2|GM|YT
🇺🇸US_4|GPT|GM
🇭🇰HK_5|GM
```

#### 特点
- ✅ 包含测试结果信息
- ✅ AI可用性标记 (GPT, GM, GPT|GM)
- ✅ YouTube解锁标记 (|YT)
- ✅ 便于筛选高质量节点

## 🔧 技术实现

### 收集阶段实现

#### 文件位置
```
src/main.py
```

#### 核心方法

##### 1. 地区提取方法
```python
def _extract_region_for_collection(self, node: str) -> str:
    """从节点中提取地区信息（收集阶段使用）"""
    # 基于端口范围判断地区
    if 10000 <= port <= 19999:
        return "US"  # 美国常用端口范围
    elif 20000 <= port <= 29999:
        return "HK"  # 香港常用端口范围
    elif 30000 <= port <= 39999:
        return "JP"  # 日本常用端口范围
    # ... 更多地区判断
```

##### 2. 简单命名生成
```python
def _generate_simple_node_name(self, region: str, number: int) -> str:
    """生成简单节点名称（收集阶段使用）"""
    flags = {"HK": "🇭🇰", "US": "🇺🇸", "JP": "🇯🇵", ...}
    flag = flags.get(region, "🇺🇸")
    return f"{flag}{region}_{number}"
```

##### 3. 节点重命名逻辑
```python
# 为收集阶段的节点生成简单命名
named_nodes = []
region_counters = {}

for i, node in enumerate(self.all_nodes):
    region = self._extract_region_for_collection(node)
    
    if region not in region_counters:
        region_counters[region] = 0
    
    region_counters[region] += 1
    region_number = region_counters[region]
    
    simple_name = self._generate_simple_node_name(region, region_number)
    
    # 添加名称到节点
    if "#" in node:
        node_with_name = node.rsplit("#", 1)[0] + f"#{simple_name}"
    else:
        node_with_name = f"{node}#{simple_name}"
    
    named_nodes.append(node_with_name)
```

### 测速阶段实现

#### 文件位置
```
src/cli/speedtest/test_nodes_with_subscheck.py
```

#### 核心方法

##### 1. 复杂命名生成
```python
def _generate_node_name(self, region: str, number: int, media_info: dict) -> str:
    """生成节点名称 - 测速后使用复杂格式"""
    flags = {"HK": "🇭🇰", "US": "🇺🇸", "JP": "🇯🇵", ...}
    flag = flags.get(region, "")
    
    # 生成AI标记
    if media_info["gpt"] and media_info["gemini"]:
        ai_tag = "GPT|GM"
    elif media_info["gpt"]:
        ai_tag = "GPT"
    elif media_info["gemini"]:
        ai_tag = "GM"
    else:
        ai_tag = ""
    
    # 生成YouTube标记
    if media_info["youtube"]:
        if ai_tag:
            yt_tag = "|YT"
        else:
            yt_tag = "YT"
    else:
        yt_tag = ""
    
    # 组合复杂名称（测速后格式）
    return f"{flag}{region}_{number}|{ai_tag}{yt_tag}"
```

##### 2. 地区计数器
```python
# 地区计数器，确保每个地区按自然数编号
region_counters = {}

for proxy in data["proxies"]:
    region = self._extract_region(proxy)
    
    if region not in region_counters:
        region_counters[region] = 0
    
    region_counters[region] += 1
    region_number = region_counters[region]
    
    # 生成复杂名称（测速后格式）
    new_name = self._generate_node_name(region, region_number, media_info)
```

## 🔄 工作流程

### 完整流程图

```
🌐 网站收集
    ↓
📦 收集阶段 (main.py)
    ↓
🏷️ 简单命名 {国旗}{区域}_{数字}
    ↓
💾 保存到 nodetotal.txt
    ↓
🚀 提交到GitHub (收集完成)
    ↓
🧪 触发测速 (test_nodes.yml)
    ↓
📊 速度测试 + AI检测
    ↓
🏷️ 复杂命名 {国旗}{区域}_{数字}|{AI标记}{YT标记}
    ↓
💾 保存到 nodelist.txt
    ↓
🚀 提交到GitHub (测速完成)
```

### 文件对比

#### nodetotal.txt (收集阶段)
```
vmess://🇺🇸US_1#🇺🇸US_1
vmess://🇭🇰HK_1#🇭🇰HK_1
vmess://🇯🇵JP_1#🇯🇵JP_1
vmess://🇺🇸US_2#🇺🇸US_2
vmess://🇭🇰HK_2#🇭🇰HK_2
```

#### nodelist.txt (测速阶段)
```
vmess://...#🇺🇸US_1|GPT|YT
vmess://...#🇭🇰HK_3|GPT
vmess://...#🇯🇵JP_2|GM|YT
vmess://...#🇺🇸US_4|GPT|GM
vmess://...#🇭🇰HK_5|GM
```

## 📊 优势分析

### 🔍 收集阶段优势

1. **快速可用**: 用户无需等待测速即可获取新节点
2. **简单命名**: 便于快速识别和基本使用
3. **完整性**: 包含所有收集到的节点

### 🧪 测速阶段优势

1. **质量保证**: 只包含通过测试的可用节点
2. **信息丰富**: AI和YouTube解锁标记便于筛选
3. **精准选择**: 用户可根据标记选择高质量节点

### 🔄 组合优势

1. **分阶段可用**: 满足不同用户需求
2. **渐进式优化**: 先获取全部，再筛选优质
3. **历史保留**: 两个文件都保留，便于追溯

## 🎯 使用场景

### 场景1: 紧急使用
- **使用**: `nodetotal.txt`
- **原因**: 获取最新节点，不等待测速
- **选择**: 按地区和编号选择节点

### 场景2: 质量优先
- **使用**: `nodelist.txt`
- **原因**: 使用已验证的高质量节点
- **选择**: 优先选择带AI标记的节点

### 场景3: 全面覆盖
- **使用**: 两个文件结合
- **原因**: `nodetotal.txt`备用 + `nodelist.txt`主力
- **选择**: 根据需要切换使用

## 📈 总结

这个双阶段命名系统完美解决了不同阶段的需求：

1. **收集阶段**: 简单命名，快速可用，保存到`nodetotal.txt`
2. **测速阶段**: 复杂命名，信息丰富，保存到`nodelist.txt`
3. **各自独立**: 两个阶段使用不同的命名逻辑
4. **用户友好**: 满足不同使用场景的需求

---

*系统实现了在不同阶段使用不同命名格式的灵活方案。*