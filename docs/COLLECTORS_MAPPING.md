# 📡 节点收集器完整映射表

## 🎯 项目支持的13个网站及对应收集器

| 序号 | 网站名称 | 网站地址 | 收集器脚本 | 状态 | 备注 |
|------|----------|----------|------------|------|------|
| 1 | FreeClashNode | freeclashnode.com | `freeclashnode.py` | ✅ | 免费Clash节点网站 |
| 2 | 米贝节点 | mibei77.com | `mibei77.py` | ✅ | 中文节点网站 |
| 3 | ClashNodeV2Ray | clashnodev2ray.github.io | `clashnodev2ray.py` | ✅ | GitHub Pages节点 |
| 4 | ProxyQueen | proxyqueen.top | `proxyqueen.py` | ✅ | 代理节点网站 |
| 5 | 玩转迷 | wanzhuanmi.com | `wanzhuanmi.py` | ✅ | 综合节点网站 |
| 6 | CFMem | cfmem.com | `cfmem.py` | ✅ | Cloudflare节点 |
| 7 | ClashNodeCC | clashnode.cc | `clashnodecc.py` | ✅ | Clash节点网站 |
| 8 | Datiya | free.datiya.com | `datiya.py` | ✅ | 免费节点网站 |
| 9 | Telegeam | telegeam.github.io | `telegeam.py` | ✅ | Telegram节点分享 |
| 10 | ClashGithub | clashgithub.com | `clashgithub.py` | ✅ | GitHub Clash节点 |
| 11 | OneClash | oneclash.cc | `oneclash.py` | ✅ | Clash节点网站 |
| 12 | FreeV2rayNode | freev2raynode.com | `freev2raynode.py` | ✅ | V2Ray专用节点 |
| 13 | 85LA | 85la.com | `eighty_five_la.py` | ✅ | 综合网络节点 |

## 🔧 收集器架构

### 双重架构设计
```
src/collectors/     ← 核心收集器源码
├── base_collector.py    # 基础收集器类
├── freeclashnode.py     # 具体实现
└── ...               # 其他收集器

scripts/collectors/  ← 运行时收集器脚本  
├── freeclashnode.py     # 运行时脚本
└── ...               # 其他脚本
```

### 配置驱动
- **配置文件**: `config/websites.py`
- **动态加载**: 基于配置自动选择收集器
- **插件化**: 每个收集器都是独立插件

## 📊 收集器功能对比

| 收集器类型 | 协议支持 | 数据格式 | 特点 | 更新频率 |
|------------|----------|----------|------|----------|
| **CFMem** | vmess, vless, trojan | txt, sub | Cloudflare优化 | 高 |
| **ClashGithub** | vmess, vless, trojan, ss, ssr, hysteria | txt, yaml | GitHub源码 | 中 |
| **ProxyQueen** | vmess, vless, trojan, hysteria | txt | 代理专业站点 | 高 |
| **Telegeam** | vmess, vless, trojan, hysteria, ss, ssr | txt | Telegram分享 | 高 |
| **85LA** | vmess, vless, trojan | txt | 综合网络资源 | 中 |

## 🚀 使用方法

### 单个收集器运行
```bash
# 运行CFMem收集器
python3 scripts/collectors/cfmem.py

# 运行米贝收集器  
python3 scripts/collectors/mibei77.py
```

### 批量收集器运行
```bash
# 运行所有收集器
python3 scripts/utils/run_all_sites.py

# 运行通用收集器
python3 scripts/utils/universal_collector.py

# 使用统一入口
python3 main.py --collect
```

### 选择性收集
```bash
# 基于配置文件中的enabled状态
python3 -c "
from config.websites import WEBSITES
enabled_sites = [name for name, config in WEBSITES.items() if config.get('enabled')]
print(f'启用的网站: {enabled_sites}')
"
```

## 🔍 配置文件结构

每个网站配置包含：
```python
{
    "name": "网站显示名称",
    "url": "网站主页URL", 
    "enabled": True/False,          # 是否启用
    "collector_key": "收集器关键字",  # 对应脚本文件名
    "selectors": [...],             # CSS选择器列表
    "patterns": [...]               # 正则匹配模式
}
```

## 📈 统计信息

### 收集器覆盖率
- **总网站数**: 13个
- **启用网站数**: 13个 (100%)
- **收集器覆盖率**: 100% ✅

### 协议支持
- **vmess**: 13/13 (100%)
- **vless**: 13/13 (100%)  
- **trojan**: 13/13 (100%)
- **hysteria**: 8/13 (61.5%)
- **ss/ssr**: 6/13 (46.2%)

## 🎯 架构优势

1. **完整性**: 支持所有配置的13个网站
2. **一致性**: 配置与收集器一一对应
3. **可扩展**: 新增网站只需添加配置和收集器
4. **可维护**: 每个收集器独立，易于调试
5. **灵活性**: 支持启用/禁用特定网站

## ✅ 验证状态

- [x] 13个网站配置完整
- [x] 13个收集器脚本存在  
- [x] 配置与收集器一一对应
- [x] 所有收集器可正常导入
- [x] 统一入口脚本支持

**节点收集器架构完整，支持配置的13个网站！** 🎉📡