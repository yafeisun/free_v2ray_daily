# 项目架构说明

## 🏗️ 目录结构

```
v2raynode/
├── README.md                          # 项目主文档
├── run.py                             # 项目启动入口
├── config/                            # 配置文件
│   ├── requirements.txt               # Python依赖
│   ├── settings.py                   # 项目设置
│   └── websites.py                   # 网站配置
├── src/                               # 核心源码
│   ├── collectors/                    # 节点收集器(核心)
│   ├── testers/                       # 测试器(核心)
│   ├── parsers/                       # 解析器
│   ├── core/                          # 核心功能
│   └── utils/                         # 工具函数
├── scripts/                           # 运行脚本
│   ├── collectors/                    # 🔥 节点收集脚本
│   │   ├── cfmem.py                  # Cloudflare收集器
│   │   ├── clashgithub.py            # GitHub Clashes收集器
│   │   ├── freeclashnode.py          # 免费Clash节点收集器
│   │   └── ...                       # 其他收集器
│   ├── speedtest/                     # 🔥 节点测速脚本
│   │   ├── test_nodes_with_subscheck.py  # 主测速脚本
│   │   ├── intelligent_timeout.py        # 智能超时管理
│   │   ├── speedtest_nodes.py           # 速度测试工具
│   │   └── ...                          # 其他测速工具
│   └── utils/                         # 工具脚本
│       ├── convert_nodes_to_subscription.py  # 节点转换工具
│       ├── universal_collector.py            # 通用收集器
│       └── progress_server.py                # 进度服务器
├── docs/                              # 文档目录
│   ├── reports/                       # 报告文档
│   └── summaries/                     # 总结文档
├── result/                            # 结果输出
└── subscheck/                         # subs-check工具
```

## 🔥 核心功能模块

### 1. 节点获取模块 (Collectors)

**位置**: `src/collectors/` + `scripts/collectors/`

**功能**: 从各种源获取免费V2Ray节点
- Cloudflare Workers节点
- GitHub开源节点列表  
- 免费节点网站
- Telegram频道节点

**使用方法**:
```bash
# 运行单个收集器
python3 scripts/collectors/cfmem.py

# 运行所有收集器
python3 scripts/utils/run_all_sites.py
```

### 2. 节点测速模块 (Speedtest)

**位置**: `src/testers/` + `scripts/speedtest/`

**功能**: 测试节点可用性和速度
- 连接性测试 (TCP)
- 媒体检测 (YouTube, Netflix)
- 延迟和速度测试
- 智能超时管理

**使用方法**:
```bash
# 主测速脚本 (推荐)
python3 scripts/speedtest/test_nodes_with_subscheck.py \
  --input result/nodetotal.txt \
  --output result/nodelist.txt

# 基础速度测试
python3 scripts/speedtest/speedtest_nodes.py

# 批量测试
python3 scripts/speedtest/test_nodes_batch.py
```

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r config/requirements.txt
```

### 2. 收集节点
```bash
# 方法1: 运行统一收集器
python3 scripts/utils/universal_collector.py

# 方法2: 运行所有收集器
python3 scripts/utils/run_all_sites.py
```

### 3. 测试节点
```bash
# 使用智能超时的主测速脚本
python3 scripts/speedtest/test_nodes_with_subscheck.py \
  --input result/nodetotal.txt \
  --output result/nodelist.txt
```

### 4. 查看结果
```bash
# 查看有效节点
cat result/nodelist.txt

# 查看节点统计
wc -l result/nodetotal.txt result/nodelist.txt
```

## 🔄 GitHub Actions自动执行

项目配置了自动化的GitHub Actions工作流:
- **Update Nodes**: 每12小时自动收集节点
- **Test Nodes**: 节点更新后自动测速

## 📊 性能优化

### 智能超时管理
- 动态调整超时时间
- 基于延迟和进度智能等待
- 避免误杀正常进程

### 并发控制
- 根据网络状况动态调整并发数
- 低延迟时提高并发
- 高延迟时降低并发

## 🎯 项目特点

1. **模块化设计**: 节点收集和测速分离，易于维护
2. **智能优化**: 动态超时和并发控制
3. **完整工作流**: 从收集到测试的自动化流程
4. **详细文档**: 完整的使用说明和开发文档