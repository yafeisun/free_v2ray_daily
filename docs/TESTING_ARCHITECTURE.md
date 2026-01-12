# 节点测试架构文档

## 概述

本文档描述了 free_v2ray_daily 项目的模块化节点测试架构，包括集成的 subs-check 内核和新的测试逻辑。

## 架构设计

### 目录结构

```
free_v2ray_daily/
├── src/
│   ├── testers/              # 测试模块
│   │   ├── __init__.py
│   │   ├── base_tester.py   # 基础测试器（抽象类）
│   │   ├── tcp_tester.py    # TCP连通性测试器
│   │   └── media_tester.py  # 流媒体解锁测试器
│   └── subscheck/           # Subs-Check集成模块
│       ├── __init__.py
│       ├── config.py        # 配置管理
│       └── manager.py       # subs-check管理器
├── scripts/
│   ├── test_nodes.py        # 节点测试脚本（新版）
│   └── install_subscheck.sh # subs-check安装脚本
└── subscheck/               # subs-check工作目录
    ├── bin/
    │   └── subs-check       # subs-check二进制文件
    └── config/
        └── config.yaml      # subs-check配置文件
```

### 模块说明

#### 1. 测试模块 (src/testers/)

##### BaseTester (base_tester.py)
- **作用**: 定义测试器接口和通用功能
- **功能**:
  - 提取节点主机和端口
  - 获取节点传输类型
  - 定义测试器抽象接口

##### TCPTester (tcp_tester.py)
- **作用**: 测试节点的TCP连通性
- **功能**:
  - 测试节点服务器的TCP连接
  - 批量并发测试
  - 提供详细的测试统计信息

##### MediaTester (media_tester.py)
- **作用**: 测试节点的流媒体访问能力
- **功能**:
  - 测试5个目标网站的访问能力
  - 实现新的测试规则：5个网站中至少3个可访问 + ChatGPT/Gemini至少1个可访问
  - 提供详细的测试统计信息

#### 2. Subs-Check集成模块 (src/subscheck/)

##### SubsCheckConfig (config.py)
- **作用**: 管理subs-check的配置文件
- **功能**:
  - 加载和保存配置
  - 提供默认配置
  - 更新订阅链接

##### SubsCheckManager (manager.py)
- **作用**: 管理subs-check内核的运行
- **功能**:
  - 检查和下载subs-check二进制文件
  - 创建和管理配置文件
  - 运行subs-check
  - 解析输出文件

## 测试逻辑

### 新的测试规则

节点必须同时满足以下两个条件才被认为是有效的：

1. **条件1**: 5个目标网站中至少3个可访问
   - ChatGPT (https://chatgpt.com)
   - Gemini (https://gemini.google.com)
   - YouTube (https://www.youtube.com)
   - X.com (https://x.com)
   - Reddit (https://www.reddit.com)

2. **条件2**: ChatGPT和Gemini中至少1个可访问
   - ChatGPT (https://chatgpt.com)
   - Gemini (https://gemini.google.com)

### 测试流程

```
节点列表
    ↓
┌─────────────────────┐
│  TCP连通性测试      │ → 过滤掉无法连接的节点
└─────────────────────┘
    ↓
┌─────────────────────┐
│  流媒体访问测试      │ → 应用新的测试规则
└─────────────────────┘
    ↓
有效节点列表
```

## 使用方法

### 1. 安装subs-check

```bash
cd /home/geely/Documents/Github/free_v2ray_daily
./scripts/install_subscheck.sh
```

### 2. 运行节点测试

```bash
# 基本用法
python3 scripts/test_nodes.py

# 指定输入输出文件
python3 scripts/test_nodes.py --input result/nodetotal.txt --output result/nodelist.txt

# 跳过TCP测试
python3 scripts/test_nodes.py --skip-tcp

# 跳过媒体测试
python3 scripts/test_nodes.py --skip-media

# 使用subs-check测试（需要先安装）
python3 scripts/test_nodes.py --use-subscheck
```

### 3. 集成到主流程

修改 `src/main.py`，在收集完节点后调用测试脚本：

```python
# 在 collect_all_nodes() 方法中添加
if valid_nodes:
    logger.info("开始节点测试...")
    
    from src.testers import TCPTester, MediaTester
    
    # TCP测试
    tcp_tester = TCPTester()
    valid_nodes = tcp_tester.test_nodes(valid_nodes)
    
    # 媒体测试
    if valid_nodes:
        media_tester = MediaTester()
        valid_nodes = media_tester.test_nodes(valid_nodes)
    
    logger.info(f"测试完成，有效节点: {len(valid_nodes)}")
```

## 配置说明

### 测试配置

在 `config/settings.py` 中可以调整以下参数：

```python
# 测试配置
CONNECTION_TIMEOUT = 5  # 连接超时时间（秒）
MAX_WORKERS = 10  # 最大并发测试线程数
```

### MediaTester配置

在 `src/testers/media_tester.py` 中可以调整以下参数：

```python
MIN_SUCCESS_SITES = 3  # 至少需要成功访问的网站数量
MIN_AI_SITES = 1      # 至少需要成功访问的AI服务数量
```

### Subs-Check配置

在 `subscheck/config/config.yaml` 中可以配置subs-check的参数：

```yaml
# 基本配置
print-progress: true
concurrent: 20
timeout: 5000

# 测速配置
speed-test-url: https://github.com/AaronFeng753/Waifu2x-Extension-GUI/releases/download/v2.21.12/Waifu2x-Extension-GUI-v2.21.12-Portable.7z
min-speed: 512
download-timeout: 10

# 流媒体检测
media-check: true
media-check-timeout: 10
platforms:
  - iprisk
  - youtube
  - netflix
  - openai
  - gemini
```

## 扩展性

### 添加新的测试器

1. 继承 `BaseTester` 类
2. 实现 `test_node()` 和 `test_nodes()` 方法
3. 在 `src/testers/__init__.py` 中导出

示例：

```python
from src.testers.base_tester import BaseTester

class CustomTester(BaseTester):
    def test_node(self, node: str) -> Tuple[bool, Dict]:
        # 实现测试逻辑
        pass
    
    def test_nodes(self, nodes: List[str]) -> List[str]:
        # 实现批量测试逻辑
        pass
```

### 添加新的测试目标

在 `src/testers/media_tester.py` 中添加新的网站到 `TEST_SITES` 列表：

```python
TEST_SITES = [
    {'name': 'ChatGPT', 'url': 'https://chatgpt.com', 'expected_status': 200, 'priority': 'high'},
    {'name': 'Gemini', 'url': 'https://gemini.google.com', 'expected_status': 200, 'priority': 'high'},
    # 添加新网站
    {'name': 'NewSite', 'url': 'https://newsite.com', 'expected_status': 200, 'priority': 'normal'},
]
```

## 注意事项

1. **TCP测试 vs HTTP代理测试**: V2Ray/Trojan节点不是HTTP代理服务器，无法通过HTTP代理方式测试。当前的实现使用TCP连接测试，这是最基础和可靠的方法。

2. **并发控制**: 根据网络状况调整并发数，避免网络拥堵。

3. **超时设置**: 根据网络状况调整超时时间。

4. **Subs-Check集成**: Subs-Check提供了更完整的流媒体检测功能，但需要额外的安装和配置。当前版本提供了基本的TCP和媒体测试，可以满足大多数需求。

## 未来改进

1. 实现真正的HTTP代理测试（需要本地代理服务器）
2. 完善Subs-Check集成功能
3. 添加更多的测试目标网站
4. 实现测试结果的持久化存储
5. 添加测试历史记录和趋势分析

## 许可证

MIT License
