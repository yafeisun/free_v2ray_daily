# 免费V2Ray节点每日更新

[![Daily Update](https://github.com/yafeisun/free_v2ray_daily/actions/workflows/update_nodes.yml/badge.svg)](https://github.com/yafeisun/free_v2ray_daily/actions/workflows/update_nodes.yml)

本项目每天自动从多个免费节点网站收集最新的V2Ray、Clash、Shadowsocks等节点，经过测速验证后更新到节点列表。

## 📋 功能特性

- ✅ **自动收集**: 每天自动从5个主要免费节点网站收集最新节点
- ✅ **智能解析**: 支持订阅链接和直接节点列表两种格式
- ✅ **连通性测试**: 自动测试所有节点的连通性，过滤无效节点
- ✅ **多协议支持**: 支持VMess、VLESS、Trojan、Hysteria、Shadowsocks等协议
- ✅ **自动更新**: 通过GitHub Actions每天北京时间早上8点自动更新
- ✅ **完全免费**: 所有节点均来自公开免费资源

## 🌐 数据来源

本项目从以下网站收集节点信息：

1. [FreeClashNode](https://www.freeclashnode.com/free-node/) - 每日更新免费Clash节点
2. [米贝节点](https://www.mibei77.com/) - 高质量免费节点分享
3. [ClashNodeV2Ray](https://clashnodev2ray.github.io/) - GitHub Pages节点分享
4. [ProxyQueen](https://www.proxyqueen.top/) - 多区域节点覆盖
5. [玩转迷](https://wanzhuanmi.com/) - 技术分享类节点

## 📦 节点列表

最新的有效节点列表请查看：[nodelist.txt](https://github.com/yafeisun/free_v2ray_daily/blob/main/nodelist.txt)

## 🚀 使用方法

### 1. 直接使用节点列表

直接下载 `nodelist.txt` 文件，导入到你的V2Ray客户端中。

### 2. 订阅链接

部分网站提供订阅链接，可以直接在客户端中添加订阅。

### 3. 支持的客户端

- V2Ray (Windows/Mac/Linux/Android/iOS)
- Clash (Windows/Mac/Linux/Android/iOS)
- Shadowrocket (iOS)
- Quantumult X (iOS)
- Sing-Box
- 其他支持V2Ray协议的客户端

## ⚙️ 技术实现

### 核心功能

- **网站爬虫**: 使用BeautifulSoup解析网页，智能提取最新文章链接
- **节点解析**: 支持Base64编码的订阅链接和直接节点文本
- **连通性测试**: 使用TCP连接测试节点可用性
- **自动提交**: 通过GitPython自动提交更新到GitHub

### 技术栈

- **Python 3.9+**: 主要编程语言
- **Requests**: HTTP请求库
- **BeautifulSoup4**: HTML解析
- **GitPython**: Git操作
- **GitHub Actions**: 自动化CI/CD

## 📅 更新时间

- **自动更新**: 每天北京时间早上8点 (UTC时间0点)
- **手动触发**: 支持通过GitHub Actions手动触发更新
- **更新频率**: 每日一次，确保节点新鲜度

## 🔧 本地运行

### 环境要求

```bash
Python 3.9+
pip
git
```

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/yafeisun/free_v2ray_daily.git
cd free_v2ray_daily
```

2. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 运行收集器
```bash
python node_collector.py
```

### 配置说明

主要配置在 `config.py` 文件中：

```python
# 网站配置
WEBSITES = [
    'https://www.freeclashnode.com/free-node/',
    'https://www.mibei77.com/',
    # ... 更多网站
]

# 测试配置
CONNECTION_TIMEOUT = 5  # 连接超时时间（秒）
MAX_WORKERS = 10        # 最大并发测试线程数
```

## 📊 节点统计

- **每日收集**: 约100-300个节点
- **有效节点**: 约30-80个节点（根据网络状况变化）
- **覆盖区域**: 美国、新加坡、日本、香港、欧洲等
- **支持协议**: VMess、VLESS、Trojan、Hysteria、Shadowsocks

## ⚠️ 免责声明

1. **仅供学习交流**: 本项目仅用于技术学习和交流目的
2. **网络安全**: 请遵守当地法律法规，合理使用网络资源
3. **服务稳定性**: 免费节点可能不稳定，建议仅供临时使用
4. **隐私保护**: 使用免费节点时请注意保护个人隐私信息
5. **商业用途**: 禁止将本项目的节点用于任何商业用途

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 贡献方式

1. **报告问题**: 如果发现无效节点或程序错误，请提交Issue
2. **新增网站**: 推荐新的免费节点网站
3. **功能改进**: 提出功能建议或代码优化
4. **文档完善**: 改进README和代码注释

### 开发规范

- 遵循PEP 8代码规范
- 添加必要的注释和文档
- 确保代码测试通过
- 提交前请运行代码检查

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

## 🙏 致谢

感谢以下开源项目和服务：

- [Python](https://www.python.org/) - 编程语言
- [Requests](https://requests.readthedocs.io/) - HTTP库
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML解析
- [GitHub Actions](https://github.com/features/actions) - CI/CD平台
- 各个免费节点网站的维护者

## 📞 联系方式

- **GitHub**: [@yafeisun](https://github.com/yafeisun)
- **Issues**: [提交问题](https://github.com/yafeisun/free_v2ray_daily/issues)

---

⭐ 如果这个项目对你有帮助，请给个Star支持一下！