#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序入口
"""

import sys
import os
import time
import re
from datetime import datetime, timedelta
from src.utils.logger import get_logger
from src.utils.file_handler import FileHandler
from src.testers.connectivity_tester import ConnectivityTester
from config.settings import *
from config.websites import WEBSITES

# 导入各个网站的爬虫
from src.collectors.freeclashnode import FreeClashNodeCollector
from src.collectors.mibei77 import Mibei77Collector
from src.collectors.clashnodev2ray import ClashNodeV2RayCollector
from src.collectors.proxyqueen import ProxyQueenCollector
from src.collectors.wanzhuanmi import WanzhuanmiCollector
from src.collectors.cfmem import CfmemCollector

class NodeCollector:
    """节点收集器主类"""
    
    def __init__(self):
        self.logger = get_logger("main")
        self.file_handler = FileHandler()
        self.connectivity_tester = ConnectivityTester()
        
        # 初始化爬虫
        self.collectors = {
            "freeclashnode": FreeClashNodeCollector(WEBSITES["freeclashnode"]),
            "mibei77": Mibei77Collector(WEBSITES["mibei77"]),
            "clashnodev2ray": ClashNodeV2RayCollector(WEBSITES["clashnodev2ray"]),
            "proxyqueen": ProxyQueenCollector(WEBSITES["proxyqueen"]),
            "wanzhuanmi": WanzhuanmiCollector(WEBSITES["wanzhuanmi"]),
            "cfmem": CfmemCollector(WEBSITES["cfmem"])
        }
        
        self.all_nodes = []
        self.v2ray_subscription_links = []
        self.v2ray_links_with_source = []
        self.articles_with_source = []
        self.source_info = {}
    
    def collect_all_nodes(self):
        """收集所有网站的节点"""
        self.logger.info("=" * 50)
        self.logger.info("开始收集节点")
        self.logger.info("=" * 50)
        
        start_time = time.time()
        today = datetime.now().strftime('%Y-%m-%d')
        
        for site_name, collector in self.collectors.items():
            try:
                self.logger.info(f"正在收集 {site_name} 的节点...")
                
                # 检查今天的缓存
                existing_articles = self._load_existing_articles(today)
                existing_subscriptions = self._load_existing_subscriptions(today)
                
                # 检查是否已有今天的文章链接
                existing_article = self._find_existing_article(existing_articles, site_name, today)
                if existing_article:
                    self.logger.info(f"跳过 {site_name} - 已找到今天的文章链接: {existing_article}")
                    collector.last_article_url = existing_article
                    
                    # 检查是否已有该文章的订阅链接
                    existing_v2ray_links = self._find_existing_subscriptions(existing_subscriptions, site_name, existing_article)
                    if existing_v2ray_links:
                        self.logger.info(f"跳过 {site_name} - 已找到该文章的 {len(existing_v2ray_links)} 个V2Ray订阅链接")
                        # 从订阅链接获取实际节点
                        nodes = self._get_nodes_from_subscription_links(existing_v2ray_links, collector)
                        v2ray_links = existing_v2ray_links
                    else:
                        # 需要获取订阅链接
                        v2ray_links = collector.get_v2ray_subscription_links(existing_article)
                        # 从订阅链接获取实际节点
                        nodes = self._get_nodes_from_subscription_links(v2ray_links, collector)
                else:
                    # 收集节点
                    nodes = collector.collect()
                    
                    # 收集V2Ray订阅链接
                    if hasattr(collector, 'last_article_url') and collector.last_article_url:
                        v2ray_links = collector.get_v2ray_subscription_links(collector.last_article_url)
                        # 从订阅链接获取实际节点
                        v2ray_nodes = self._get_nodes_from_subscription_links(v2ray_links, collector)
                        nodes.extend(v2ray_nodes)
                    else:
                        v2ray_links = []
                
                # 保存文章链接信息
                if hasattr(collector, 'last_article_url') and collector.last_article_url:
                    self.articles_with_source.append({
                        'website_name': site_name,
                        'article_url': collector.last_article_url,
                        'date': today
                    })
                
                # 记录V2Ray订阅链接信息
                if not v2ray_links:
                    self.v2ray_links_with_source.append({
                        'url': '# 无V2Ray订阅链接',
                        'source': site_name,
                        'source_url': collector.last_article_url if hasattr(collector, 'last_article_url') else 'N/A'
                    })
                else:
                    for link in v2ray_links:
                        self.v2ray_links_with_source.append({
                            'url': link,
                            'source': site_name,
                            'source_url': collector.last_article_url
                        })
                
                if nodes:
                    self.all_nodes.extend(nodes)
                    self.v2ray_subscription_links.extend(v2ray_links)
                    
                    self.source_info[site_name] = {
                        "count": len(nodes),
                        "enabled": collector.enabled,
                        "subscription_links": len(collector.subscription_links),
                        "v2ray_links": len(v2ray_links),
                        "links": collector.subscription_links[:5],
                        "v2ray_link_samples": v2ray_links[:5]
                    }
                    self.logger.info(f"{site_name} 收集完成: {len(nodes)} 个节点，{len(v2ray_links)} 个V2Ray订阅链接")
                else:
                    self.source_info[site_name] = {
                        "count": 0,
                        "enabled": collector.enabled,
                        "subscription_links": 0,
                        "v2ray_links": 0,
                        "links": [],
                        "v2ray_link_samples": []
                    }
                    self.logger.warning(f"{site_name} 未收集到节点")
                
                # 请求间隔
                if site_name != list(self.collectors.keys())[-1]:
                    time.sleep(REQUEST_DELAY)
                    
            except Exception as e:
                self.logger.error(f"收集 {site_name} 时出错: {str(e)}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 去重
        original_count = len(self.all_nodes)
        self.all_nodes = list(set(self.all_nodes))
        duplicate_count = original_count - len(self.all_nodes)
        
        original_v2ray_count = len(self.v2ray_subscription_links)
        self.v2ray_subscription_links = list(set(self.v2ray_subscription_links))
        v2ray_duplicate_count = original_v2ray_count - len(self.v2ray_subscription_links)
        
        self.logger.info("=" * 50)
        self.logger.info("节点收集完成")
        self.logger.info(f"总收集时间: {duration:.2f}秒")
        self.logger.info(f"原始节点数: {original_count}")
        self.logger.info(f"去重后节点数: {len(self.all_nodes)}")
        self.logger.info(f"重复节点数: {duplicate_count}")
        self.logger.info(f"原始V2Ray订阅链接数: {original_v2ray_count}")
        self.logger.info(f"去重后V2Ray订阅链接数: {len(self.v2ray_subscription_links)}")
        self.logger.info(f"重复V2Ray订阅链接数: {v2ray_duplicate_count}")
        self.logger.info("=" * 50)
        
        return self.all_nodes
    
    def test_nodes(self, nodes=None):
        """测试节点连通性"""
        if nodes is None:
            nodes = self.all_nodes
        
        if not nodes:
            self.logger.warning("没有节点需要测试")
            return []
        
        self.logger.info("开始测试节点连通性...")
        
        # 备份原始节点
        self.file_handler.backup_nodes(nodes)
        
        # 测试连通性
        valid_nodes = self.connectivity_tester.test_nodes(nodes)
        
        return valid_nodes
    
    def save_results(self, valid_nodes):
        """保存结果"""
        try:
            # 保存V2Ray订阅链接
            v2ray_success = self.file_handler.save_v2ray_links(self.v2ray_links_with_source)
            if not v2ray_success:
                self.logger.warning("V2Ray订阅链接保存失败")
            
            # 保存节点列表
            success = self.file_handler.save_nodes_to_file(valid_nodes)
            if not success:
                return False
            
            # 保存元数据
            self.file_handler.save_nodes_with_metadata(valid_nodes, self.source_info)
            
            # 清理旧备份
            self.file_handler.clean_old_backups()
            
            self.logger.info("结果保存完成")
            return True
            
        except Exception as e:
            self.logger.error(f"保存结果失败: {str(e)}")
            return False
    
    def update_github(self):
        """更新GitHub仓库"""
        try:
            import git
            
            repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            os.chdir(repo_path)
            
            repo = git.Repo(repo_path)
            
            with repo.config_writer() as cw:
                cw.set_value('user', 'email', GIT_EMAIL)
                cw.set_value('user', 'name', GIT_NAME)
            
            if repo.is_dirty(untracked_files=True):
                repo.index.add(['nodelist.txt', 'data/'])
                
                node_count = len(self.all_nodes)
                valid_count = len([n for n in self.all_nodes if n in self.connectivity_tester.test_nodes(self.all_nodes)])
                
                commit_message = f"更新节点列表 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ({valid_count}/{node_count} 有效)"
                
                repo.index.commit(commit_message)
                
                origin = repo.remote(name='origin')
                origin.push()
                
                self.logger.info(f"成功推送到GitHub: {commit_message}")
            else:
                self.logger.info("没有变化需要提交")
            
            return True
            
        except Exception as e:
            self.logger.error(f"更新GitHub失败: {str(e)}")
            return False
    
    def run(self, test_connectivity=True, target_dates=None):
        """运行完整的收集流程"""
        if target_dates is None:
            target_dates = [datetime.now()]
        
        try:
            # 1. 收集所有网站的节点
            all_nodes = self.collect_all_nodes()
            
            # 2. 保存文章链接（按日期分文件夹）
            date_suffix = datetime.now().strftime('%Y%m%d') if target_dates is None else target_dates[0].strftime('%Y%m%d') if len(target_dates) == 1 else None
            webpage_saved = self.file_handler.save_webpage_links(self.articles_with_source, date_suffix)
            if webpage_saved:
                self.logger.info("文章链接保存完成")
            else:
                self.logger.error("文章链接保存失败")
            
            # 3. 保存V2Ray订阅链接（按日期分文件夹）
            links_saved = self.file_handler.save_subscription_links(self.v2ray_links_with_source, date_suffix)
            if links_saved:
                self.logger.info("订阅链接信息保存完成")
            else:
                self.logger.error("V2Ray订阅链接保存失败")
            
            if not all_nodes:
                self.logger.warning("未收集到任何节点")
                return False
            
            # 4. 测试节点连通性
            if test_connectivity:
                self.logger.info("开始测试节点连通性...")
                valid_nodes = self.connectivity_tester.test_nodes(all_nodes)
                self.logger.info(f"连通性测试完成，有效节点: {len(valid_nodes)}")
            else:
                valid_nodes = all_nodes
                self.logger.info("跳过连通性测试")
            
            if not valid_nodes:
                self.logger.warning("没有有效的节点")
                return False
            
            # 5. 按AI服务可用性分类保存节点
            ai_available_nodes = []
            
            for node in valid_nodes:
                # 重新测试AI服务可用性
                host, port = self._extract_host_port_from_node(node)
                if host and port:
                    is_ai_available, _ = self.connectivity_tester.test_ai_services_connectivity(host, port)
                    if is_ai_available:
                        ai_available_nodes.append(node)
            
            # 6. 保存节点到文件
            # 保存到日期目录
            ai_saved = self.file_handler.save_nodes(ai_available_nodes, NODELIST_FILE, date_suffix)
            
            # 同步最新节点到根目录
            if date_suffix:
                # 保存AI可用节点到根目录
                root_ai_saved = self.file_handler.save_nodes(ai_available_nodes, NODELIST_FILE, None)
                
                if ai_saved and root_ai_saved:
                    self.logger.info(f"节点保存完成: AI可用节点 {len(ai_available_nodes)} 个")
                    self.logger.info(f"节点已同步到根目录: result/nodelist.txt")
                else:
                    self.logger.error("节点保存失败")
                    return False
            else:
                if ai_saved:
                    self.logger.info(f"节点保存完成: AI可用节点 {len(ai_available_nodes)} 个")
                else:
                    self.logger.error("节点保存失败")
                    return False
            
            self.logger.info("收集流程完成")
            return True
            
        except Exception as e:
            self.logger.error(f"运行收集流程时发生错误: {str(e)}")
            return False
    
    def _load_existing_articles(self, date_str=None):
        """加载现有的文章链接缓存"""
        articles = {}
        
        # 确定要检查的文件路径
        if date_str:
            # 转换日期格式: YYYY-MM-DD -> YYYYMMDD
            formatted_date = date_str.replace('-', '')
            webpage_file = f"result/{formatted_date}/webpage.txt"
        else:
            # 如果没有指定日期，先尝试今天的日期目录
            today = datetime.now().strftime('%Y-%m-%d')
            formatted_date = today.replace('-', '')
            webpage_file = f"result/{formatted_date}/webpage.txt"
            # 如果今天的目录不存在，再检查根目录
            if not os.path.exists(webpage_file):
                webpage_file = "result/webpage.txt"
        
        if not os.path.exists(webpage_file):
            self.logger.debug(f"文章缓存文件不存在: {webpage_file}")
            return articles
        
        try:
            with open(webpage_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            sections = content.split('------------------------------------------------------------')
            for section in sections:
                lines = section.strip().split('\n')
                website_name = None
                article_url = None
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('# ') and not line.startswith('===') and not line.startswith('各网站'):
                        website_name = line.replace('#', '').strip()
                    elif line.startswith('https://') and not line.startswith('#') and website_name:
                        article_url = line.strip()
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
                        if date_match:
                            date_str = date_match.group(1)
                            key = f"{website_name}_{date_str}"
                            articles[key] = article_url
                        
                        # 总是保存最新的文章链接（无论是否有日期）
                        articles[f"{website_name}_latest"] = article_url
                            
        except Exception as e:
            self.logger.error(f"加载文章缓存失败: {str(e)}")
        
        return articles
    
    def _load_existing_subscriptions(self, date_str=None):
        """加载现有的订阅链接缓存"""
        subscriptions = {}
        
        # 确定要检查的文件路径
        if date_str:
            # 转换日期格式: YYYY-MM-DD -> YYYYMMDD
            formatted_date = date_str.replace('-', '')
            subscription_file = f"result/{formatted_date}/subscription.txt"
        else:
            # 如果没有指定日期，先尝试今天的日期目录
            today = datetime.now().strftime('%Y-%m-%d')
            formatted_date = today.replace('-', '')
            subscription_file = f"result/{formatted_date}/subscription.txt"
            # 如果今天的目录不存在，再检查根目录
            if not os.path.exists(subscription_file):
                subscription_file = "result/subscription.txt"
        
        if not os.path.exists(subscription_file):
            self.logger.debug(f"订阅缓存文件不存在: {subscription_file}")
            return subscriptions
        
        try:
            with open(subscription_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            sections = content.split('------------------------------------------------------------')
            for section in sections:
                lines = section.strip().split('\n')
                website_name = None
                article_url = None
                links = []
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('# ') and not line.startswith('===') and '文章链接:' not in line and '链接数:' not in line:
                        website_name = line.replace('#', '').strip()
                    elif line.startswith('# 文章链接:'):
                        if '文章链接: None' not in line:
                            article_url = line.split('文章链接:')[1].strip()
                    elif line.startswith('https://') and not line.startswith('#'):
                        links.append(line)
                
                if website_name and article_url and links:
                    key = f"{website_name}_{article_url}"
                    subscriptions[key] = links
                    
        except Exception as e:
            self.logger.error(f"加载订阅链接缓存失败: {str(e)}")
        
        return subscriptions
    
    def _find_existing_article(self, existing_articles, website_name, date_str):
        """查找现有的文章链接"""
        # 优先查找指定日期的文章
        key = f"{website_name}_{date_str}"
        if key in existing_articles:
            return existing_articles[key]
        
        # 如果没有指定日期的文章，查找最新文章
        key_latest = f"{website_name}_latest"
        return existing_articles.get(key_latest)
    
    def _find_existing_subscriptions(self, existing_subscriptions, website_name, article_url):
        """查找现有的订阅链接"""
        key = f"{website_name}_{article_url}"
        return existing_subscriptions.get(key, [])
    
    def _get_nodes_from_subscription_links(self, subscription_links, collector):
        """从订阅链接获取实际节点"""
        nodes = []
        
        for link in subscription_links:
            try:
                self.logger.info(f"从订阅链接获取节点: {link}")
                sub_nodes = collector.get_nodes_from_subscription(link)
                nodes.extend(sub_nodes)
                self.logger.info(f"从 {link} 获取到 {len(sub_nodes)} 个节点")
            except Exception as e:
                self.logger.error(f"从订阅链接获取节点失败 {link}: {str(e)}")
        
        # 去重
        nodes = list(set(nodes))
        self.logger.info(f"从所有订阅链接获取到 {len(nodes)} 个去重后的节点")
        
        return nodes
    
    def _extract_host_port_from_node(self, node):
        """从节点信息中提取主机和端口"""
        try:
            if node.startswith('vmess://'):
                import base64
                import json
                data = node[8:]
                data += '=' * (-len(data) % 4)
                decoded = base64.b64decode(data).decode('utf-8')
                config = json.loads(decoded)
                return config.get('add'), config.get('port')
                
            elif node.startswith('vless://') or node.startswith('trojan://') or node.startswith('hysteria://'):
                import urllib.parse
                parsed = urllib.parse.urlparse(node)
                return parsed.hostname, parsed.port
                
            elif node.startswith('ss://'):
                import urllib.parse
                import base64
                
                if '#' in node:
                    node = node.split('#')[0]
                
                parsed = urllib.parse.urlparse(node)
                
                if parsed.hostname and parsed.port:
                    return parsed.hostname, parsed.port
                else:
                    data = node[5:]
                    data += '=' * (-len(data) % 4)
                    decoded = base64.b64decode(data).decode('utf-8')
                    
                    if ':' in decoded:
                        parts = decoded.split(':')
                        if len(parts) >= 2:
                            host = parts[0]
                            port_str = parts[1].split('@')[0] if '@' in parts[1] else parts[1]
                            return host, int(port_str)
            
            return None, None
            
        except Exception as e:
            self.logger.error(f"提取主机端口失败: {str(e)}")
            return None, None

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="免费V2Ray节点收集器")
    parser.add_argument("--no-test", action="store_true", help="跳过连通性测试")
    parser.add_argument("--update-github", action="store_true", help="更新GitHub仓库")
    parser.add_argument("--sites", nargs="+", help="指定要收集的网站", choices=list(WEBSITES.keys()))
    parser.add_argument("--date", help="指定日期，格式: YYYY-MM-DD (默认: 今天)")
    parser.add_argument("--dates", nargs="+", help="指定多个日期，格式: YYYY-MM-DD")
    parser.add_argument("--days", type=int, help="获取最近N天的数据")
    
    args = parser.parse_args()
    
    # 处理日期参数
    target_dates = []
    
    if args.dates:
        for date_str in args.dates:
            try:
                target_dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
            except ValueError:
                print(f"❌ 无效的日期格式: {date_str}，请使用 YYYY-MM-DD 格式")
                sys.exit(1)
    elif args.days:
        today = datetime.now()
        for i in range(args.days):
            target_dates.append(today - timedelta(days=i))
    elif args.date:
        try:
            target_dates.append(datetime.strptime(args.date, "%Y-%m-%d"))
        except ValueError:
            print(f"❌ 无效的日期格式: {args.date}，请使用 YYYY-MM-DD 格式")
            sys.exit(1)
    else:
        target_dates = None
    
    # 创建收集器
    collector = NodeCollector()
    
    # 如果指定了特定网站，只启用这些网站
    if args.sites:
        for site_name in collector.collectors:
            if site_name not in args.sites:
                collector.collectors[site_name].enabled = False
                collector.logger.info(f"禁用网站: {site_name}")
    else:
        collector.logger.info("运行所有网站")
    
    # 运行收集
    success = collector.run(
        test_connectivity=not args.no_test,
        target_dates=target_dates
    )
    
    # 更新GitHub
    if success and args.update_github:
        collector.update_github()
    
    if success:
        print("✓ 任务完成")
        sys.exit(0)
    else:
        print("✗ 任务失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
