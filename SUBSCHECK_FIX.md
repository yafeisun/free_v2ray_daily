# Subs-Check 测试方案

## 问题分析

### 原始测试逻辑的问题

之前的 `media_tester.py` 实现存在严重缺陷：

```python
# 测试到目标网站的TCP连接
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(self.timeout)
result = sock.connect_ex((site_host, 443))  # HTTPS端口
sock.close()
```

**这个测试只测试本地网络能否直接连接到目标网站，而不是通过V2Ray节点代理访问。**

### 测试结果分析

| 网站 | 成功率 | 原因 |
|------|--------|------|
| Gemini | 0.00% | 在中国大陆被完全封锁 |
| YouTube | 0.00% | 在中国大陆被完全封锁 |
| ChatGPT | 30.82% | 部分IP段没有被完全封锁 |
| X.com | 98.93% | 访问限制较少 |
| Reddit | 98.53% | 访问限制较少 |

**结论：这是测试逻辑问题，不是节点问题。测试结果不能反映节点的真实可用性。**

## 解决方案

### 使用 subs-check 工具

`subs-check` 是一个命令行工具，可以在无头环境（如 GitHub Actions）中运行，进行真实的代理测试：

1. **支持多种节点类型**：VMess, VLESS, Trojan, Shadowsocks, Hysteria2
2. **真实的代理测试**：启动节点客户端，通过代理发送HTTP请求
3. **流媒体解锁测试**：支持 YouTube, Netflix, OpenAI, Gemini 等平台
4. **速度测试**：测试节点的实际下载速度
5. **自动筛选**：根据配置自动筛选有效节点

### 实现步骤

#### 1. 节点转换 (`scripts/convert_nodes_to_subscription.py`)

将 V2Ray URI 格式的节点列表转换为 Clash 订阅格式：

```python
# 输入: V2Ray URI 列表
vless://e258977b-e413-4718-a3af-02d75492c349@104.16.93.22:443?encryption=none&security=tls&sni=jp20.xaniusg2.qzz.io&type=ws&host=jp20.xaniusg2.qzz.io&path=%2F%3Fed%3D2560#HK
trojan://e0e28234-f4cd-4583-922c-c97795cb6222@green2.cdntencentmusic.com:31102?security=tls&sni=green2.cdntencentmusic.com&type=tcp&headerType=none#TW

# 输出: Clash YAML 格式
proxies:
  - name: HK
    type: vless
    server: 104.16.93.22
    port: 443
    uuid: e258977b-e413-4718-a3af-02d75492c349
    ...
  - name: TW
    type: trojan
    server: green2.cdntencentmusic.com
    port: 31102
    password: e0e28234-f4cd-4583-922c-c97795cb6222
    ...
```

#### 2. 测试脚本 (`scripts/test_nodes_with_subscheck.py`)

使用 subs-check 进行真实的代理测试：

```python
# 1. 自动下载 subs-check 工具
# 2. 创建配置文件
# 3. 运行测试
# 4. 解析结果
# 5. 转换回 V2Ray 格式
```

#### 3. GitHub Actions 工作流

更新 `.github/workflows/test_nodes.yml`：

```yaml
- name: Install subs-check
  run: |
    chmod +x scripts/convert_nodes_to_subscription.py
    chmod +x scripts/test_nodes_with_subscheck.py

- name: Test nodes with subs-check
  run: |
    python3 scripts/test_nodes_with_subscheck.py \
      --input result/nodetotal.txt \
      --output result/nodelist.txt \
      --timeout 1800
```

## 测试配置

### subs-check 配置

```yaml
# 测速配置
alive-test-url: http://gstatic.com/generate_204
speed-test-url: https://github.com/AaronFeng753/Waifu2x-Extension-GUI/releases/download/v2.21.12/Waifu2x-Extension-GUI-v2.21.12-Portable.7z
min-speed: 512  # 最小速度 512 KB/s

# 流媒体检测
media-check: true
media-check-timeout: 10
platforms:
  - iprisk
  - youtube
  - netflix
  - openai
  - gemini

# 并发配置
concurrent: 20  # 并发测试20个节点
timeout: 5000  # 单个测试超时5秒
```

## 使用方法

### 本地测试

```bash
# 1. 转换节点为Clash格式
python3 scripts/convert_nodes_to_subscription.py \
  --input result/nodetotal.txt \
  --output result/clash_subscription.yaml

# 2. 运行测试
python3 scripts/test_nodes_with_subscheck.py \
  --input result/nodetotal.txt \
  --output result/nodelist.txt \
  --timeout 1800
```

### GitHub Actions

测试会在节点收集完成后自动触发：

```yaml
# 触发条件
on:
  workflow_run:
    workflows: ["Update Free Nodes"]
    types: [completed]
    branches: [main]
```

## 预期结果

使用 subs-check 后，预期会得到：

1. **真实的节点可用性测试结果**
2. **准确的速度测试数据**
3. **流媒体解锁能力测试结果**
4. **自动筛选的高质量节点**

### 测试指标

- **连通性测试**：节点是否可以连接
- **速度测试**：节点的实际下载速度
- **流媒体解锁**：YouTube, Netflix, OpenAI, Gemini 等平台的访问能力
- **IP风险检测**：节点IP是否被列入黑名单

## 注意事项

1. **测试时间**：subs-check 测试需要较长时间（约30分钟，取决于节点数量）
2. **网络要求**：需要能够访问 GitHub 和测试目标网站
3. **资源消耗**：并发测试会占用较多系统资源
4. **超时设置**：可以根据实际情况调整超时时间

## 相关文件

- `scripts/convert_nodes_to_subscription.py` - 节点转换脚本
- `scripts/test_nodes_with_subscheck.py` - 测试脚本
- `src/subscheck/manager.py` - Subs-Check 管理器
- `src/subscheck/config.py` - 配置管理器
- `.github/workflows/test_nodes.yml` - GitHub Actions 工作流