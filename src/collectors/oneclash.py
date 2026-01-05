#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OneClash 爬虫
"""

import re
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
from .base_collector import BaseCollector
from config.websites import SUBSCRIPTION_PATTERNS, SUBSCRIPTION_KEYWORDS, UNIVERSAL_SELECTORS

class OneClashCollector(BaseCollector):
    """OneClash 专用爬虫"""
    
    def __init__(self, site_config):
        super().__init__(site_config)
        # 添加额外的请求头以绕过反爬虫
        self.session.headers.update({
            'Referer': 'https://oneclash.cc/',
            'Origin': 'https://oneclash.cc',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        })
    
    def _make_request(self, url, method='GET', **kwargs):
        """重写请求方法，添加随机延迟"""
        # 添加随机延迟以模拟人类行为
        time.sleep(random.uniform(1, 2))
        
        # 调用父类方法
        return super()._make_request(url, method, **kwargs)
    
    def get_latest_article_url(self, target_date=None):
        """获取文章URL，支持指定日期"""
        try:
            self.logger.info(f"访问网站: {self.base_url}")
            response = self._make_request(self.base_url)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 默认使用今天作为目标日期
            if target_date is None:
                target_date = datetime.now()
            
            # 生成多种日期格式用于匹配
            date_str = target_date.strftime('%Y-%m-%d')
            date_str_alt = target_date.strftime('%Y/%m/%d')
            date_str_month_day_cn = f'{target_date.month}月{target_date.day}日'
            date_str_month_day_cn_alt = f'{target_date.month:02d}月{target_date.day:02d}日'
            date_str_month_day = target_date.strftime('%m-%d')
            date_str_year_month = target_date.strftime('%Y-%m')
            date_str_year_month_cn = f'{target_date.year}年{target_date.month:02d}月{target_date.day:02d}日'
            
            # 优先通过日期匹配查找文章
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                # 检查链接文本或URL中是否包含今天的日期
                if href and (date_str in href or date_str_alt in href or
                           date_str_month_day_cn in text or date_str_month_day_cn_alt in text or
                           date_str_year_month_cn in text or date_str in text or
                           date_str_month_day in text or date_str_year_month in href):
                    # 排除导航链接（只选择文章链接）
                    if href and not any(x in href for x in ['category', 'tag', 'page', 'search', 'about', 'feed']):
                        article_url = self._process_url(href)
                        self.logger.info(f"通过日期匹配找到文章: {article_url}")
                        return article_url
            
            # 如果日期匹配失败，尝试特定选择器
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
            
            # 如果都没找到，返回None
            self.logger.warning(f"未找到文章链接")
            return None
            
        except Exception as e:
            self.logger.error(f"获取文章链接失败: {str(e)}")
            return None
    
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
            if (clean_link and clean_link not in seen and 
                self._is_valid_url(clean_link) and 
                self._is_valid_subscription_link(clean_link)):
                cleaned_links.append(clean_link)
                seen.add(clean_link)
        
        return cleaned_links