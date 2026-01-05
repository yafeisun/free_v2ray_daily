# 使用说明

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行收集器
```bash
# 完整运行（收集+保存）
python3 src/main.py

# 启用测速
python3 src/main.py --test

# 只收集特定网站
python3 src/main.py --sites freeclashnode mibei77

# 收集并更新GitHub
python3 src/main.py --update-github
```

### 3. 使用脚本运行
```bash
python3 scripts/run_collector.py
```

### 4. 批量运行所有网站
```bash
python3 scripts/run_all_sites.py
```

## 支持的网站

项目支持多个免费V2Ray节点网站，具体配置可在 `config/websites.py` 中查看和调整。

## 项目结构

```
free_v2ray_daily/
├── src/                    # 源代码
│   ├── collectors/         # 网站爬虫
│   ├── testers/           # 测试工具
│   ├── utils/             # 工具模块
│   └── main.py           # 主程序
├── config/                # 配置文件
├── data/                  # 数据目录
├── tests/                 # 测试文件
└── scripts/              # 运行脚本
```

## 配置说明

主要配置在 `config/settings.py` 和 `config/websites.py` 中：

- `CONNECTION_TIMEOUT`: 连接超时时间
- `MAX_WORKERS`: 最大并发线程数
- `WEBSITES`: 网站配置，可以启用/禁用特定网站

## 自动部署

项目配置了GitHub Actions，每天北京时间早上8点自动运行。

## 输出文件

- `nodelist.txt`: 有效节点列表
- `data/processed/`: 处理后的数据和元数据
- `data/logs/`: 运行日志

## 故障排除

1. **网络问题**: 检查网络连接和代理设置
2. **依赖问题**: 确保安装了所有requirements.txt中的包
3. **权限问题**: 确保有写入权限
4. **Git问题**: 检查Git配置和权限

运行测试验证安装：
```bash
python3 tests/test_basic.py
```

## 代理配置

某些网站需要通过代理才能访问，详细配置请参考：[代理配置故障排除指南](PROXY_TROUBLESHOOTING.md)

## 架构说明

项目采用可插拔架构，详细说明请参考：[可插拔架构使用指南](PLUGIN_ARCHITECTURE.md)