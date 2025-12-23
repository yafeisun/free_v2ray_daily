#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础爬虫类
"""

import requests
import re
import time
import os
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from abc import ABC, abstractmethod
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from config.settings import *
from config.websites import *
from src.utils.logger import get_logger

class BaseCollector(ABC):
    """基础爬虫抽象类"""
    
    def __init__(self, site_config):
        self.site_config = site_config
        self.site_name = site_config["name"]
        self.base_url = site_config["url"]
        self.enabled = site_config.get("enabled", True)
        self.last_article_url = None  # 记录最后访问的文章URL
        
        # 设置日志
        self.logger = get_logger(f"collector.{self.site_name}")
        
        # 创建会话
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT
        })
        
        # 配置参数
        self.timeout = REQUEST_TIMEOUT
        self.retry_count = REQUEST_RETRY
        self.delay = REQUEST_DELAY
        
        # 存储结果
        self.collected_nodes = []
        self.subscription_links = []
        self.raw_data = ""
        
    def collect(self):
        """收集节点的主方法"""
        if not self.enabled:
            self.logger.info(f"{self.site_name} 已禁用，跳过收集")
            return []
        
        try:
            self.logger.info(f"开始收集 {self.site_name} 的节点")
            
            # 获取最新文章URL
            article_url = self.get_latest_article_url()
            if not article_url:
                self.logger.warning(f"{self.site_name}: 未找到最新文章")
                return []
            
            # 记录文章URL
            self.last_article_url = article_url
            
            # 提取节点信息
            nodes = self.extract_nodes_from_article(article_url)
            
            # 保存原始数据
            self.save_raw_data(article_url)
            
            self.logger.info(f"{self.site_name}: 收集到 {len(nodes)} 个节点")
            return nodes
            
        except Exception as e:
            self.logger.error(f"{self.site_name}: 收集失败 - {str(e)}")
            return []
    
    def get_latest_article_url(self, target_date=None):
        """获取文章URL，支持指定日期"""
        try:
            self.logger.info(f"访问网站: {self.base_url}")
            response = self.session.get(self.base_url, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 如果指定了目标日期，优先查找该日期的文章
            if target_date:
                date_str = target_date.strftime('%Y-%m-%d')
                date_str_alt = target_date.strftime('%Y/%m/%d')
                date_str_month_day = target_date.strftime('%m-%d')
                
                # 查找包含目标日期的链接
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    
                    if href and (date_str in href or date_str_alt in href or 
                               date_str_month_day in text or date_str in text):
                        article_url = self._process_url(href)
                        self.logger.info(f"通过日期匹配找到文章: {article_url}")
                        return article_url
            
            # 尝试特定选择器
            selectors = self.site_config.get("selectors", [])
            links = []
            
            for selector in selectors:
                links = soup.select(selector)
                if links:
                    href = links[0].get('href')
                    if href:
                        article_url = self._process_url(href)
                        self.logger.info(f"通过选择器找到文章: {article_url}")
                        return article_url
            
            # 尝试通用选择器
            for selector in UNIVERSAL_SELECTORS:
                links = soup.select(selector)
                if links:
                    href = links[0].get('href')
                    if href:
                        article_url = self._process_url(href)
                        self.logger.info(f"通过通用选择器找到文章: {article_url}")
                        return article_url
            
            # 尝试查找今日链接
            today_url = self._find_today_article(soup)
            if today_url:
                return today_url
            
            # 尝试通过时间查找
            time_url = self._find_by_time(soup)
            if time_url:
                return time_url
            
            # 如果都没找到，返回主页URL
            self.logger.warning(f"未找到文章链接，使用主页URL")
            return self.base_url
            
        except Exception as e:
            self.logger.error(f"获取文章链接失败: {str(e)}")
            return None
    
    def extract_nodes_from_article(self, article_url):
        """从文章中提取节点"""
        try:
            self.logger.info(f"解析文章: {article_url}")
            response = self.session.get(article_url, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            content = response.text
            self.raw_data = content
            
            # 查找订阅链接
            subscription_links = self.find_subscription_links(content)
            self.subscription_links = subscription_links
            
            nodes = []
            
            # 从订阅链接获取节点
            for link in subscription_links:
                self.logger.info(f"找到订阅链接: {link}")
                sub_nodes = self.get_nodes_from_subscription(link)
                nodes.extend(sub_nodes)
                time.sleep(self.delay)  # 避免请求过快
            
            # 直接从页面提取节点
            direct_nodes = self.extract_direct_nodes(content)
            nodes.extend(direct_nodes)
            
            # 去重
            nodes = list(set(nodes))
            
            return nodes
            
        except Exception as e:
            self.logger.error(f"解析文章失败: {str(e)}")
            return []
    
    def find_subscription_links(self, content):
        """查找订阅链接"""
        links = []
        
        # 使用特定网站的模式
        patterns = self.site_config.get("patterns", [])
        for pattern in patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                links.extend(matches)
            except Exception as e:
                self.logger.warning(f"模式匹配失败: {pattern} - {str(e)}")
        
        # 使用通用订阅模式
        for pattern in SUBSCRIPTION_PATTERNS:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        links.extend(match)
                    else:
                        links.append(match)
            except Exception as e:
                self.logger.warning(f"通用模式匹配失败: {pattern} - {str(e)}")
        
        # 在关键词附近查找
        for keyword in SUBSCRIPTION_KEYWORDS:
            try:
                pattern = rf'{keyword}[^:]*[:：]\s*(https?://[^\s\n\r]+)'
                matches = re.findall(pattern, content, re.IGNORECASE)
                links.extend(matches)
            except:
                pass
        
        # 清理和去重
        cleaned_links = []
        seen = set()
        
        for link in links:
            clean_link = self._clean_link(link)
            if clean_link and clean_link not in seen and self._is_valid_url(clean_link):
                cleaned_links.append(clean_link)
                seen.add(clean_link)
        
        return cleaned_links
    
    def get_nodes_from_subscription(self, subscription_url):
        """从订阅链接获取节点"""
        try:
            self.logger.info(f"获取订阅内容: {subscription_url}")
            response = self.session.get(subscription_url, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            content = response.text.strip()
            nodes = self.parse_node_text(content)
            
            self.logger.info(f"从订阅链接获取到 {len(nodes)} 个节点")
            return nodes
            
        except Exception as e:
            self.logger.error(f"获取订阅链接失败: {str(e)}")
            return []
    
    def get_v2ray_subscription_links(self, article_url):
        """获取V2Ray订阅链接"""
        try:
            self.logger.info(f"解析文章: {article_url}")
            response = self.session.get(article_url, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            content = response.text
            
            # 查找所有订阅链接
            subscription_links = self.find_subscription_links(content)
            
            # 过滤出V2Ray订阅链接
            v2ray_links = []
            for link in subscription_links:
                if self.is_v2ray_subscription(link):
                    v2ray_links.append(link)
            
            self.logger.info(f"从文章中找到 {len(v2ray_links)} 个V2Ray订阅链接")
            return v2ray_links
            
        except Exception as e:
            self.logger.error(f"获取V2Ray订阅链接失败: {str(e)}")
            return []
    
    def is_v2ray_subscription(self, url):
        """判断是否为V2Ray订阅链接"""
        try:
            # 订阅链接通常以http开头
            if not url.startswith('http'):
                return False
            
            from urllib.parse import urlparse
            parsed = urlparse(url)
            path_part = parsed.path.lower()
            
            # 必须以.txt结尾（V2Ray格式）
            if not path_part.endswith('.txt'):
                return False
            
            # 排除明显的Clash和Sing-Box订阅链接
            excluded_keywords = [
                'sing-box', 'singbox', 'yaml', 'yml',
                'clash免费节点', 'sing-box免费节点', 'Clash免费节点', 'Sing-Box免费节点'
            ]
            
            # 只检查路径部分，不检查域名
            for keyword in excluded_keywords:
                if keyword in path_part:
                    return False
            
            # 检查是否包含V2Ray相关关键词
            v2ray_keywords = ['v2ray', 'sub', 'subscribe', 'node', 'link']
            for keyword in v2ray_keywords:
                if keyword in path_part:
                    return True
            
            return True
            
        except:
            return False
    
    def extract_direct_nodes(self, content):
        """直接从页面内容提取节点"""
        nodes = []
        
        # 使用标准节点模式
        for pattern in NODE_PATTERNS:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    node = match.strip()
                    if len(node) >= MIN_NODE_LENGTH:
                        nodes.append(node)
            except Exception as e:
                self.logger.warning(f"节点模式匹配失败: {pattern} - {str(e)}")
        
        # 从代码块中提取
        for selector in CODE_BLOCK_SELECTORS:
            try:
                matches = re.findall(selector, content, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    block_nodes = self.parse_node_text(match)
                    nodes.extend(block_nodes)
            except Exception as e:
                self.logger.warning(f"代码块匹配失败: {selector} - {str(e)}")
        
        # 从Base64内容中提取
        for pattern in BASE64_PATTERNS:
            try:
                matches = re.findall(pattern, content)
                for match in matches:
                    try:
                        import base64
                        decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                        if any(proto in decoded.lower() for proto in SUPPORTED_PROTOCOLS):
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
        
        for pattern in NODE_PATTERNS:
            try:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    node = match.strip()
                    if node and len(node) >= MIN_NODE_LENGTH:
                        nodes.append(node)
            except Exception as e:
                self.logger.warning(f"节点解析失败: {pattern} - {str(e)}")
        
        return list(set(nodes))  # 去重
    
    def save_raw_data(self, article_url):
        """保存原始数据"""
        try:
            if not os.path.exists(RAW_DATA_DIR):
                os.makedirs(RAW_DATA_DIR)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.site_name}_{timestamp}.html"
            filepath = os.path.join(RAW_DATA_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"<!-- URL: {article_url} -->\n")
                f.write(f"<!-- Time: {datetime.now().isoformat()} -->\n")
                f.write(self.raw_data)
            
            self.logger.info(f"原始数据已保存: {filepath}")
            
        except Exception as e:
            self.logger.error(f"保存原始数据失败: {str(e)}")
    
    def _process_url(self, url):
        """处理URL"""
        if url.startswith('/'):
            return urljoin(self.base_url, url)
        return url
    
    def _find_today_article(self, soup):
        """查找今日文章"""
        try:
            today = datetime.now()
            date_patterns = [
                f"{today.month}-{today.day}",
                f"{today.year}-{today.month}-{today.day}",
                f"{today.month}月{today.day}日",
                f"{today.year}年{today.month}月{today.day}日"
            ]
            
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href')
                text = link.get_text().strip()
                
                for pattern in date_patterns:
                    if pattern in text:
                        article_url = self._process_url(href)
                        self.logger.info(f"找到今日文章: {article_url}")
                        return article_url
            
            return None
            
        except Exception as e:
            self.logger.error(f"查找今日文章失败: {str(e)}")
            return None
    
    def _find_by_time(self, soup):
        """通过时间查找文章"""
        try:
            for time_selector in TIME_SELECTORS:
                time_elements = soup.select(time_selector)
                if time_elements:
                    for time_elem in time_elements:
                        parent = time_elem.find_parent(['article', '.post', '.entry'])
                        if parent:
                            article_link = parent.find('a')
                            if article_link and article_link.get('href'):
                                article_url = self._process_url(article_link.get('href'))
                                self.logger.info(f"通过时间找到文章: {article_url}")
                                return article_url
            
            return None
            
        except Exception as e:
            self.logger.error(f"通过时间查找文章失败: {str(e)}")
            return None
    
    def _clean_link(self, link):
        """清理链接"""
        if not link:
            return ""
        
        # 移除HTML标签和无效字符
        clean_link = re.sub(r'<[^>]+>', '', link)
        clean_link = re.sub(r'["\'`<>]', '', clean_link).strip()
        
        # 处理常见的错误链接格式
        for suffix in ['/strong', '/span', '/pp', '/h3', '&nbsp;', '/div', 'div']:
            if suffix in clean_link:
                clean_link = clean_link.split(suffix)[0]
        
        # 移除末尾的无效字符
        clean_link = clean_link.rstrip(';/')
        
        return clean_link.strip()
    
    def _is_valid_url(self, url):
        """验证URL是否有效"""
        try:
            url_pattern = re.compile(
                r'^https?://'
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
                r'localhost|'
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                r'(?::\d+)?'
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            return url_pattern.match(url) is not None
        except:
            return False