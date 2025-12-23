# 免费V2Ray节点收集器

一个自动化的V2Ray节点收集和测试系统，每日从多个免费节点网站收集最新的V2Ray节点。

## 功能特性

- 🌐 **多网站支持**: 支持6个主流免费V2Ray节点网站
- 📰 **文章链接收集**: 自动获取每个网站最新发布的文章链接
- 🔗 **订阅链接提取**: 自动提取V2Ray订阅链接（过滤Clash/Sing-box）
- 🧪 **连通性测试**: 自动测试节点可用性，丢弃超时节点
- 🇭🇰 **地区分类**: 自动识别并分离香港节点
- 📁 **分类保存**: 不同类型节点分别保存到不同文件
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
│   └── run_all_sites.py   # 批量运行脚本
├── result/                # 结果文件
│   ├── webpage.txt        # 最新文章链接
│   ├── subscription.txt   # V2Ray订阅链接
│   ├── nodelist.txt       # 其他地区节点
│   └── nodelist_HK.txt    # 香港节点
├── tests/                 # 测试文件
├── docs/                  # 文档
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

### 3. 运行方式

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

## 输出文件说明

### `result/webpage.txt`
包含各网站最新发布的文章链接，格式：
```
# 各网站最新文章链接
# 收集时间: 2025-12-23 13:17:43
# 总网站数: 6
================================================================================

# freeclashnode
https://www.freeclashnode.com/free-node/2025-12-23-free-clash-subscribe.htm

------------------------------------------------------------
```

### `result/subscription.txt`
包含所有V2Ray订阅链接，格式：
```
# V2Ray订阅链接收集结果
# 收集时间: 2025-12-23 13:17:43
# 总链接数: 6
================================================================================

# freeclashnode
# 文章链接: https://www.freeclashnode.com/free-node/2025-12-23-free-clash-subscribe.htm
# 链接数: 2
https://node.freeclashnode.com/uploads/2025/12/4-20251223.txt
https://node.freeclashnode.com/uploads/2025/12/1-20251223.txt

------------------------------------------------------------
```

### `result/nodelist.txt` 和 `result/nodelist_HK.txt`
包含经过连通性测试的有效节点，已按地区分类。

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

## 注意事项

- 本项目仅用于学习和研究目的
- 请遵守相关网站的使用条款
- 节点的可用性会随时间变化
- 建议定期检查和更新配置

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 更新日志

- **v2.0.0**: 重构项目结构，添加文章链接收集功能
- **v1.0.0**: 初始版本，支持基本的节点收集和测试