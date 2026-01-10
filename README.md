# Free V2Ray Daily Node Collector

每日自动收集13个主流免费V2Ray节点的脚本，支持GitHub Actions自动更新。

## 📋 支持的网站

- [FreeClashNode](https://www.freeclashnode.com/free-node/)
- [米贝节点](https://www.mibei77.com/) (mibei77)
- [ClashNodeV2Ray](https://clashnodev2ray.github.io/)
- [ProxyQueen](https://www.proxyqueen.top/)
- [玩转迷](https://wanzhuanmi.com/) (wanzhuanmi)
- [CFMem](https://www.cfmem.com/)
- [ClashNodeCC](https://clashnode.cc/)
- [Datiya](https://free.datiya.com/)
- [Telegeam](https://telegeam.github.io/clashv2rayshare/)
- [ClashGithub](https://clashgithub.com/)
- [OneClash](https://oneclash.cc/freenode)
- [FreeV2rayNode](https://www.freev2raynode.com/free-node-subscription/)
- [85LA](https://www.85la.com/internet-access/free-network-nodes)

## 🎯 快速使用

### 订阅链接

```
https://raw.githubusercontent.com/yafeisun/v2raynode/refs/heads/main/result/nodetotal.txt
```

### 使用方法

**方法1：直接导入节点文件**
- 下载 `nodetotal.txt` 文件
- 在V2Ray客户端中直接导入

## 📦 安装与运行

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行收集器

**运行所有网站**
```bash
python3 run.py
```

**运行指定网站**
```bash
python3 run.py --sites telegeam wanzhuanmi
```

**启用连通性测试**
```bash
python3 run.py --test
```

**自动提交到GitHub**
```bash
python3 run.py --update-github
```

## 🔧 代理配置（可选）

### 本地运行

如果某些网站无法访问，配置代理：

```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
export http_proxy=http://127.0.0.1:10808/
export https_proxy=http://127.0.0.1:10808/

# 重新加载
source ~/.zshrc
```

### GitHub Actions

GitHub Actions 自动使用 Cloudflare WARP 代理，无需额外配置。

## ❓ 常见问题

**Q: 节点无法使用？**
A: 免费节点时效性强，建议每日更新。如果全部失效，请等待下一批次更新。

**Q: 如何查看收集日志？**
A: 查看 `data/logs/` 目录下的日志文件。

**Q: 网站访问失败？**
A: 检查网络连接，必要时配置代理（见上方代理配置）。

**Q: GitHub Actions自动更新时间？**
A: 每日北京时间下午3点自动运行。

## 📝 更新日志

- **v2.3.0**: 集成 Cloudflare WARP 代理，提高节点收集成功率
- **v2.2.1**: 修复日期匹配问题，支持中文日期格式
- **v2.2.0**: 优化代理配置，支持自动回退
- **v2.1.0**: 新增ClashNodeCC支持
- **v2.0.0**: 重构项目结构，添加文章链接收集

## 📄 许可证

MIT License

---

**注意**: 本项目仅供学习交流使用，请遵守当地法律法规。