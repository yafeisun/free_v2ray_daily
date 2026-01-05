# Free V2Ray Daily Node Collector - iFlow CLI 项目指南

## 项目概述

这是一个自动化的V2Ray节点收集和测试系统，每日从多个免费节点网站收集最新的V2Ray节点。项目采用模块化架构，支持13个主流免费V2Ray节点网站，具备自动文章链接收集、订阅链接提取、连通性测试和GitHub自动化部署功能。

### 主要特性
- 🌐 **多网站支持**: 支持13个主流免费V2Ray节点网站
- 📰 **文章链接收集**: 自动获取每个网站最新发布的文章链接
- 🔗 **订阅链接提取**: 自动提取V2Ray订阅链接，支持Base64解码
- 🧪 **连通性测试**: 自动测试节点可用性，丢弃超时节点
- 🌍 **多地区节点**: 包含香港、美国、欧洲等多个地区的节点
- 📁 **统一保存**: 所有有效节点统一保存到nodelist.txt文件
- ⚡ **独立脚本**: 每个网站都有独立的收集脚本
- 🤖 **自动化**: 支持GitHub Actions自动部署

### 技术栈
- **语言**: Python 3.8+
- **网络请求**: requests库
- **HTML解析**: BeautifulSoup4 + lxml
- **版本控制**: Git + GitHub Actions
- **日志系统**: Python logging
- **数据处理**: 正则表达式 + Base64编码

## 项目架构

### 目录结构
```
free_v2ray_daily/
├── config/                 # 配置文件
│   ├── settings.py        # 项目设置和路径配置
│   └── websites.py        # 网站配置信息（13个网站）
├── src/                    # 源代码
│   ├── collectors/        # 网站收集器（13个专用收集器）
│   │   ├── base_collector.py      # 基础收集器抽象类
│   │   └── {网站名称}.py          # 各网站专用收集器
│   ├── parsers/           # 解析器模块
│   ├── testers/           # 测试工具
│   │   └── connectivity_tester.py  # 连通性测试器
│   └── utils/             # 工具类
│       ├── logger.py      # 日志工具
│       ├── file_handler.py # 文件处理工具
│       └── region_detector.py # 区域检测工具
├── scripts/               # 独立脚本
│   ├── {网站名称}.py      # 各网站独立脚本
│   └── run_all_sites.py   # 批量运行脚本
├── result/                # 结果文件
│   └── nodelist.txt       # 所有有效节点
├── tests/                 # 测试文件
├── docs/                  # 文档
├── .github/workflows/     # GitHub Actions配置
│   └── update_nodes.yml   # 自动更新工作流
├── run.py                 # 主程序入口
└── requirements.txt       # 依赖包
```

## 构建和运行

### 环境要求
- Python 3.8+
- 网络连接
- Git（用于自动化部署）

### 代理配置（重要）
某些网站需要通过代理才能访问，如果遇到网络连接问题，请按以下步骤配置代理：

#### 1. 检查代理服务器
确保您的代理服务器正在运行，常见的代理地址：
- HTTP代理：`http://127.0.0.1:10808/`
- SOCKS代理：`socks://127.0.0.1:10808/`

#### 2. 配置环境变量
将以下配置添加到您的shell配置文件（`~/.zshrc` 或 `~/.bashrc`）：

```bash
# 代理设置
export http_proxy=http://127.0.0.1:10808/
export https_proxy=http://127.0.0.1:10808/
export HTTP_PROXY=http://127.0.0.1:10808/
export HTTPS_PROXY=http://127.0.0.1:10808/
export ALL_PROXY=socks://127.0.0.1:10808/
export no_proxy=localhost,127.0.0.0/8,::1
export NO_PROXY=localhost,127.0.0.0/8,::1
export FTP_PROXY=http://127.0.0.1:10808/
export ftp_proxy=http://127.0.0.1:10808/
```

#### 3. 重新加载环境变量
```bash
# 对于zsh
source ~/.zshrc

# 对于bash
source ~/.bashrc
```

#### 4. VSCode用户特别注意
如果您使用VSCode，在配置完环境变量后需要：
1. **完全关闭VSCode**（不是仅关闭窗口）
2. **重新打开VSCode**
3. **重新打开终端**

#### 5. 验证代理配置
```bash
# 检查环境变量
env | grep -i proxy

# 运行测试脚本
python3 -c "
import os
for key in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
    print(f'{key}: {repr(os.getenv(key))}')
"
```

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行方式

#### 1. 运行所有网站（推荐）
```bash
python3 run.py
```

#### 2. 运行指定网站
```bash
python3 run.py --sites {网站名称1} {网站名称2}
```

#### 3. 跳过连通性测试
```bash
python3 run.py --no-test
```

#### 4. 运行独立脚本
```bash
# 运行单个网站脚本
python3 scripts/{网站名称}.py

# 批量运行所有网站
python3 scripts/run_all_sites.py
```

#### 5. 更新GitHub仓库
```bash
python3 run.py --update-github
```

### 命令行参数
- `--sites`: 指定要运行的网站（多个网站用空格分隔）
- `--no-test`: 跳过连通性测试
- `--update-github`: 自动更新GitHub仓库
- `--date`: 指定日期（格式：YYYY-MM-DD）
- `--days`: 获取最近N天的数据

### 代理状态验证
运行脚本时，查看日志输出：
- ✅ 正常：`使用系统代理: {'http': 'http://127.0.0.1:10808/', 'https': 'http://127.0.0.1:10808/'}`
- ❌ 异常：`禁用代理设置`

## 开发约定

### 代码结构
1. **继承模式**: 所有网站收集器都继承自`BaseCollector`抽象类
2. **模块化设计**: 每个网站都有独立的收集器类和脚本
3. **配置驱动**: 网站配置统一管理在`config/websites.py`中
4. **日志规范**: 使用统一的日志格式和级别

### 添加新网站
1. 在`src/collectors/`中创建新的收集器类
2. 继承`BaseCollector`类，实现必要方法：
   - `get_latest_article_url()`: 获取最新文章URL
   - `get_nodes_from_subscription()`: 从订阅链接获取节点（可选）
   - `find_subscription_links()`: 查找订阅链接（可选）
3. 在`config/websites.py`中添加网站配置
4. 在`src/main.py`中注册新收集器
5. 创建对应的独立脚本文件

### 节点协议支持
项目支持以下V2Ray协议：
- vmess://
- vless://
- trojan://
- hysteria://
- hysteria2://
- ss://
- ssr://

### 错误处理
- 网络请求超时：自动重试3次
- SSL证书验证：默认禁用（适用于某些网站）
- 节点解析失败：记录警告日志，继续处理其他节点
- Base64解码：支持自动检测和修复填充字符

### 测试规范
- 每个收集器都应该有对应的独立脚本
- 使用`python3 scripts/run_all_sites.py`进行批量测试
- 检查`result/`目录下的输出文件
- 验证节点数量和格式正确性

## 配置管理

### 主要配置文件

#### `config/settings.py`
- 项目路径配置
- 网络请求参数（超时、重试、延迟）
- 日志配置
- 节点协议配置
- 性能参数

#### `config/websites.py`
- 13个目标网站的详细配置
- 每个网站的URL、选择器、匹配模式
- 节点解析模式
- 订阅链接过滤规则

### 环境变量
- `DEBUG`: 调试模式开关
- `DATABASE_URL`: 数据库连接URL（可选）
- `GIT_EMAIL`: Git提交邮箱
- `GIT_NAME`: Git提交用户名

## 自动化部署

### GitHub Actions
项目配置了完整的CI/CD流程：

1. **触发条件**：
   - 每日北京时间早上8点（UTC 0点）自动运行
   - 支持手动触发

2. **执行流程**：
   - 检出代码
   - 安装Python依赖
   - 运行节点收集器
   - 检查文件变更
   - 自动提交并推送更新
   - 生成运行摘要

3. **输出文件**：
   - `nodelist.txt`: 所有有效节点
   - 自动提交到GitHub仓库

### 手动部署
```bash
# 克隆仓库
git clone https://github.com/yourusername/free_v2ray_daily.git
cd free_v2ray_daily

# 安装依赖
pip install -r requirements.txt

# 运行收集器
python3 run.py --update-github
```

## 使用说明

### 输出文件

#### `result/webpage.txt`
包含各网站最新发布的文章链接，按网站分组显示。

#### `result/subscription.txt`
包含所有V2Ray订阅链接，支持多种格式（.txt、.yaml、.json）。

#### `result/nodelist.txt`
包含经过连通性测试的有效节点，可直接用于V2Ray客户端。

### 订阅链接使用

1. **直接使用节点文件**：
   ```bash
   # 获取节点文件
   curl https://raw.githubusercontent.com/yourusername/free_v2ray_daily/main/result/nodelist.txt
   ```

2. **通过订阅转换服务**：
   - 将节点文件内容进行Base64编码
   - 使用订阅转换服务（如sub.xeton.dev、sub.id9.cc）
   - 生成标准订阅链接

3. **客户端导入**：
   - 支持直接导入节点文件
   - 支持订阅链接自动更新

## 故障排除

### 代理相关问题

#### 1. VSCode中显示"禁用代理设置"
**问题**: 在终端中代理正常工作，但在VSCode中显示"禁用代理设置"
**原因**: VSCode启动时没有继承shell环境变量
**解决**: 
- 将代理配置写入shell配置文件（如 ~/.zshrc）
- 完全重启VSCode（不是仅关闭窗口）
- 重新打开终端验证环境变量

#### 2. 环境变量检测失败
**问题**: 代理环境变量设置正确但检测失败
**原因**: 代码只检查小写环境变量
**解决**: 系统已修复，现在同时检查大小写环境变量

#### 3. 网站连接超时
**问题**: 某些网站连接超时或SSL错误
**原因**: 网站需要代理访问但直接连接失败
**解决**: 
- 确认代理服务器正在运行
- 系统会自动尝试直接连接作为回退
- 检查目标网站是否需要特定代理

### 常见问题

1. **网站访问失败**：
   - 检查网络连接和代理设置
   - 查看日志文件（`data/logs/`）
   - 确认网站URL有效性

2. **节点数量为0**：
   - 检查网站文章链接是否正确获取
   - 验证订阅链接是否有效
   - 查看Base64解码是否成功

3. **GitHub Actions失败**：
   - 检查工作流配置
   - 验证GitHub令牌权限
   - 查看Actions日志

### 调试模式
```bash
# 启用调试模式
export DEBUG=true
python3 run.py --sites freeclashnode
```

### 日志查看
```bash
# 查看当日日志
tail -f data/logs/collector_$(date +%Y%m%d).log

# 查看完整日志
cat data/logs/collector_$(date +%Y%m%d).log
```

### 代理测试工具
```bash
# 测试代理连接
python3 -c "
import requests
proxies = {'http': 'http://127.0.0.1:10808/', 'https': 'http://127.0.0.1:10808/'}
try:
    response = requests.get('https://www.google.com', proxies=proxies, timeout=10)
    print('代理连接成功')
except Exception as e:
    print(f'代理连接失败: {e}')
"
```

## 性能优化

### 并发处理
- 最大并发测试线程数：10
- 请求间隔：2秒
- 连接超时：5秒

### 缓存机制
- 文件缓存时间：3600秒
- 批处理大小：100个节点

### 资源管理
- 自动清理旧备份文件
- 智能重试机制
- 内存使用优化

## 安全考虑

### 隐私保护
- 不收集用户个人信息
- 仅收集公开可用的节点信息
- 支持使用代理访问

### 网络安全
- 禁用SSL证书验证（仅用于目标网站）
- 设置合理的请求超时
- 限制并发请求数量

## 许可证和贡献

- 许可证：MIT License
- 欢迎提交Issue和Pull Request
- 请遵循现有代码风格和约定
- 添加新功能时请更新相关文档

## 更新日志

- **v2.2.0**: 修复代理配置问题，支持大小写环境变量检测，添加自动回退机制
- **v2.1.0**: 新增ClashNodeCC支持，修复Base64解码问题
- **v2.0.0**: 重构项目结构，添加文章链接收集功能
- **v1.0.0**: 初始版本，支持基本的节点收集和测试

## 代理配置改进

### v2.2.0 主要改进

1. **环境变量检测增强**
   - 同时支持大小写环境变量（http_proxy/HTTP_PROXY）
   - 提高代理检测的兼容性

2. **自动回退机制**
   - 代理连接失败时自动切换到直接连接
   - 提高网络连接的稳定性

3. **VSCode兼容性**
   - 提供完整的VSCode环境配置指南
   - 解决VSCode环境变量继承问题

4. **SSL验证统一**
   - 统一SSL验证设置，避免连接冲突
   - 适配不同网站的SSL要求

5. **详细文档**
   - 新增代理配置故障排除指南
   - 提供完整的调试和验证方法