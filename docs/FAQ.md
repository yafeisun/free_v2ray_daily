# ❓ 常见问题 (FAQ)

本文档收集了用户在使用过程中遇到的常见问题及其解决方案。

---

## 📋 目录

- [安装问题](#安装问题)
- [运行问题](#运行问题)
- [节点问题](#节点问题)
- [客户端配置](#客户端配置)
- [性能优化](#性能优化)
- [开发相关问题](#开发相关问题)
- [代理配置问题](#代理配置问题)

---

## 🔧 安装问题

### Q1: Python版本不兼容怎么办？

**问题描述**:
```
ERROR: This project requires Python 3.8 or higher.
Your Python version: 3.6.9
```

**解决方案**:

**Ubuntu/Debian**:
```bash
# 添加PPA源
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# 安装Python 3.10
sudo apt install python3.10 python3.10-venv

# 设置为默认（可选）
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
```

**macOS**:
```bash
# 使用Homebrew
brew install python@3.10

# 验证安装
python3.10 --version
```

**Windows**:
1. 访问 [python.org/downloads](https://www.python.org/downloads/)
2. 下载Python 3.10或更高版本
3. 安装时勾选"Add Python to PATH"

---

### Q2: 依赖安装失败怎么办？

**问题描述**:
```bash
ERROR: Could not find a version that satisfies the requirement xxx
```

**解决方案**:

**方案1: 升级pip**
```bash
python3 -m pip install --upgrade pip
```

**方案2: 使用国内镜像源**
```bash
# 清华镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 豆瓣镜像
pip install -r requirements.txt -i https://pypi.douban.com/simple/
```

**方案3: 单独安装失败的包**
```bash
# 查看具体哪个包失败
pip install package_name --verbose

# 强制重装
pip install package_name --force-reinstall --no-cache-dir
```

**常见依赖问题**:
```bash
# lxml安装失败
sudo apt-get install python3-dev libxml2-dev libxslt-dev

# telethon安装失败
pip install telethon --upgrade

# pycryptodome安装失败
pip install pycryptodome --upgrade
```

---

### Q3: 克隆仓库失败怎么办？

**问题描述**:
```bash
fatal: unable to access 'https://github.com/.../': Failed to connect
```

**解决方案**:

**方案1: 使用代理**
```bash
git config --global http.proxy http://127.0.0.1:10808
git config --global https.proxy http://127.0.0.1:10808
```

**方案2: 使用SSH克隆**
```bash
git clone git@github.com:yafeisun/v2raynode.git
```

**方案3: 使用镜像站点**
```bash
git clone https://gitee.com/mirrors/v2raynode.git
```

---

## 🚀 运行问题

### Q4: 收集节点数量为0怎么办？

**问题描述**:
运行收集器后显示:
```
📊 成功收集统计:
  • 原始节点数: 0
  • 去重后节点数: 0
```

**可能原因和解决方案**:

**原因1: 网络连接问题**
```bash
# 测试网络连接
ping -c 3 google.com
ping -c 3 github.com

# 测试能否访问目标网站
curl -I https://www.freeclashnode.com
```

**原因2: 代理配置问题**
```bash
# 检查代理环境变量
env | grep -i proxy

# 如果需要代理，设置环境变量
export http_proxy=http://127.0.0.1:10808/
export https_proxy=http://127.0.0.1:10808/

# 重新运行
python3 run.py --collect
```

**原因3: 网站结构变化**
```bash
# 查看详细日志
python3 run.py --collect 2>&1 | tee collect.log

# 搜索错误信息
grep -i error collect.log
```

**原因4: 收集器配置错误**
```bash
# 检查网站配置
python3 -c "from config.websites import WEBSITES; print(WEBSITES)"

# 测试单个网站
python3 src/main.py --sites telegeam
```

---

### Q5: 收集过程超时怎么办？

**问题描述**:
```
ERROR: Request timeout after 30 seconds
```

**解决方案**:

**方案1: 增加超时时间**
```python
# 编辑 config/settings.py
REQUEST_TIMEOUT = 60  # 从30秒增加到60秒
CONNECTION_TIMEOUT = 10  # 从5秒增加到10秒
```

**方案2: 增加重试次数**
```python
# 编辑 config/settings.py
REQUEST_RETRY = 5  # 从3次增加到5次
```

**方案3: 使用代理**
```bash
export http_proxy=http://127.0.0.1:10808/
export https_proxy=http://127.0.0.1:10808/
python3 run.py --collect
```

**方案4: 减少并发数**
```python
# 编辑 config/settings.py
MAX_WORKERS = 5  # 从10减少到5
```

---

### Q6: 出现SSL证书错误怎么办？

**问题描述**:
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**解决方案**:

**方案1: 更新证书（推荐）**
```bash
# Ubuntu/Debian
sudo apt-get install ca-certificates
sudo update-ca-certificates

# macOS
brew install openssl
```

**方案2: 临时禁用SSL验证**
```python
# 编辑 src/collectors/base_collector.py
# 在创建session时添加:
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

self.session.verify = False
```

**方案3: 使用代理**
```bash
# 某些情况下通过代理可以绕过SSL问题
export http_proxy=http://127.0.0.1:10808/
export https_proxy=http://127.0.0.1:10808/
```

---

### Q7: 出现"模块未找到"错误怎么办？

**问题描述**:
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案**:

**方案1: 重新安装依赖**
```bash
pip install -r requirements.txt --force-reinstall
```

**方案2: 检查Python路径**
```bash
# 确保在项目根目录
cd /path/to/v2raynode

# 添加项目路径到Python
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**方案3: 使用虚拟环境**
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

---

## 🌐 节点问题

### Q8: 节点无法连接怎么办？

**问题描述**:
导入节点后无法连接，客户端显示连接失败。

**可能原因和解决方案**:

**原因1: 节点已失效**
```bash
# 使用已测试的节点文件
cat result/nodelist.txt

# 重新测速
python3 run.py --test
```

**原因2: 客户端配置错误**
- 检查客户端配置是否正确
- 确认选择的节点类型（vmess/vless/trojan）
- 查看客户端日志

**原因3: 网络环境限制**
- 尝试切换到其他节点
- 检查本地网络连接
- 尝试使用不同的客户端

**原因4: 节点类型不支持**
```bash
# 查看节点类型
grep "vmess://" result/nodelist.txt
grep "vless://" result/nodelist.txt
grep "trojan://" result/nodelist.txt

# 确认客户端支持的协议类型
```

---

### Q9: 节点速度很慢怎么办？

**问题描述**:
节点连接成功但速度很慢，打开网页很卡。

**优化方案**:

**方案1: 使用速度快的节点**
```bash
# nodelist.txt已按速度排序
# 使用前面的节点（速度更快）
head -20 result/nodelist.txt
```

**方案2: 选择延迟低的节点**
```bash
# 查看测试日志中的延迟信息
grep "延迟" data/logs/collector_$(date +%Y%m%d).log
```

**方案3: 使用CDN加速的节点**
```bash
# CFMem的节点通常更快
python3 src/main.py --sites cfmem
```

**方案4: 调整客户端设置**

**V2RayN**:
- 设置 → 全局设置 → DNS设置
- 使用DoH (DNS over HTTPS)

**ClashX**:
- 配置 → DNS设置
- 启用fake-ip

**方案5: 分流规则**
- 配置分流规则，国内直连
- 减少不必要的流量走代理

---

### Q10: 如何筛选高质量节点？

**解决方案**:

**基于速度筛选**:
```bash
# 提取前50个最快节点
head -50 result/nodelist.txt > fast_nodes.txt
```

**基于区域筛选**:
```bash
# 筛选香港节点
grep -i "hk\|hongkong" result/nodelist.txt > hk_nodes.txt

# 筛选美国节点
grep -i "us\|united.*states\|america" result/nodelist.txt > us_nodes.txt
```

**基于协议筛选**:
```bash
# 筛选vmess节点
grep "^vmess://" result/nodelist.txt > vmess_nodes.txt

# 筛选vless节点
grep "^vless://" result/nodelist.txt > vless_nodes.txt
```

**组合使用**:
```bash
# 美国的vless节点，取前20个
grep "^vless://" result/nodelist.txt | grep -i "us" | head -20
```

---

## 💻 客户端配置

### Q11: V2RayN如何导入节点？

**详细步骤**:

1. **下载V2RayN**
   - 访问: https://github.com/2dust/v2rayN/releases
   - 下载最新版本
   - 解压并运行 `v2rayN.exe`

2. **导入订阅链接**
   - 点击菜单栏的"订阅" → "订阅设置"
   - 点击"添加"
   - 粘贴订阅链接:
     ```
     https://raw.githubusercontent.com/yafeisun/v2raynode/refs/heads/main/result/nodelist.txt
     ```
   - 点击"确定"

3. **更新订阅**
   - 点击"订阅" → "更新订阅"
   - 等待更新完成

4. **选择节点**
   - 在"服务器"列表中查看导入的节点
   - 双击选择一个节点
   - 或右键选择"测试延迟"查看可用性

5. **启用代理**
   - 点击系统托盘图标
   - 启用"系统代理"
   - 浏览器访问测试网站

---

### Q12: ClashX如何导入节点？

**详细步骤**:

1. **下载ClashX**
   - 访问: https://github.com/yichengchen/clashX/releases
   - 下载最新版本
   - 安装并运行ClashX

2. **配置文件管理**
   - 点击菜单栏的ClashX图标
   - 选择"配置" → "Open Config Folder"
   - 关闭文件夹

3. **导入订阅**
   - 点击"配置" → "Manage"
   - 点击"Download"或"New"
   - 粘贴订阅链接
   - 输入配置名称
   - 点击"Download"

4. **应用配置**
   - 在配置列表中选择刚下载的配置
   - 点击"Apply"

5. **选择节点**
   - 点击菜单栏图标
   - 在列表中选择节点
   - 或使用"Auto"模式自动选择

---

### Q13: 如何配置分流规则？

**V2RayN分流规则**:

1. 打开设置 → 路由设置
2. 添加规则:
   - 直连: `geoip:cn`, `geosite:cn`
   - 代理: `geosite:google`, `geosite:youtube`
3. 保存并应用

**ClashX分流规则**:

1. 编辑配置文件 `config.yaml`
2. 添加规则:
```yaml
rules:
  - GEOIP,CN,DIRECT
  - GEOSITE,google,Proxy
  - GEOSITE,youtube,Proxy
  - MATCH,Proxy
```
3. 重新加载配置

---

## ⚡ 性能优化

### Q14: 如何提高收集速度？

**优化方案**:

**方案1: 增加并发数**
```python
# 编辑 config/settings.py
MAX_WORKERS = 20  # 增加并发数
```

**方案2: 减少超时时间**
```python
# 编辑 config/settings.py
REQUEST_TIMEOUT = 15  # 减少超时时间
REQUEST_DELAY = 1  # 减少请求间隔
```

**方案3: 使用代理**
```bash
# 某些网站通过代理更快
export http_proxy=http://127.0.0.1:10808/
```

**方案4: 禁用不需要的网站**
```python
# 编辑 config/websites.py
"telegeam": {
    "enabled": False,  # 禁用这个网站
    # ...
}
```

---

### Q15: 如何减少内存使用？

**优化方案**:

**方案1: 减少并发数**
```python
MAX_WORKERS = 5  # 减少并发数
```

**方案2: 分批收集**
```bash
# 先收集一部分网站
python3 src/main.py --sites freeclashnode mibei77 cfmem

# 再收集另一部分
python3 src/main.py --sites clashnodev2ray telegeam
```

**方案3: 清理旧数据**
```bash
# 清理旧的日志文件
find data/logs/ -name "*.log" -mtime +7 -delete

# 清理旧的原始数据
find data/raw/ -mtime +30 -delete
```

---

## 🛠️ 开发相关问题

### Q16: 如何添加新的网站收集器？

**详细步骤**:

1. **创建收集器类**
```python
# src/collectors/new_site.py
from src.collectors.base_collector import BaseCollector
from typing import List, Optional
import requests
from bs4 import BeautifulSoup

class NewSiteCollector(BaseCollector):
    """新网站收集器"""

    def __init__(self, site_config):
        super().__init__(site_config)

    def get_today_article_url(self) -> Optional[str]:
        """获取今日文章链接"""
        # 实现你的逻辑
        return "https://example.com/article/today"

    def collect(self) -> List[str]:
        """收集节点"""
        article_url = self.get_today_article_url()
        nodes = self.get_v2ray_subscription_links(article_url)
        return nodes
```

2. **添加网站配置**
```python
# config/websites.py
"new_site": {
    "name": "新网站",
    "url": "https://example.com/",
    "enabled": True,
    "collector_key": "new_site",
    "selectors": {
        "article": "a[href*='/article/']",
        "subscription": "a[href*='.txt']",
    },
    "patterns": [
        r'https?://example\.com/\d{4}/\d{2}/\d{2}\.txt',
    ]
}
```

3. **测试收集器**
```bash
python3 src/main.py --sites new_site
```

详细文档: [插件架构指南](PLUGIN_ARCHITECTURE.md)

---

### Q17: 如何调试收集器？

**调试步骤**:

1. **启用调试模式**
```python
# config/settings.py
DEBUG = True
```

2. **查看详细日志**
```bash
# 运行时保存日志
python3 src/main.py --sites telegeam 2>&1 | tee debug.log

# 实时查看日志
tail -f data/logs/collector_$(date +%Y%m%d).log
```

3. **单独测试功能**
```python
# 在收集器中添加测试代码
def test_collection(self):
    """测试收集功能"""
    # 测试文章URL获取
    article_url = self.get_today_article_url()
    print(f"文章URL: {article_url}")

    # 测试订阅链接获取
    sub_links = self.get_v2ray_subscription_links(article_url)
    print(f"订阅链接: {sub_links}")

    # 测试节点收集
    nodes = self.collect_with_base64_detection()
    print(f"节点数量: {len(nodes)}")

# 在主程序中调用
if __name__ == "__main__":
    collector = NewSiteCollector(config)
    collector.test_collection()
```

4. **使用Python调试器**
```bash
# 使用pdb调试
python3 -m pdb src/main.py --sites telegeam

# 或使用ipdb（更友好）
pip install ipdb
python3 -m ipdb src/main.py --sites telegeam
```

---

### Q18: 如何运行测试？

**运行测试**:

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_basic.py

# 查看详细输出
pytest -v tests/

# 显示测试覆盖率
pytest --cov=src tests/
```

**编写测试**:

```python
# tests/test_new_site.py
import pytest
from src.collectors.new_site import NewSiteCollector

def test_new_site_collector():
    """测试新网站收集器"""
    config = {
        "name": "Test Site",
        "url": "https://example.com/",
        "enabled": True,
    }
    collector = NewSiteCollector(config)
    nodes = collector.collect()

    assert len(nodes) > 0
    assert all(node.startswith("vmess://") for node in nodes)
```

---

## 📞 其他问题

### Q19: 如何获取更多帮助？

**获取帮助的方式**:

1. **查看文档**
   - [README.md](../README.md)
   - [项目架构](ARCHITECTURE.md)
   - [故障排除](PROXY_TROUBLESHOOTING.md)

2. **搜索Issues**
   - 访问: https://github.com/yafeisun/v2raynode/issues
   - 搜索你遇到的问题

3. **创建新Issue**
   - 描述问题
   - 提供错误日志
   - 说明你的环境:
     ```yaml
     OS: Ubuntu 20.04
     Python: 3.10
     Version: 2.0.0
     ```

4. **加入讨论**
   - GitHub Discussions: https://github.com/yafeisun/v2raynode/discussions

---

### Q20: 如何贡献代码？

**贡献步骤**:

1. Fork项目
2. 创建分支: `git checkout -b feature/your-feature`
3. 提交更改: `git commit -m "Add your feature"`
4. 推送分支: `git push origin feature/your-feature`
5. 创建Pull Request

详细指南: [贡献指南](../CONTRIBUTING.md)

---

## 🌐 代理配置问题

### Q21: VSCode中显示"禁用代理设置"怎么办？

**问题描述**：
在终端直接运行Python时代理正常工作，但在VSCode中运行时显示"禁用代理设置"。

**根本原因**：
- 代理环境变量仅在当前终端会话中有效
- VSCode作为独立应用程序启动时，不会自动继承终端的环境变量
- 需要将代理配置写入shell配置文件

**解决方案**：

**方案1: 设置系统代理（推荐）**
```bash
# 写入shell配置文件
echo 'export http_proxy=http://127.0.0.1:10808/' >> ~/.zshrc
echo 'export https_proxy=http://127.0.0.1:10808/' >> ~/.zshrc
echo 'export HTTP_PROXY=http://127.0.0.1:10808/' >> ~/.zshrc
echo 'export HTTPS_PROXY=http://127.0.0.1:10808/' >> ~/.zshrc

# 重新加载配置
source ~/.zshrc  # 或 ~/.bashrc
```

**方案2: VSCode设置代理**
1. 打开VSCode设置 (Ctrl+,)
2. 搜索"proxy"
3. 设置：
   ```json
   {
       "http.proxy": "http://127.0.0.1:10808",
       "https.proxy": "http://127.0.0.1:10808",
       "http.proxyAuthorization": null
   }
   ```

**方案3: 重启VSCode**
```bash
# 在设置了环境变量的终端中启动VSCode
code .
```

### Q22: SSL连接问题如何解决？

**问题描述**：
某些网站在直接连接时出现SSL错误，需要通过代理访问。

**解决方案**：

**方案1: 配置代理**
```bash
export http_proxy=http://127.0.0.1:10808/
export https_proxy=http://127.0.0.1:10808/
python3 main.py --collect
```

**方案2: 更新证书**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ca-certificates
sudo update-ca-certificates

# macOS
brew install openssl
```

**方案3: 临时禁用SSL验证**
```python
# 已在代码中实现
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

### Q23: 环境变量大小写不一致怎么办？

**问题描述**：
系统中可能同时存在大小写环境变量，导致检测不一致。

**解决方案**：
```python
# 代码已修复，同时检查大小写
http_proxy = os.getenv("http_proxy") or os.getenv("HTTP_PROXY")
https_proxy = os.getenv("https_proxy") or os.getenv("HTTPS_PROXY")
```

**手动设置所有变量**：
```bash
export http_proxy=http://127.0.0.1:10808/
export https_proxy=http://127.0.0.1:10808/
export HTTP_PROXY=http://127.0.0.1:10808/
export HTTPS_PROXY=http://127.0.0.1:10808/
```

---

## 🔗 相关资源

- [V2Ray官方文档](https://www.v2ray.com/)
- [Clash文档](https://github.com/Dreamacro/clash/wiki)
- [V2RayN使用教程](https://github.com/2dust/v2rayN/wiki)
- [ClashX使用教程](https://github.com/yichengchen/clashX/wiki)

---

**仍有问题？** 请在GitHub提交Issue或讨论。
