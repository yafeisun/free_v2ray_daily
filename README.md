# 🌐 Free V2Ray Daily Node Collector

> 每日自动收集、测试和更新免费V2Ray节点的开源工具

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-passing-brightgreen.svg)](.github/workflows)
[![Last Update](https://img.shields.io/badge/last%20update-daily-orange.svg)](https://github.com/yafeisun/v2raynode)

## 📋 目录

- [项目简介](#项目简介)
- [核心特点](#核心特点)
- [快速开始](#快速开始)
- [使用指南](#使用指南)
- [节点测试](#节点测试)
- [配置说明](#配置说明)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)

---

## 🎯 项目简介

**Free V2Ray Daily Node Collector** 是一个自动化工具，用于每日收集、测试和更新来自13个主流来源的免费V2Ray节点。项目采用插件化架构，支持并发收集、节点验证、速度测试和自动部署到GitHub。

### 应用场景

- 🌍 **网络访问**: 获取稳定的代理节点用于访问全球网络
- 🚀 **性能测试**: 测试不同地区的网络质量和延迟
- 🔬 **技术研究**: 学习V2Ray协议和节点收集技术
- 📊 **数据分析**: 分析免费节点的可用性和稳定性

---

## ✨ 核心特点

### 🚀 高效收集
- **多源并发**: 同时从13个网站收集节点
- **智能去重**: 自动去除重复节点
- **格式修复**: 修复错误编码的节点链接
- **Base64解码**: 支持Base64编码的节点提取

### ✅ 节点验证
- **连通性测试**: TCP连接测试验证节点可用性
- **速度测试**: 集成subs-check进行真实速度测试
- **流媒体解锁**: 测试Netflix、YouTube、OpenAI等服务访问能力
- **智能筛选**: 基于速度和可靠性的自动筛选

### 🏗️ 插件化架构
- **零代码添加**: 新增网站只需2个文件
- **动态加载**: 自动发现和注册收集器
- **配置驱动**: 通过配置文件控制一切
- **易于扩展**: 清晰的接口设计

### 🤖 自动化部署
- **GitHub Actions**: 每日自动收集和更新
- **定时任务**: 支持cron定时收集
- **自动提交**: 自动提交测试结果到仓库
- **状态监控**: 实时监控收集状态

### 📋 核心工作流程

**节点收集流程**：
1. 查找今日文章链接 → 获取订阅链接 → 获取节点 → 汇总
2. 去重机制：订阅链接去重 + 节点server:port去重
3. 保存到 `result/{date}/nodetotal.txt`

**线上测速流程**（node test action）：
1. 转换为Clash格式 → 两阶段测速（连通性+媒体检测）
2. 过滤标准：至少通过GPT或Gemini其中一个（2选1）
3. 节点重命名 → 保存到 `result/{date}/nodelist.txt`

---

## 📊 性能指标

| 指标 | 数值 |
|-----|------|
| 🌐 支持网站 | 13个 |
| ⚡ 平均收集时间 | ~4分钟 |
| 📦 平均节点数量 | ~2,000个/天 |
| ✅ 节点可用率 | ~60-80% |
| 🔄 更新频率 | 每日自动更新 |
| 🎯 支持协议 | vmess, vless, trojan, ss, ssr, hysteria |

---

## 🚀 快速开始

### 方式1: 直接使用订阅链接（推荐新手）

直接使用每日自动更新的订阅链接，无需本地运行。

**所有节点订阅链接**:
```
https://raw.githubusercontent.com/yafeisun/v2raynode/refs/heads/main/result/nodetotal.txt
```

**已测试有效节点订阅链接**:
```
https://raw.githubusercontent.com/yafeisun/v2raynode/refs/heads/main/result/nodelist.txt
```

#### 导入到V2Ray客户端

**V2RayN / V2RayNG**:
1. 打开客户端
2. 复制上述订阅链接
3. 在"订阅"选项中点击"从剪贴板导入"
4. 更新订阅即可

**Clash / ClashX**:
1. 打开客户端
2. 进入"Profiles"或"配置"页面
3. 点击"Download"或"New"
4. 粘贴订阅链接
5. 下载并应用配置

---

### 方式2: 本地运行收集器

#### 步骤1: 环境准备

**检查Python版本**:
```bash
python3 --version
# 需要 3.8 或更高版本
```

**克隆项目**:
```bash
git clone https://github.com/yafeisun/v2raynode.git
cd v2raynode
```

#### 步骤2: 安装依赖

```bash
# 使用pip安装所有依赖
pip install -r requirements.txt

# 验证安装
python3 -c "import requests; import bs4; print('✅ 依赖安装成功')"
```

#### 步骤3: 运行收集器

```bash
# 运行所有网站收集器
python3 run.py --collect

# 查看收集统计
python3 run.py --status

# 完整工作流（收集+测速）
python3 run.py --full
```

#### 步骤4: 使用节点

收集完成后，节点文件位于 `result/` 目录:

```bash
# 查看结果目录
ls -lh result/

# 所有收集的节点（未测试）
cat result/nodetotal.txt

# 通过测试的有效节点
cat result/nodelist.txt
```

导入节点到客户端（参考方式1）。

---

## 📖 使用指南

### 基本命令

```bash
# 查看所有可用命令
python3 run.py --help

# 显示项目状态
python3 run.py --status

# 收集所有网站节点
python3 run.py --collect

# 运行节点测速
python3 run.py --test

# 完整工作流（收集+测速）
python3 run.py --full
```

### 高级用法

#### 运行指定网站

```bash
# 只收集特定网站
python3 src/main.py --sites telegeam wanzhuanmi

# 列出所有可用网站
python3 src/main.py --list-sites
```

#### 自定义配置

编辑 `config/settings.py` 修改全局配置:

```python
# 调整超时时间
CONNECTION_TIMEOUT = 10  # 秒

# 调整并发数
MAX_WORKERS = 20

# 启用调试模式
DEBUG = True
```

#### 使用代理

如果你的网络环境需要代理访问目标网站:

```bash
# 设置代理环境变量
export http_proxy=http://127.0.0.1:10808/
export https_proxy=http://127.0.0.1:10808/

# 然后运行收集器
python3 run.py --collect
```

详细代理配置请参考: [代理故障排除指南](docs/PROXY_TROUBLESHOOTING.md)

---

## 🧪 节点测试

### 测试策略

项目使用 `subs-check` 工具进行真实的代理测试，验证节点的实际可用性。

### 测试内容

| 测试类型 | 说明 | 标准 |
|---------|------|------|
| **连通性测试** | 测试节点服务器是否可达 | TCP连接成功 |
| **速度测试** | 测试节点的实际下载速度 | ≥ 512 KB/s |
| **流媒体解锁** | 测试能否访问流媒体服务 | 见下方列表 |

### 流媒体解锁测试

支持测试以下服务:
- 📺 **YouTube**: 视频流访问
- 🎬 **Netflix**: 内容解锁
- 🤖 **OpenAI (ChatGPT)**: API访问
- 💎 **Gemini**: Google AI服务

### 测试标准

- **测试方法**: 使用 subs-check 进行真实代理测试
- **最小速度**: 512 KB/s
- **并发测试**: 同时测试20个节点
- **测试超时**: 单个节点测试超时5秒
- **最小节点数**: 保留前100个速度最快的节点

### 运行测试

```bash
# 测试所有收集的节点
python3 run.py --test

# 测试指定文件
python3 run.py --test --input result/nodetotal.txt --output result/nodelist.txt
```

### 查看测试结果

```bash
# 查看有效节点
cat result/nodelist.txt

# 查看测试日志
tail -100 data/logs/collector_$(date +%Y%m%d).log

# 查看统计信息
python3 run.py --status
```

---

## 🛠️ 配置说明

### 支持的网站

项目支持以下13个免费节点源（自动按顺序收集）:

| 序号 | 网站名称 | 网站地址 | 特点 |
|-----|---------|---------|------|
| 1 | FreeClashNode | freeclashnode.com | Clash节点 |
| 2 | 米贝节点 | mibei77.com | 中文节点 |
| 3 | ClashNodeV2Ray | clashnodev2ray.github.io | GitHub源 |
| 4 | ProxyQueen | proxyqueen.top | 代理节点 |
| 5 | 玩转迷 | wanzhuanmi.com | 综合节点 |
| 6 | CFMem | cfmem.com | Cloudflare节点 |
| 7 | ClashNodeCC | clashnode.cc | Clash节点 |
| 8 | Datiya | datiya.com | 免费节点 |
| 9 | Telegeam | telegeam.github.io | Telegram分享 |
| 10 | ClashGithub | clashgithub.com | GitHub节点 |
| 11 | OneClash | oneclash.cc | Clash节点 |
| 12 | FreeV2rayNode | freev2raynode.com | V2Ray专用 |
| 13 | 85LA | 85la.com | 综合资源 |

详细的网站配置请查看: [config/websites.py](config/websites.py)

### 启用/禁用网站

编辑 `config/websites.py`:

```python
WEBSITES = {
    "freeclashnode": {
        "name": "FreeClashNode",
        "url": "https://www.freeclashnode.com/",
        "enabled": True,  # 改为 False 可禁用
        # ... 其他配置
    },
    # ...
}
```

### 全局配置

主要配置位于 `config/settings.py`:

| 配置项 | 默认值 | 说明 |
|-------|--------|------|
| `CONNECTION_TIMEOUT` | 5 | 连接超时时间（秒） |
| `MAX_WORKERS` | 10 | 最大并发线程数 |
| `REQUEST_TIMEOUT` | 30 | 请求超时时间（秒） |
| `REQUEST_DELAY` | 2 | 请求间隔时间（秒） |
| `DEBUG` | False | 调试模式 |

---

## ❓ 常见问题

### 安装问题

<details>
<summary><b>Q1: Python版本不兼容怎么办？</b></summary>

本项目需要 Python 3.8 或更高版本。

**检查版本**:
```bash
python3 --version
```

**升级Python**:
- **Ubuntu/Debian**:
  ```bash
  sudo apt update
  sudo apt install python3.10
  ```

- **macOS**:
  ```bash
  brew install python3
  ```

- **Windows**:
  从 [python.org](https://python.org/downloads/) 下载安装
</details>

<details>
<summary><b>Q2: 依赖安装失败怎么办？</b></summary>

**问题**: `pip install -r requirements.txt` 失败

**解决方案**:
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 单独安装失败的包
pip install package_name --force-reinstall
```
</details>

### 运行问题

<details>
<summary><b>Q3: 收集节点数量为0怎么办？</b></summary>

**可能原因**:
1. 网络连接问题
2. 目标网站结构变化
3. 代理配置问题

**排查步骤**:
```bash
# 1. 检查网络连接
ping -c 3 google.com

# 2. 查看详细日志
python3 run.py --collect 2>&1 | tee collect.log

# 3. 测试单个网站
python3 src/main.py --sites telegeam

# 4. 检查网站配置
cat config/websites.py
```
</details>

<details>
<summary><b>Q4: 收集过程超时怎么办？</b></summary>

**解决方案**:
```python
# 编辑 config/settings.py
REQUEST_TIMEOUT = 60  # 增加到60秒
REQUEST_RETRY = 5    # 增加重试次数
```

或使用代理访问:
```bash
export http_proxy=http://127.0.0.1:10808/
export https_proxy=http://127.0.0.1:10808/
python3 run.py --collect
```
</details>

### 节点问题

<details>
<summary><b>Q5: 节点无法连接怎么办？</b></summary>

**可能原因**:
1. 节点已失效
2. 网络环境限制
3. 客户端配置错误

**解决方案**:
1. 使用 `nodelist.txt`（已测试的节点）
2. 检查客户端配置
3. 尝试其他节点
4. 重新运行测速:
   ```bash
   python3 run.py --test
   ```
</details>

<details>
<summary><b>Q6: 节点速度很慢怎么办？</b></summary>

**优化建议**:
1. 使用 `nodelist.txt`（已按速度排序）
2. 选择延迟低的节点
3. 使用CDN加速的节点（如CFMem）
4. 调整客户端的MTU设置
</details>

### 客户端配置

<details>
<summary><b>Q7: 如何在V2RayN中导入节点？</b></summary>

**步骤**:
1. 下载 [V2RayN](https://github.com/2dust/v2rayN/releases)
2. 打开V2RayN
3. 点击"订阅" → "从剪贴板导入订阅链接"
4. 粘贴订阅链接:
   ```
   https://raw.githubusercontent.com/yafeisun/v2raynode/refs/heads/main/result/nodelist.txt
   ```
5. 点击"更新订阅"
6. 在"服务器"列表中选择节点
7. 点击"系统代理"启用
</details>

<details>
<summary><b>Q8: 如何在ClashX中导入节点？</b></summary>

**步骤**:
1. 下载 [ClashX](https://github.com/yichengchen/clashX/releases)
2. 打开ClashX
3. 点击"Profiles" → "Download from URL"
4. 粘贴订阅链接（同上）
5. 点击"Download"
6. 选择配置文件并应用
</details>

更多常见问题请查看: [常见问题FAQ](docs/FAQ.md)

---

## 📚 文档导航

### 用户指南
- [快速开始指南](docs/QUICK_START.md) - 详细的快速上手教程
- [安装指南](docs/INSTALLATION.md) - 完整的安装步骤
- [客户端配置](docs/CLIENT_SETUP.md) - 各类客户端配置教程
- [故障排除](docs/PROXY_TROUBLESHOOTING.md) - 问题排查指南

### 开发者指南
- [项目架构](docs/ARCHITECTURE.md) - 架构设计说明
- [插件架构](docs/PLUGIN_ARCHITECTURE.md) - 插件化架构详解
- [收集器开发](docs/developer-guide/COLLECTOR_DEVELOPMENT.md) - 如何添加新网站
- [API参考](docs/developer-guide/API_REFERENCE.md) - API文档

### 技术报告
- [收集器映射](docs/COLLECTORS_MAPPING.md) - 所有收集器的详细映射
- [测速对比分析](docs/reports/测速对比分析报告.md) - 测试结果分析
- [更新日志](CHANGELOG.md) - 版本更新记录

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 如何贡献

1. **Fork项目**
   ```bash
   # 点击GitHub页面右上角的Fork按钮
   ```

2. **克隆到本地**
   ```bash
   git clone https://github.com/your-username/v2raynode.git
   cd v2raynode
   ```

3. **创建分支**
   ```bash
   git checkout -b feature/your-feature
   ```

4. **提交更改**
   ```bash
   git add .
   git commit -m "Add your feature"
   ```

5. **推送到Fork**
   ```bash
   git push origin feature/your-feature
   ```

6. **创建Pull Request**
   - 访问原始仓库
   - 点击"New Pull Request"
   - 描述你的更改

### 贡献类型

- 🐛 **Bug修复**: 修复已知问题
- ✨ **新功能**: 添加新功能
- 📝 **文档改进**: 完善文档
- 🎨 **代码优化**: 提升代码质量
- ⚡ **性能提升**: 优化性能

详细贡献指南请查看: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📜 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

```
MIT License

Copyright (c) 2026 yafeisun

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## ⚖️ 免责声明

本项目仅供**学习交流和技术研究**使用，请遵守当地法律法规。使用本项目的任何功能所产生的一切后果由使用者自行承担，项目作者不承担任何责任。

- 🔒 请勿用于任何非法用途
- 🌐 尊重网络服务提供商的使用条款
- 📚 建议仅用于技术学习和个人使用
- ⚠️ 本项目不保证节点的稳定性和可用性

---

## 🙏 致谢

感谢以下开源项目和服务：

- [V2Ray](https://www.v2ray.com/) - 优秀的网络代理工具
- [Clash](https://github.com/Dreamacro/clash) - 强大的代理内核
- [subs-check](https://github.com/lnd-db/subs-check) - 节点测试工具
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML解析库
- [Requests](https://requests.readthedocs.io/) - HTTP库

感谢所有贡献者对本项目的支持！

---

## 📮 联系方式

- **GitHub**: [yafeisun/v2raynode](https://github.com/yafeisun/v2raynode)
- **Issues**: [提交问题](https://github.com/yafeisun/v2raynode/issues)
- **Discussions**: [讨论区](https://github.com/yafeisun/v2raynode/discussions)

---

<div align="center">

**如果这个项目对你有帮助，请给个⭐️Star支持一下！**

Made with ❤️ by yafeisun

</div>
