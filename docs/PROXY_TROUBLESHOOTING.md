# 代理配置问题解决方案

## 问题描述

在V2Ray节点收集系统中，遇到了代理配置相关的问题：

1. **环境变量检测不一致**：在终端直接运行Python时代理正常工作，但在VSCode中运行时显示"禁用代理设置"
2. **SSL连接问题**：某些网站在直接连接时出现SSL错误，需要通过代理访问
3. **环境变量继承问题**：VSCode启动时无法正确继承系统代理环境变量

## 根本原因分析

### 1. 环境变量作用域问题
- 代理环境变量仅在当前终端会话中有效
- VSCode作为独立应用程序启动时，不会自动继承终端的环境变量
- 需要将代理配置写入shell配置文件（.zshrc/.bashrc）

### 2. Python环境检测逻辑
- 原始代码只检查小写环境变量（http_proxy, https_proxy）
- 实际系统中可能同时存在大小写变量
- 需要兼容两种格式的环境变量

### 3. 网络连接策略
- 某些网站（如CFMem、ClashNodeV2Ray）需要代理才能访问
- 直接连接会导致SSL握手失败
- 需要实现代理到直接连接的自动回退机制

## 解决方案

### 1. 修复环境变量检测逻辑

```python
# 配置代理（如果系统有设置代理）
import os
http_proxy = os.getenv('http_proxy') or os.getenv('HTTP_PROXY')
https_proxy = os.getenv('https_proxy') or os.getenv('HTTPS_PROXY')

if http_proxy or https_proxy:
    # 使用系统代理设置
    proxies = {}
    if http_proxy:
        proxies['http'] = http_proxy
    if https_proxy:
        proxies['https'] = https_proxy
    self.session.proxies.update(proxies)
    self.logger.info(f"使用系统代理: {proxies}")
else:
    # 如果没有代理设置，禁用代理以避免潜在问题
    self.session.proxies = {'http': None, 'https': None}
    self.logger.info("禁用代理设置")
```

### 2. 配置Shell环境变量

在 `.zshrc` 或 `.bashrc` 文件中添加：

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

### 3. 实现自动回退机制

```python
# 在请求失败时自动切换到直接连接
if using_proxy and attempt == 0:
    self.logger.info(f"代理连接失败，尝试直接访问: {url}")
    self.session.proxies = {'http': None, 'https': None}
    using_proxy = False
    continue
```

### 4. 统一SSL验证设置

```python
# 禁用SSL验证（与代理使用保持一致）
self.session.verify = False
```

## 验证步骤

### 1. 检查环境变量
```bash
env | grep -i proxy
```

### 2. 测试Python环境
```python
import os
for key in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
    print(f'{key}: {repr(os.getenv(key))}')
```

### 3. 测试网络连接
```python
import requests
proxies = {'http': 'http://127.0.0.1:10808/', 'https': 'http://127.0.0.1:10808/'}
response = requests.get('https://example.com', verify=False, proxies=proxies)
```

## 最佳实践

### 1. 环境配置
- 将代理设置写入shell配置文件，确保永久生效
- 同时设置大小写环境变量，提高兼容性
- 配置no_proxy避免本地地址走代理

### 2. 代码设计
- 实现优雅的代理检测和回退机制
- 统一SSL验证设置
- 添加详细的日志记录

### 3. 调试技巧
- 添加调试日志跟踪环境变量检测
- 分别测试代理和直接连接
- 使用环境变量验证工具

## 常见问题

### Q: VSCode中仍然显示"禁用代理设置"？
A: 需要完全重启VSCode，重新加载环境变量。

### Q: 某些网站仍然无法访问？
A: 检查代理服务器状态，确认目标网站是否需要特定代理。

### Q: 如何临时禁用代理？
A: 在终端中运行：`unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY`

## 总结

通过以上解决方案，成功解决了代理配置问题：
- ✅ 环境变量检测兼容大小写格式
- ✅ 实现了代理到直接连接的自动回退
- ✅ 配置了永久有效的shell环境变量
- ✅ 统一了SSL验证设置
- ✅ 提供了完整的调试和验证方法

这些改进确保了V2Ray节点收集系统在不同网络环境下的稳定运行。