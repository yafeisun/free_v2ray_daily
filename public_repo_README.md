# V2Ray 免费节点

每日自动更新的免费V2Ray节点列表，支持多种协议。

## 📋 节点文件说明

### nodelist.txt
- **描述**: 经过筛选的有效节点列表
- **协议**: vmess, vless, trojan, hysteria2, ss, ssr
- **更新频率**: 每日北京时间早上8点
- **使用方式**: 直接导入到V2Ray客户端

### nodetotal.txt
- **描述**: 所有收集到的节点（包括未测试的）
- **用途**: 备份和完整节点列表

### subscription.txt
- **描述**: 订阅链接列表
- **用途**: 可用于订阅转换服务

## 🎯 使用方法

### 方法1：直接导入节点文件

1. 下载 `nodelist.txt` 文件
2. 在V2Ray客户端中选择"从文件导入"
3. 选择下载的文件

### 方法2：通过订阅链接

```bash
# 使用curl下载
curl https://raw.githubusercontent.com/yafeisun/v2ray-nodes/main/nodelist.txt -o nodes.txt

# 使用wget下载
wget https://raw.githubusercontent.com/yafeisun/v2ray-nodes/main/nodelist.txt
```

### 方法3：通过订阅转换服务

1. 复制节点文件内容
2. 使用订阅转换服务（如 sub.xeton.dev, sub.id9.cc）
3. 生成标准订阅链接

## 📱 支持的客户端

- V2Ray / V2RayN
- Clash / Clash Meta / Mihomo
- QuantumultX
- Shadowrocket
- Sing-Box
- Loon
- Surge

## ⚠️ 注意事项

1. **时效性**: 免费节点时效性强，建议每日更新
2. **速度**: 节点速度可能不稳定，建议测试后使用
3. **合法性**: 请遵守当地法律法规，仅供学习交流使用
4. **隐私**: 不收集用户信息，仅提供公开节点

## 🔄 更新时间

- **自动更新**: 每日北京时间早上8点
- **手动触发**: 可通过GitHub Actions手动触发

## 📊 节点统计

- **节点来源**: 13个主流免费节点网站
- **协议支持**: vmess, vless, trojan, hysteria2, ss, ssr
- **地区覆盖**: 香港、美国、欧洲、日本、韩国等

## 🔗 相关链接

- 私有代码仓库: https://github.com/yafeisun/v2raynode
- 节点订阅地址: https://raw.githubusercontent.com/yafeisun/v2ray-nodes/main/nodelist.txt

## 📝 更新日志

- 2026-01-09: 初始化公开仓库，开始自动发布节点

---

**免责声明**: 本项目仅供学习交流使用，不对节点可用性、速度或安全性负责。请谨慎使用，遵守当地法律法规。