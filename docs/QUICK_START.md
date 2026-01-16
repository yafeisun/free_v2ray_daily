# V2Ray节点收集器 - 快速使用指南

## 🚀 **问题修复说明**

### ✅ 已修复的问题
1. **订阅链接检测**: 修复了米贝节点等收集器的V2Ray订阅链接检测问题
2. **网站信息文件**: 现在所有网站都能正确生成 `*_info.txt` 文件
3. **节点汇总**: 所有订阅链接获取的节点都正确汇总到 `nodetotal.txt`

### 🎯 最新验证结果 (2026-01-15)
```
📊 成功收集统计:
 • 总收集时间: 242.69秒
 • 原始节点数: 2,234
 • 去重后节点数: 2,234
 • V2Ray订阅链接数: 14个
 • 网站信息文件: 14个
 • 节点总文件: nodetotal.txt (2,234个节点)
```

### 📁 文件生成说明
每天运行后会在 `result/YYYYMMDD/` 目录下生成：
- **14个 `*_info.txt` 文件** (每个网站一个)
- **1个 `nodetotal.txt` 文件** (所有节点汇总)
- **1个 `summary.json` 文件** (统计信息)

## 🚀 使用方法

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行收集器

**收集所有网站（推荐）**
```bash
python3 run.py
```

## 📋 其他命令

### 查看可用网站
```bash
python3 run.py list-sites
```

### 收集指定网站
```bash
python3 run.py collect freeclashnode mibei77
```

### 启用测速
```bash
python3 main.py --test
```

### 完整工作流
```bash
python3 main.py --full --validation --update-github
```

### 查看统计信息
```bash
python3 main.py --status
```



### 查看统计信息
```bash
python3 run.py show-stats
```

## 📊 支持的网站（14个）

- freeclashnode - FreeClashNode
- mibei77 - 米贝节点  
- clashnodev2ray - ClashNodeV2Ray
- proxyqueen - ProxyQueen
- wanzhuanmi - 玩转迷
- cfmem - CFMem
- clashnodecc - ClashNodeCC
- clashgithub - GitHub V2Ray
- datiya - Datiya
- telegeam - Telegeam
- oneclash - OneClash
- freev2raynode - FreeV2rayNode
- eighty_five_la - 85LA
- openproxylist - OpenProxyList

## 📁 输出文件

### 汇总模式
- `result/nodetotal.txt` - 所有节点汇总



## 🔧 高级用法

组合命令：
```bash
# 收集并查看统计
python3 run.py collect && python3 run.py show-stats
```

服务器自动化：
```bash
# 定时任务收集所有网站
0 */6 * * * cd /path/to/v2raynode && python3 run.py
```