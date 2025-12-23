#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
免费节点收集器
从多个网站收集免费节点信息，进行测速并更新到GitHub
"""

import requests
import re
import base64
import json
import time
import socket
import concurrent.futures
from datetime import datetime
from bs4 import BeautifulSoup
import urllib3
import os
import sys
import git
from config import *

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NodeCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = REQUEST_TIMEOUT
        self.max_workers = MAX_WORKERS
        
        # 目标网站列表
        self.websites = WEBSITES
        
        # 存储所有节点
        self.all_nodes = []
        
    def get_latest_article_url(self, website_url):
        """获取网站最新文章URL"""
        try:
            print(f"正在访问网站: {website_url}")
            response = self.session.get(website_url, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 根据不同网站使用特定的选择器
            if 'freeclashnode.com' in website_url:
                selectors = [
                    '.post-title a',
                    'h2 a',
                    '.entry-title a',
                    'article h2 a'
                ]
            elif 'mibei77.com' in website_url:
                selectors = [
                    '.post h2 a',
                    '.entry-title a',
                    'h1 a',
                    '.post-title a'
                ]
            elif 'clashnodev2ray.github.io' in website_url:
                selectors = [
                    'h1 a',
                    '.post-title a',
                    'article h1 a',
                    'h2 a'
                ]
            elif 'proxyqueen.top' in website_url:
                selectors = [
                    '.post-title a',
                    'h2 a',
                    '.entry-header a',
                    'article h2 a'
                ]
            elif 'wanzhuanmi.com' in website_url:
                selectors = [
                    '.post-title a',
                    'h2 a',
                    '.entry-title a',
                    'article h2 a'
                ]
            else:
                # 通用选择器
                selectors = [
                    'article:first-child a',
                    '.post:first-child a',
                    '.entry-title:first-child a',
                    'h1 a',
                    'h2:first-child a',
                    '.latest-post a',
                    'a[href*="/post/"]',
                    'a[href*="/article/"]',
                    'a[href*="/node/"]',
                    'a[href*="/free/"]'
                ]
            
            # 尝试选择器
            for selector in selectors:
                links = soup.select(selector)
                if links:
                    href = links[0].get('href')
                    if href:
                        # 处理相对链接
                        if href.startswith('/'):
                            from urllib.parse import urljoin
                            href = urljoin(website_url, href)
                        print(f"找到文章链接: {href}")
                        return href
            
            # 如果没有找到特定选择器，尝试查找包含日期的链接
            all_links = soup.find_all('a', href=True)
            today_links = []
            
            for link in all_links:
                href = link.get('href')
                text = link.get_text().strip()
                # 查找包含今天日期的链接
                if self.contains_today_date(text):
                    if href.startswith('/'):
                        from urllib.parse import urljoin
                        href = urljoin(website_url, href)
                    today_links.append((href, text))
            
            # 如果找到今日链接，选择第一个
            if today_links:
                href, text = today_links[0]
                print(f"找到今日文章链接: {href} - {text}")
                return href
            
            # 尝试查找最新发布的文章（通过时间标签）
            time_selectors = [
                'time',
                '.post-date',
                '.entry-date',
                '.published',
                '[datetime]'
            ]
            
            for time_selector in time_selectors:
                time_elements = soup.select(time_selector)
                if time_elements:
                    # 找到最新时间元素对应的文章链接
                    for time_elem in time_elements:
                        parent = time_elem.find_parent(['article', '.post', '.entry'])
                        if parent:
                            article_link = parent.find('a')
                            if article_link and article_link.get('href'):
                                href = article_link.get('href')
                                if href.startswith('/'):
                                    from urllib.parse import urljoin
                                    href = urljoin(website_url, href)
                                print(f"通过时间找到文章链接: {href}")
                                return href
            
            print(f"未找到文章链接，尝试直接解析当前页面")
            return website_url
            
        except Exception as e:
            print(f"获取 {website_url} 文章链接失败: {str(e)}")
            return None
    
    def contains_today_date(self, text):
        """检查文本是否包含今天的日期"""
        today = datetime.now()
        date_patterns = [
            f"{today.month}-{today.day}",
            f"{today.year}-{today.month}-{today.day}",
            f"{today.month}月{today.day}日",
            f"{today.year}年{today.month}月{today.day}日"
        ]
        
        for pattern in date_patterns:
            if pattern in text:
                return True
        return False
    
    def extract_nodes_from_article(self, article_url):
        """从文章中提取节点信息"""
        try:
            print(f"正在解析文章: {article_url}")
            response = self.session.get(article_url, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            content = response.text
            
            # 查找订阅链接
            subscription_links = self.find_subscription_links(content)
            nodes = []
            
            # 如果找到订阅链接，获取订阅内容
            for link in subscription_links:
                print(f"找到订阅链接: {link}")
                sub_nodes = self.get_nodes_from_subscription(link)
                nodes.extend(sub_nodes)
            
            # 直接从页面内容提取节点
            direct_nodes = self.extract_direct_nodes(content)
            nodes.extend(direct_nodes)
            
            print(f"从文章中提取到 {len(nodes)} 个节点")
            return nodes
            
        except Exception as e:
            print(f"解析文章 {article_url} 失败: {str(e)}")
            return []
    
    def find_subscription_links(self, content):
        """查找订阅链接"""
        links = []
        
        # 首先处理被HTML标签污染的链接（如freeclashnode.com的情况）
        links.extend(self._extract_polluted_links(content))
        
        # 然后使用标准模式查找
        links.extend(self._extract_standard_links(content))
        
        # 最后在关键词附近查找
        links.extend(self._extract_keyword_links(content))
        
        # 去重并过滤
        unique_links = []
        seen = set()
        for link in links:
            clean_link = self._clean_link(link)
            if clean_link and clean_link not in seen and self.is_valid_url(clean_link):
                unique_links.append(clean_link)
                seen.add(clean_link)
        
        return unique_links
    
    def _extract_polluted_links(self, content):
        """提取被HTML标签污染的链接"""
        links = []
        
        # 首先处理freeclashnode.com的特殊格式
        # 查找所有node.freeclashnode.com的URL片段
        pattern = r'node\.freeclashnode\.com/uploads/\d{4}/\d{2}/[^\\s\\<]*'
        matches = re.findall(pattern, content, re.IGNORECASE)
        
        # 为每个匹配找到完整的URL
        for match in matches:
            # 尝试不同的文件扩展名
            for ext in ['.txt', '.yaml', '.json']:
                # 构建基础URL模式
                base_pattern = f'(https?://{match}[^\\s]*)'
                base_matches = re.findall(base_pattern, content, re.IGNORECASE)
                
                for base_match in base_matches:
                    # 清理URL
                    clean_url = base_match
                    # 移除污染部分
                    for separator in ['pp', 'Clash免费节点', 'Sing-Box免费节点:', 'strong', 'span']:
                        if separator in clean_url:
                            clean_url = clean_url.split(separator)[0]
                    
                    # 确保以正确的扩展名结尾
                    if not clean_url.endswith(ext):
                        # 尝试找到正确的结尾位置
                        if ext in clean_url:
                            # 截取到扩展名位置
                            ext_pos = clean_url.find(ext)
                            clean_url = clean_url[:ext_pos + len(ext)]
                        else:
                            continue
                    
                    # 验证URL格式
                    if clean_url.endswith(ext) and len(clean_url) > 40:
                        links.append(clean_url)
        
        # 备用方法：手动解析特定的污染字符串
        if 'node.freeclashnode.com' in content:
            # 查找所有以https://node.freeclashnode.com开头的部分
            parts = content.split('https://node.freeclashnode.com')
            for i, part in enumerate(parts[1:], 1):  # 跳过第一个空部分
                # 查找下一个分隔符
                separators = ['pphttps://', 'Clash免费节点https://', 'Sing-Box免费节点:https://', 'stronghttps://', 'spanhttps://']
                clean_part = part
                
                for sep in separators:
                    if sep in clean_part:
                        clean_part = clean_part.split(sep)[0]
                        break
                
                # 尝试不同的文件扩展名
                candidate = 'https://node.freeclashnode.com' + clean_part
                for ext in ['.txt', '.yaml', '.json']:
                    if ext in candidate:
                        ext_pos = candidate.find(ext)
                        final_url = candidate[:ext_pos + len(ext)]
                        if final_url not in links and len(final_url) > 40:
                            links.append(final_url)
        
        # 查找其他网站的订阅链接
        other_patterns = [
            r'v2clash\.blog/Link/[^\\s\\<]+\\.(?:txt|yaml|json)',
        ]
        
        for pattern in other_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                full_url = 'https://' + match
                # 清理污染
                for suffix in ['pp', 'strong', 'span', '/h3', 'clash订阅链接：']:
                    if suffix in full_url:
                        full_url = full_url.split(suffix)[0]
                
                if full_url not in links and len(full_url) > 20:
                    links.append(full_url)
        
        return links
    
    def _extract_standard_links(self, content):
        """提取标准格式的链接"""
        links = []
        patterns = [
            # 标准订阅链接
            r'https?://[^\s\'"\.]*\.?[^\s\'"]*(?:/sub|/subscribe|/link|/api|/node|/v2)[^\s\'"]*',
            # 包含协议名称的链接
            r'https?://[^\s\'"]*?[^\s\'"]*(?:vmess|vless|trojan|hysteria|shadowsocks|ss)[^\s\'"]*',
            # 引号内的订阅链接
            r'["\']((?:https?://[^\s\'"]*?/sub[^\s\'"]*?))["\']',
            r'["\']((?:https?://[^\s\'"]*?/subscribe[^\s\'"]*?))["\']',
            r'["\']((?:https?://[^\s\'"]*?/link[^\s\'"]*?))["\']',
            r'["\']((?:https?://[^\s\'"]*?/api[^\s\'"]*?))["\']',
            # 特殊格式的链接
            r'https?://[^\s\'"]*?\.(?:top|com|org|net|io|gg|tk|ml)[^\s\'"]*(?:/sub|/api|/link)[^\s\'"]*',
            # 包含端口的链接
            r'https?://[^\s\'"]*:\d+[^\s\'"]*(?:/sub|/api|/link)[^\s\'"]*'
        ]
        
        for pattern in patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        links.extend(match)
                    else:
                        links.append(match)
            except Exception as e:
                print(f"正则匹配失败: {pattern} - {str(e)}")
        
        return links
    
    def _extract_keyword_links(self, content):
        """在关键词附近查找链接"""
        links = []
        keywords = ['订阅', 'subscription', 'sub', 'link', '节点', 'nodes', '配置', 'config']
        
        for keyword in keywords:
            try:
                pattern = rf'{keyword}[^:]*[:：]\s*(https?://[^\s\n\r]+)'
                matches = re.findall(pattern, content, re.IGNORECASE)
                links.extend(matches)
            except:
                pass
        
        return links
    
    def _clean_link(self, link):
        """清理链接"""
        if not link:
            return ""
        
        # 移除HTML标签和无效字符
        clean_link = re.sub(r'<[^>]+>', '', link)  # 移除HTML标签
        clean_link = re.sub(r'["\'`<>]', '', clean_link).strip()  # 移除特殊字符
        
        # 处理常见的错误链接格式
        for suffix in ['/strong', '/span', '/pp', '/h3', '&nbsp;']:
            if suffix in clean_link:
                clean_link = clean_link.split(suffix)[0]
        
        # 移除末尾的无效字符
        clean_link = clean_link.rstrip(';/')
        
        return clean_link.strip()
    
    def is_valid_url(self, url):
        """验证URL是否有效"""
        try:
            import re
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            return url_pattern.match(url) is not None
        except:
            return False
    
    def get_nodes_from_subscription(self, subscription_url):
        """从订阅链接获取节点"""
        try:
            print(f"正在获取订阅内容: {subscription_url}")
            response = self.session.get(subscription_url, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            content = response.text.strip()
            
            # 如果是base64编码，先解码
            try:
                decoded_content = base64.b64decode(content).decode('utf-8')
                nodes = self.parse_node_text(decoded_content)
            except:
                # 如果不是base64，直接解析
                nodes = self.parse_node_text(content)
            
            return nodes
            
        except Exception as e:
            print(f"获取订阅链接 {subscription_url} 失败: {str(e)}")
            return []
    
    def extract_direct_nodes(self, content):
        """直接从页面内容提取节点"""
        nodes = []
        
        # 首先使用标准方法提取
        standard_nodes = self.parse_node_text(content)
        nodes.extend(standard_nodes)
        
        # 尝试从代码块中提取
        code_blocks = re.findall(r'<(?:code|pre)[^>]*>(.*?)</(?:code|pre)>', content, re.DOTALL | re.IGNORECASE)
        for block in code_blocks:
            block_nodes = self.parse_node_text(block)
            nodes.extend(block_nodes)
        
        # 尝试从常见的节点展示区域提取
        content_areas = [
            r'<div[^>]*class="[^"]*(?:node|config|subscription)[^"]*"[^>]*>(.*?)</div>',
            r'<textarea[^>]*>(.*?)</textarea>',
            r'<input[^>]*value="([^"]*(?:vmess|vless|trojan|hysteria|ss://)[^"]*)"',
        ]
        
        for pattern in content_areas:
            try:
                matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    area_nodes = self.parse_node_text(match)
                    nodes.extend(area_nodes)
            except:
                pass
        
        # 尝试从Base64编码的内容中提取
        base64_patterns = [
            r'([A-Za-z0-9+/]{50,}={0,2})',
        ]
        
        for pattern in base64_patterns:
            try:
                matches = re.findall(pattern, content)
                for match in matches:
                    try:
                        # 尝试解码base64
                        import base64
                        decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                        if any(proto in decoded.lower() for proto in ['vmess://', 'vless://', 'trojan://', 'hysteria', 'ss://']):
                            decoded_nodes = self.parse_node_text(decoded)
                            nodes.extend(decoded_nodes)
                    except:
                        pass
            except:
                pass
        
        return list(set(nodes))  # 去重
    
    def parse_node_text(self, text):
        """解析文本中的节点信息"""
        nodes = []
        
        # 节点协议模式
        patterns = [
            r'(vmess://[^\s\n\r]+)',
            r'(vless://[^\s\n\r]+)',
            r'(trojan://[^\s\n\r]+)',
            r'(hysteria2://[^\s\n\r]+)',
            r'(hysteria://[^\s\n\r]+)',
            r'(ss://[^\s\n\r]+)',
            r'(ssr://[^\s\n\r]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                node = match.strip()
                if node and len(node) > 20:  # 确保是有效的节点链接
                    nodes.append(node)
        
        return list(set(nodes))  # 去重
    
    def test_node_connectivity(self, node):
        """测试节点连通性"""
        try:
            # 从节点链接中提取主机和端口
            if node.startswith('vmess://'):
                return self.test_vmess_node(node)
            elif node.startswith('vless://'):
                return self.test_vless_node(node)
            elif node.startswith('trojan://'):
                return self.test_trojan_node(node)
            elif node.startswith('hysteria2://') or node.startswith('hysteria://'):
                return self.test_hysteria_node(node)
            elif node.startswith('ss://'):
                return self.test_shadowsocks_node(node)
            else:
                return False
        except Exception as e:
            return False
    
    def test_vmess_node(self, node):
        """测试VMess节点"""
        try:
            # 解码base64
            import base64
            import json
            data = node[8:]  # 去掉 vmess://
            decoded = json.loads(base64.b64decode(data + '==').decode('utf-8'))
            host = decoded.get('add')
            port = int(decoded.get('port', 0))
            
            if host and port:
                return self.test_connection(host, port)
        except:
            pass
        return False
    
    def test_vless_node(self, node):
        """测试VLESS节点"""
        try:
            # 解析VLESS链接
            import re
            pattern = r'vless://([^@]+)@([^:]+):(\d+)'
            match = re.search(pattern, node)
            if match:
                host = match.group(2)
                port = int(match.group(3))
                return self.test_connection(host, port)
        except:
            pass
        return False
    
    def test_trojan_node(self, node):
        """测试Trojan节点"""
        try:
            # 解析Trojan链接
            import re
            pattern = r'trojan://([^@]+)@([^:]+):(\d+)'
            match = re.search(pattern, node)
            if match:
                host = match.group(2)
                port = int(match.group(3))
                return self.test_connection(host, port)
        except:
            pass
        return False
    
    def test_hysteria_node(self, node):
        """测试Hysteria节点"""
        try:
            # 解析Hysteria链接
            import re
            pattern = r'hysteria2?://[^@]*@([^:]+):(\d+)'
            match = re.search(pattern, node)
            if match:
                host = match.group(1)
                port = int(match.group(2))
                return self.test_connection(host, port)
        except:
            pass
        return False
    
    def test_shadowsocks_node(self, node):
        """测试Shadowsocks节点"""
        try:
            # 解析SS链接
            import base64
            data = node[5:]  # 去掉 ss://
            decoded = base64.b64decode(data).decode('utf-8')
            parts = decoded.split('@')
            if len(parts) >= 2:
                host_port = parts[1].split(':')[0]
                if ':' in host_port:
                    host, port = host_port.rsplit(':', 1)
                    return self.test_connection(host, int(port))
        except:
            pass
        return False
    
    def test_connection(self, host, port, timeout=None):
        """测试TCP连接"""
        try:
            if timeout is None:
                timeout = CONNECTION_TIMEOUT
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def test_all_nodes(self, nodes):
        """批量测试所有节点"""
        print(f"开始测试 {len(nodes)} 个节点的连通性...")
        valid_nodes = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_node = {executor.submit(self.test_node_connectivity, node): node for node in nodes}
            
            for future in concurrent.futures.as_completed(future_to_node):
                node = future_to_node[future]
                try:
                    is_valid = future.result()
                    if is_valid:
                        valid_nodes.append(node)
                        print(f"✓ 节点有效: {node[:50]}...")
                    else:
                        print(f"✗ 节点无效: {node[:50]}...")
                except Exception as e:
                    print(f"✗ 测试节点失败: {node[:50]}... - {str(e)}")
        
        print(f"测试完成，有效节点: {len(valid_nodes)}/{len(nodes)}")
        return valid_nodes
    
    def collect_nodes(self):
        """收集所有网站的节点"""
        print("开始收集节点...")
        
        for website in self.websites:
            try:
                article_url = self.get_latest_article_url(website)
                if article_url:
                    nodes = self.extract_nodes_from_article(article_url)
                    self.all_nodes.extend(nodes)
                    print(f"从 {website} 收集到 {len(nodes)} 个节点")
                time.sleep(REQUEST_DELAY)  # 避免请求过快
            except Exception as e:
                print(f"处理网站 {website} 时出错: {str(e)}")
        
        # 去重
        self.all_nodes = list(set(self.all_nodes))
        print(f"总共收集到 {len(self.all_nodes)} 个节点")
        
        # 测试节点连通性
        valid_nodes = self.test_all_nodes(self.all_nodes)
        
        return valid_nodes
    
    def save_nodes_to_file(self, nodes, filename):
        """保存节点到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for node in nodes:
                    f.write(node + '\n')
            print(f"节点已保存到 {filename}")
        except Exception as e:
            print(f"保存节点失败: {str(e)}")
    
    def update_github(self, nodes):
        """更新GitHub仓库"""
        try:
            # 获取当前脚本所在目录
            repo_path = os.path.dirname(os.path.abspath(__file__))
            
            # 切换到仓库目录
            os.chdir(repo_path)
            
            # 保存节点到文件
            self.save_nodes_to_file(nodes, 'nodelist.txt')
            
            # Git操作
            repo = git.Repo(repo_path)
            
            # 设置Git配置
            with repo.config_writer() as cw:
                cw.set_value('user', 'email', GIT_EMAIL)
                cw.set_value('user', 'name', GIT_NAME)
            
            # 添加文件到暂存区
            repo.index.add(['nodelist.txt'])
            
            # 提交更改
            commit_message = f"更新节点列表 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            repo.index.commit(commit_message)
            
            # 推送到远程仓库
            origin = repo.remote(name='origin')
            origin.push()
            
            print(f"成功更新GitHub仓库，提交信息: {commit_message}")
            
        except Exception as e:
            print(f"更新GitHub失败: {str(e)}")

def main():
    collector = NodeCollector()
    
    print("=" * 50)
    print("免费节点收集器启动")
    print("=" * 50)
    
    # 收集节点
    valid_nodes = collector.collect_nodes()
    
    if valid_nodes:
        # 更新GitHub
        collector.update_github(valid_nodes)
        print(f"任务完成！更新了 {len(valid_nodes)} 个有效节点")
    else:
        print("未找到有效节点")

if __name__ == "__main__":
    main()