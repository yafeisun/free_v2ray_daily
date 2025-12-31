# 免费V2Ray节点收集器

一个自动化的V2Ray节点收集和测试系统，每日从多个免费节点网站收集最新的V2Ray节点。

## 功能特性

- 🌐 **多网站支持**: 支持6个主流免费V2Ray节点网站
- 📰 **文章链接收集**: 自动获取每个网站最新发布的文章链接
- 🔗 **订阅链接提取**: 自动提取V2Ray订阅链接（过滤Clash/Sing-box）
- 🔄 **订阅转换支持**: 支持通过第三方服务将节点文件转换为标准订阅链接
- 🧪 **连通性测试**: 自动测试节点可用性，丢弃超时节点
- 🌍 **多地区节点**: 包含香港、美国、欧洲等多个地区的节点
- 📁 **统一保存**: 所有有效节点统一保存到nodelist.txt文件
- ⚡ **独立脚本**: 每个网站都有独立的收集脚本
- 🤖 **自动化**: 支持GitHub Actions自动部署

## 支持的网站

1. [FreeClashNode](https://www.freeclashnode.com/free-node/)
2. [米贝77](https://www.mibei77.com/)
3. [ClashNodeV2Ray](https://clashnodev2ray.github.io/)
4. [ProxyQueen](https://www.proxyqueen.top/)
5. [玩转迷](https://wanzhuanmi.com/)
6. [CFMem](https://www.cfmem.com/)

## 项目结构

```
free_v2ray_daily/
├── config/                 # 配置文件
│   ├── settings.py        # 项目设置和路径配置
│   └── websites.py        # 网站配置信息
├── src/                    # 源代码
│   ├── collectors/        # 网站收集器
│   ├── parsers/           # 解析器
│   ├── testers/           # 测试工具
│   └── utils/             # 工具类
├── scripts/               # 独立脚本
│   ├── freeclashnode.py   # FreeClashNode独立脚本
│   ├── mibei77.py         # 米贝77独立脚本
│   ├── clashnodev2ray.py  # ClashNodeV2Ray独立脚本
│   ├── proxyqueen.py      # ProxyQueen独立脚本
│   ├── wanzhuanmi.py      # 玩转迷独立脚本
│   ├── cfmem.py           # CFMem独立脚本
│   ├── clashnodecc.py     # ClashNodeCC独立脚本
│   └── run_all_sites.py   # 批量运行脚本
├── result/                # 结果文件
│   ├── 20251224/          # 按日期分文件夹（本地存储，不提交到GitHub）
│   │   ├── webpage.txt    # 2025-12-24的文章链接
│   │   ├── subscription.txt # 2025-12-24的订阅链接
│   │   └── nodelist.txt   # 2025-12-24的有效节点
│   ├── 20251223/          # 按日期分文件夹（本地存储，不提交到GitHub）
│   │   ├── webpage.txt    # 2025-12-23的文章链接
│   │   ├── subscription.txt # 2025-12-23的订阅链接
│   │   └── nodelist.txt   # 2025-12-23的有效节点
│   ├── webpage.txt        # 最新文章链接（兼容性）
│   ├── subscription.txt   # V2Ray订阅链接（兼容性）
│   └── nodelist.txt       # 所有有效节点（兼容性，提交到GitHub）
├── tests/                 # 测试文件
├── docs/                  # 文档
├── .github/workflows/     # GitHub Actions配置
├── run.py                 # 主程序入口
└── requirements.txt       # 依赖包
```

## 安装和使用

### 1. 环境要求

- Python 3.8+
- 网络连接

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 代理配置（重要）

某些网站需要通过代理才能访问，如果遇到网络连接问题，请按以下步骤配置代理：

#### 3.1 检查代理服务器
确保您的代理服务器正在运行，常见的代理地址：
- HTTP代理：`http://127.0.0.1:10808/`
- SOCKS代理：`socks://127.0.0.1:10808/`

#### 3.2 配置环境变量
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

#### 3.3 重新加载环境变量
```bash
# 对于zsh
source ~/.zshrc

# 对于bash
source ~/.bashrc
```

#### 3.4 验证代理配置
```bash
# 检查环境变量
env | grep -i proxy

# 测试网络连接
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

#### 3.5 VSCode用户特别注意
如果您使用VSCode，在配置完环境变量后需要：
1. **完全关闭VSCode**（不是仅关闭窗口）
2. **重新打开VSCode**
3. **重新打开终端**
4. 验证环境变量是否正确加载

#### 3.6 临时禁用代理
如果需要临时禁用代理：
```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY
```

### 4. 代理故障排除

如果遇到代理相关问题，请参考：[代理配置故障排除指南](docs/PROXY_TROUBLESHOOTING.md)

### 5. 运行方式

#### 运行所有网站
```bash
python3 run.py
```

#### 运行指定网站
```bash
python3 run.py --sites freeclashnode mibei77
```

#### 跳过连通性测试
```bash
python3 run.py --no-test
```

#### 运行独立脚本
```bash
python3 scripts/freeclashnode.py
python3 scripts/run_all_sites.py
```

#### 验证代理是否正常工作
运行脚本时，查看日志输出：
- ✅ 正常：`使用系统代理: {'http': 'http://127.0.0.1:10808/', 'https': 'http://127.0.0.1:10808/'}`
- ❌ 异常：`禁用代理设置`

## 输出文件说明

**重要说明**：
- 带日期格式的文件夹（如 `result/20251224/`）仅在本地存储，**不会提交到GitHub**
- 根目录的 `result/nodelist.txt` 会提交到GitHub，作为最新数据源
- 推荐订阅链接：`https://raw.githubusercontent.com/yafeisun/free_v2ray_daily/refs/heads/main/result/nodelist.txt`

### 按日期分文件夹结构（本地存储）
系统现在支持按日期自动分文件夹保存数据，避免重复执行：

```
result/
├── 20251224/              # 2025-12-24的数据
│   ├── webpage.txt      # 当天所有网站的文章链接
│   ├── subscription.txt # 当天所有网站的订阅链接
│   └── nodelist.txt      # 当天收集的有效节点
├── 20251223/              # 2025-12-23的数据
│   ├── webpage.txt      # 当天所有网站的文章链接
│   ├── subscription.txt # 当天所有网站的订阅链接
│   └── nodelist.txt      # 当天收集的有效节点
└── ...                   # 其他日期的数据
```

### `result/YYYYMMDD/webpage.txt`
包含指定日期各网站最新发布的文章链接，格式：
```
# 各网站最新文章链接
# 收集时间: 2025-12-24 14:30:15
# 目标日期: 20251224
# 总网站数: 7
================================================================================

# freeclashnode
https://www.freeclashnode.com/free-node/2025-12-24-free-clash-subscribe.htm

------------------------------------------------------------
# 米贝节点
https://www.mibei77.com/2025/12/20251224172-1080p4k-v2rayclash-vpn.html

------------------------------------------------------------
```

### `result/YYYYMMDD/subscription.txt`
包含指定日期所有V2Ray订阅链接，格式：
```
# V2Ray订阅链接收集结果
# 收集时间: 2025-12-24 14:30:15
# 目标日期: 20251224
# 总链接数: 12
================================================================================

# freeclashnode
# 文章链接: https://www.freeclashnode.com/free-node/2025-12-24-free-clash-subscribe.htm
# 链接数: 2
https://node.freeclashnode.com/uploads/2025/12/4-20251224.txt
https://node.freeclashnode.com/uploads/2025/12/1-20251224.txt

------------------------------------------------------------
# 米贝节点
# 文章链接: https://www.mibei77.com/2025/12/20251224172-1080p4k-v2rayclash-vpn.html
# 链接数: 1
https://mm.mibei77.com/2025.12/12.2464bafrg.txt

------------------------------------------------------------
```

### `result/YYYYMMDD/nodelist.txt`
包含指定日期经过连通性测试的有效节点，包括香港、美国、欧洲等各地区的节点。

### 兼容性文件
为了保持向后兼容，系统仍会在根目录生成以下文件：
- `result/webpage.txt` - 最新文章链接
- `result/subscription.txt` - 最新订阅链接
- `result/nodelist.txt` - 最新有效节点

### 缓存机制
系统具有智能缓存机制：
- **文章链接缓存**：如果当天已经收集过某网站的文章链接，则跳过该网站的文章收集
- **订阅链接缓存**：如果某文章的订阅链接已经收集过，则跳过该文章的订阅解析
- **避免重复执行**：只处理尚未收集的数据，大幅提高运行效率

## 订阅链接使用

### 直接使用节点文件
您可以将 `result/nodelist.txt` 中的节点内容直接复制到您的V2Ray客户端中。

**注意**：带日期的文件夹不会提交到GitHub，请使用根目录的 `nodelist.txt` 获取最新数据。

### 按日期访问历史数据
系统支持按日期访问历史数据：
- 2025-12-24的数据：`https://raw.githubusercontent.com/你的用户名/free_v2ray_daily/main/result/20251224/nodelist.txt`
- 2025-12-23的数据：`https://raw.githubusercontent.com/你的用户名/free_v2ray_daily/main/result/20251223/nodelist.txt`

**注意**：带日期的文件夹不会提交到GitHub，建议使用以下订阅链接获取最新数据。

### 通过订阅转换服务
为了更方便地使用这些节点，您可以通过订阅转换服务将节点文件转换为订阅链接：

1. **获取节点文件内容**
   - 访问 `https://raw.githubusercontent.com/你的用户名/free_v2ray_daily/main/result/20251224/nodelist.txt`

2. **使用订阅转换服务**
   推荐的订阅转换服务：
   - https://sub.xeton.dev/
   - https://sub.id9.cc/
   - https://api.dler.io/

3. **转换步骤**
   - 获取最新节点文件：`https://raw.githubusercontent.com/yafeisun/free_v2ray_daily/refs/heads/main/result/nodelist.txt`
   - 将节点文件内容进行Base64编码
   - 在订阅转换服务中输入编码后的内容
   - 选择目标客户端格式（V2Ray、Clash、Quantumult等）
   - 生成订阅链接

4. **示例订阅链接格式**
   ```
   https://sub.xeton.dev/sub?target=v2ray&url=base64编码后的节点文件内容
   ```

### 自动化订阅链接
如果您fork了本项目并启用了GitHub Actions，可以直接使用以下格式的订阅链接：

**推荐订阅链接（最新数据）**：
```
https://raw.githubusercontent.com/yafeisun/free_v2ray_daily/refs/heads/main/result/nodelist.txt
```

**使用方法**：
1. 将上述链接复制到您的V2Ray客户端
2. 使用"从URL导入"功能
3. 或通过订阅转换服务转换为标准订阅格式

**注意**：
- 带日期的文件夹不会提交到GitHub，请使用根目录的 `nodelist.txt` 获取最新数据
- 如果您fork了本项目，请将链接中的 `yafeisun` 替换为您的GitHub用户名

## 配置说明

### 网站配置
在 `config/websites.py` 中可以配置：
- 网站URL
- 文章列表选择器
- 文章链接选择器
- 订阅链接选择器

### 项目设置
在 `config/settings.py` 中可以配置：
- 文件路径
- 连通性测试参数
- 日志设置

## 自动化部署

项目支持GitHub Actions自动部署：

1. Fork本项目到你的GitHub
2. 启用GitHub Actions
3. 每日自动运行收集任务
4. 自动提交结果到仓库

## 开发说明

### 添加新网站

1. 在 `src/collectors/` 中创建新的收集器类
2. 继承 `BaseCollector` 类
3. 实现必要的方法
4. 在 `config/websites.py` 中添加配置
5. 在主程序中注册新收集器

### 自定义解析

每个网站的收集器都可以自定义：
- 文章链接提取逻辑
- 订阅链接过滤规则
- 节点解析方法

## 故障排除

### 常见问题

#### 1. 代理相关错误
**问题**: 显示"禁用代理设置"但实际需要代理
**解决**: 
- 检查环境变量是否正确设置
- 重启VSCode（如果使用）
- 参考[代理配置故障排除指南](docs/PROXY_TROUBLESHOOTING.md)

#### 2. 网站连接超时
**问题**: 某些网站连接超时
**解决**:
- 确认代理服务器正在运行
- 检查网站是否需要特定代理
- 系统会自动尝试直接连接作为回退

#### 3. SSL证书错误
**问题**: SSL握手失败
**解决**:
- 系统已禁用SSL验证以适应某些网站
- 如果仍有问题，检查代理配置

#### 4. 节点数量为0
**问题**: 收集到的节点为空
**解决**:
- 检查网站是否有当日更新
- 验证网络连接和代理设置
- 查看日志文件了解详细错误

### 调试模式
```bash
# 启用详细日志
python3 run.py --sites freeclashnode

# 查看日志文件
tail -f data/logs/collector_$(date +%Y%m%d).log
```

## 注意事项

- 本项目仅用于学习和研究目的
- 请遵守相关网站的使用条款
- 节点的可用性会随时间变化
- 建议定期检查和更新配置
- 使用订阅转换服务时，请注意数据安全和隐私保护
- 建议使用可信的第三方订阅转换服务
- **代理配置是正常运行的关键，请确保正确设置**

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 更新日志

- **v2.0.0**: 重构项目结构，添加文章链接收集功能
- **v1.0.0**: 初始版本，支持基本的节点收集和测试