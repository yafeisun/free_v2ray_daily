# Free V2Ray Daily Node Collector

每日自动收集13个主流免费V2Ray节点的脚本，支持GitHub Actions自动更新。

## 📋 支持的网站

- FreeClashNode
- 米贝节点 (mibei77)
- ClashNodeV2Ray
- ProxyQueen
- 玩转迷 (wanzhuanmi)
- CFMem
- ClashNodeCC
- Datiya
- Telegeam
- ClashGithub
- OneClash
- FreeV2rayNode
- 85LA

## 🎯 快速使用

### 订阅链接

```
https://raw.githubusercontent.com/yafeisun/free_v2ray_daily/refs/heads/main/result/nodelist.txt
```

### 使用方法

**方法1：直接导入节点文件**
- 下载 `nodelist.txt` 文件
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

**跳过连通性测试**
```bash
python3 run.py --no-test
```

**自动提交到GitHub**
```bash
python3 run.py --update-github
```

## 🔧 代理配置（可选）

如果某些网站无法访问，配置代理：

```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
export http_proxy=http://127.0.0.1:10808/
export https_proxy=http://127.0.0.1:10808/

# 重新加载
source ~/.zshrc
```

## ❓ 常见问题

**Q: 节点无法使用？**
A: 免费节点时效性强，建议每日更新。如果全部失效，请等待下一批次更新。

**Q: 如何查看收集日志？**
A: 查看 `data/logs/` 目录下的日志文件。

**Q: 网站访问失败？**
A: 检查网络连接，必要时配置代理（见上方代理配置）。

**Q: GitHub Actions自动更新时间？**
A: 每日北京时间早上8点自动运行。

## 📝 更新日志

- **v2.2.1**: 修复日期匹配问题，支持中文日期格式
- **v2.2.0**: 优化代理配置，支持自动回退
- **v2.1.0**: 新增ClashNodeCC支持
- **v2.0.0**: 重构项目结构，添加文章链接收集

## 📄 许可证

MIT License

---

**注意**: 本项目仅供学习交流使用，请遵守当地法律法规。