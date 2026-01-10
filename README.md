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

**方法2：使用已测速的节点文件**
- 下载 `nodelist.txt` 文件（已通过TCP连通性测试）
- 在V2Ray客户端中直接导入

**已测速节点链接**
```
https://raw.githubusercontent.com/yafeisun/v2raynode/refs/heads/main/result/nodelist.txt
```

## 🧪 节点测试

### 测试策略

- **支持HTTP代理的节点**：测试5个目标网站，至少成功访问3个才算有效
- **不支持HTTP代理的节点**：仅测试TCP连通性，能建立连接就算有效

### 测试目标网站

节点测试通过以下主流网站的连通性来验证：
- [ChatGPT](https://chatgpt.com)
- [Gemini](https://gemini.google.com)
- [YouTube](https://www.youtube.com)
- [X.com](https://x.com)
- [Reddit](https://www.reddit.com)

### 测试说明

- **测试方法**: TCP连通性测试 + HTTP代理测试（适用于支持HTTP代理的节点）
- **测试标准**: 
  - 支持HTTP代理的节点：5个网站中至少成功访问3个
  - 不支持HTTP代理的节点：能够建立TCP连接
- **测试原因**: V2Ray节点类型多样，需要根据节点类型采用不同的测试方法
- **建议**: 使用V2Ray客户端（如V2RayN、Qv2ray等）测试节点的实际可用性

### 测试结果

测试结果会自动提交到GitHub，可以通过Git提交历史查看最新的测试统计信息。

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

## 📄 许可证

MIT License

---

**注意**: 本项目仅供学习交流使用，请遵守当地法律法规。