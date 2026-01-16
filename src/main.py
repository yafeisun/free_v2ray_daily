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

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 使用绝对导入
import sys
import os
import time
import re
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入工具模块
try:
    from utils.logger import get_logger
    from utils.file_handler import FileHandler
    from config.settings import *
    from config.websites import WEBSITES
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保在正确的目录运行")
    sys.exit(1)

# 导入各个网站的爬虫
from src.collectors.freeclashnode import FreeClashNodeCollector
from src.collectors.mibei77 import Mibei77Collector
from src.collectors.clashnodev2ray import ClashNodeV2RayCollector
from src.collectors.proxyqueen import ProxyQueenCollector
from src.collectors.wanzhuanmi import WanzhuanmiCollector
from src.collectors.cfmem import CfmemCollector
from src.collectors.clashnodecc import ClashNodeCCCollector
from src.collectors.datiya import DatiyaCollector
from src.collectors.telegeam import TelegeamCollector
from src.collectors.clashgithub import ClashGithubCollector
from src.collectors.freev2raynode import FreeV2rayNodeCollector
from src.collectors.eighty_five_la import EightyFiveLaCollector
from src.collectors.oneclash import OneClashCollector


class NodeCollector:
    """节点收集器主类"""

    def __init__(self):
        self.logger = get_logger("main")
        self.file_handler = FileHandler()

        # 初始化爬虫
        self.collectors = {
            "freeclashnode": FreeClashNodeCollector(WEBSITES["freeclashnode"]),
            "mibei77": Mibei77Collector(WEBSITES["mibei77"]),
            "clashnodev2ray": ClashNodeV2RayCollector(WEBSITES["clashnodev2ray"]),
            "proxyqueen": ProxyQueenCollector(WEBSITES["proxyqueen"]),
            "wanzhuanmi": WanzhuanmiCollector(WEBSITES["wanzhuanmi"]),
            "cfmem": CfmemCollector(WEBSITES["cfmem"]),
            "clashnodecc": ClashNodeCCCollector(WEBSITES["clashnodecc"]),
            "datiya": DatiyaCollector(WEBSITES["datiya"]),
            "telegeam": TelegeamCollector(WEBSITES["telegeam"]),
            "clashgithub": ClashGithubCollector(WEBSITES["clashgithub"]),
            "freev2raynode": FreeV2rayNodeCollector(WEBSITES["freev2raynode"]),
            "85la": EightyFiveLaCollector(WEBSITES["85la"]),
            "oneclash": OneClashCollector(WEBSITES["oneclash"]),
        }

        self.all_nodes = []
        self.v2ray_subscription_links = []
        self.v2ray_links_with_source = []
        self.articles_with_source = []
        self.source_info = {}

    def collect_all_nodes(self):
        """收集所有网站的文章和订阅链接 - 两阶段执行策略"""
        self.logger.info("=" * 50)
        self.logger.info("第一阶段：收集所有网站的文章链接和订阅链接")
        self.logger.info("=" * 50)

        start_time = time.time()
        today = datetime.now().strftime("%Y-%m-%d")
        date_str = datetime.now().strftime("%Y%m%d")

        # 创建日期目录
        date_dir = f"result/{date_str}"
        os.makedirs(date_dir, exist_ok=True)

        # 第一阶段：收集所有网站的文章链接和订阅链接
        for site_name, collector in self.collectors.items():
            try:
                self.logger.info(f"正在收集 {site_name} 的文章和订阅链接...")

                # 获取最新文章URL
                article_url = collector.get_latest_article_url()

                # 获取V2Ray订阅链接
                v2ray_links = []
                if article_url:
                    v2ray_links = collector.get_v2ray_subscription_links(article_url)

                # 合并保存文章链接和订阅链接到一个文件
                info_file = os.path.join(date_dir, f"{site_name}_info.txt")
                with open(info_file, "w", encoding="utf-8") as f:
                    f.write(f"# {site_name} 文章和订阅链接\n")
                    f.write(
                        f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    )
                    f.write("-" * 60 + "\n\n")

                    # 文章链接部分
                    f.write("## 文章链接\n")
                    if article_url:
                        f.write(f"{article_url}\n")
                        self.articles_with_source.append(
                            {
                                "website_name": site_name,
                                "article_url": article_url,
                                "date": today,
                            }
                        )
                    else:
                        f.write("# 今日未更新文章\n")
                    f.write("\n")

                    # 订阅链接部分
                    f.write("## 订阅链接\n")
                    if v2ray_links:
                        for link in v2ray_links:
                            f.write(f"{link}\n")
                    else:
                        f.write("# 无V2Ray订阅链接\n")

                self.logger.info(
                    f"{site_name}: 文章和订阅链接已保存到 {info_file}，共 {len(v2ray_links)} 个链接"
                )

                # 记录V2Ray订阅链接信息（用于汇总）
                if not v2ray_links:
                    self.v2ray_links_with_source.append(
                        {
                            "url": "# 无V2Ray订阅链接",
                            "source": site_name,
                            "source_url": article_url if article_url else "N/A",
                        }
                    )
                else:
                    for link in v2ray_links:
                        self.v2ray_links_with_source.append(
                            {
                                "url": link,
                                "source": site_name,
                                "source_url": article_url,
                            }
                        )

                # 收集所有订阅链接（不去重，保留网站信息）
                self.v2ray_subscription_links.extend(v2ray_links)

                # 更新源信息
                self.source_info[site_name] = {
                    "count": 0,  # 稍后更新
                    "enabled": collector.enabled,
                    "subscription_links": len(v2ray_links),
                    "v2ray_links": len(v2ray_links),
                    "links": v2ray_links[:5],
                    "v2ray_link_samples": v2ray_links[:5],
                }

                # 请求间隔
                if site_name != list(self.collectors.keys())[-1]:
                    time.sleep(REQUEST_DELAY)

            except Exception as e:
                self.logger.error(f"收集 {site_name} 时出错: {str(e)}")
                # 即使出错也保存错误信息
                article_file = os.path.join(date_dir, f"{site_name}_article.txt")
                with open(article_file, "w", encoding="utf-8") as f:
                    f.write(f"# {site_name} 文章链接\n")
                    f.write(
                        f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    )
                    f.write(f"# 状态: 收集失败\n")
                    f.write(f"# 错误信息: {str(e)}\n")
                    f.write("-" * 60 + "\n\n")

        # 第一阶段完成
        first_phase_time = time.time() - start_time
        self.logger.info(f"第一阶段完成，耗时: {first_phase_time:.2f}秒")
        self.logger.info(f"收集到 {len(self.v2ray_subscription_links)} 个订阅链接")

        # 第二阶段：通过订阅链接获取节点
        self.logger.info("=" * 50)
        self.logger.info("第二阶段：通过订阅链接获取节点")
        self.logger.info("=" * 50)

        second_start_time = time.time()

        # 去重订阅链接（保留网站信息）
        unique_links = []
        seen_links = set()
        links_with_source = []

        for link_info in self.v2ray_links_with_source:
            if (
                link_info["url"] not in seen_links
                and link_info["url"] != "# 无V2Ray订阅链接"
            ):
                seen_links.add(link_info["url"])
                unique_links.append(link_info["url"])
                links_with_source.append(link_info)

        self.logger.info(f"去重后有 {len(unique_links)} 个唯一订阅链接")

        # 通过订阅链接获取节点
        for i, link_info in enumerate(links_with_source):
            try:
                self.logger.info(
                    f"处理订阅链接 ({i + 1}/{len(links_with_source)}): {link_info['url'][:50]}..."
                )

                # 获取收集器实例
                collector = self.collectors[link_info["source"]]

                # 从订阅链接获取节点
                nodes = collector.get_nodes_from_subscription(link_info["url"])

                if nodes:
                    self.all_nodes.extend(nodes)
                    self.logger.info(
                        f"从 {link_info['source']} 获取到 {len(nodes)} 个节点"
                    )

                    # 更新源信息中的节点数
                    if link_info["source"] in self.source_info:
                        self.source_info[link_info["source"]]["count"] += len(nodes)
                else:
                    self.logger.warning(f"从 {link_info['url']} 未获取到节点")

                # 请求间隔
                if i < len(links_with_source) - 1:
                    time.sleep(REQUEST_DELAY)

            except Exception as e:
                self.logger.error(f"处理订阅链接失败 {link_info['url']}: {str(e)}")

        # 去重（使用server+port组合作为去重标准，去除真正重复的节点）
        original_count = len(self.all_nodes)
        seen = set()
        unique_nodes = []
        for node in self.all_nodes:
            # 提取server+port作为唯一标识
            server_port = None
            try:
                if "://" in node:
                    protocol = node.split("://", 1)[0]
                    rest = node.split("://", 1)[1]

                    # 移除名称部分（#后面的内容）
                    if "#" in rest:
                        rest = rest.rsplit("#", 1)[0]

                    # 提取server+port
                    if "@" in rest:
                        rest = rest.split("@", 1)[1]

                    if ":" in rest:
                        parts = rest.split(":")
                        if len(parts) >= 2:
                            server = parts[0]
                            port = (
                                parts[1]
                                .split("?")[0]
                                .split("/")[0]
                                .split("\\")[0]
                                .rstrip("/")
                            )
                            server_port = f"{server}:{port}"
            except:
                pass

            # 如果无法提取server+port，使用完整节点作为标识
            if not server_port:
                server_port = node

            if server_port not in seen:
                seen.add(server_port)
                unique_nodes.append(node)

        self.all_nodes = unique_nodes
        duplicate_count = original_count - len(self.all_nodes)

        # 为收集阶段的节点生成简单命名（国旗_区域_数字）
        named_nodes = []
        region_counters = {}

        for i, node in enumerate(self.all_nodes):
            # 提取地区信息用于生成简单名称
            region = self._extract_region_for_collection(node)

            # 初始化地区计数器
            if region not in region_counters:
                region_counters[region] = 0

            # 地区编号递增
            region_counters[region] += 1
            region_number = region_counters[region]

            # 生成简单名称
            simple_name = self._generate_simple_node_name(region, region_number)

            # 添加名称到节点（如果节点有名称部分）
            if "#" in node:
                node_with_name = node.rsplit("#", 1)[0] + f"#{simple_name}"
            else:
                node_with_name = f"{node}#{simple_name}"

            named_nodes.append(node_with_name)

        # 保存去重并重命名后的所有节点到 nodetotal.txt
        nodetotal_file = os.path.join(date_dir, "nodetotal.txt")
        with open(nodetotal_file, "w", encoding="utf-8") as f:
            for node in named_nodes:
                f.write(f"{node}\n")

        self.logger.info(
            f"所有节点已保存到 {nodetotal_file}，原始: {original_count} 个，去重后: {len(self.all_nodes)} 个，重复: {duplicate_count} 个"
        )

        end_time = time.time()
        total_duration = end_time - start_time
        second_phase_time = end_time - second_start_time

        self.logger.info("=" * 50)
        self.logger.info("节点收集完成")
        self.logger.info(f"总收集时间: {total_duration:.2f}秒")
        self.logger.info(f"第一阶段时间: {first_phase_time:.2f}秒")
        self.logger.info(f"第二阶段时间: {second_phase_time:.2f}秒")
        self.logger.info(f"原始节点数: {original_count}")
        self.logger.info(f"去重后节点数: {len(self.all_nodes)}")
        self.logger.info(f"重复节点数: {duplicate_count}")
        self.logger.info(f"唯一订阅链接数: {len(unique_links)}")
        self.logger.info("=" * 50)

        return self.all_nodes

    def update_github(self):
        """更新GitHub仓库"""
        try:
            import git

            repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            os.chdir(repo_path)

            repo = git.Repo(repo_path)

            with repo.config_writer() as cw:
                cw.set_value("user", "email", GIT_EMAIL)
                cw.set_value("user", "name", GIT_NAME)

            if repo.is_dirty(untracked_files=True):
                repo.index.add(["result/nodelist.txt", "result/nodetotal.txt"])

                # 生成详细的提交信息
                date_str = datetime.now().strftime("%Y-%m-%d")
                date_dir = f"result/{date_str}"
                update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                commit_lines = [f"更新节点列表 - {update_time}"]
                commit_lines.append("=" * 60)
                commit_lines.append(f"更新时间: {update_time}")

                # 汇总网站收集情况
                commit_lines.append("\n网站收集情况:")
                success_sites = []
                failed_sites = []

                for site_name in self.collectors.keys():
                    info_file = os.path.join(date_dir, f"{site_name}_info.txt")
                    if os.path.exists(info_file):
                        success_sites.append(site_name)
                        # 读取 info 文件内容
                        with open(info_file, "r", encoding="utf-8") as f:
                            content = f.read()
                            # 提取文章链接
                            article_url = None
                            for line in content.split("\n"):
                                if line.startswith("## 文章链接\n"):
                                    next_line = (
                                        content.split("## 文章链接\n")[1].split("\n")[1]
                                        if "## 文章链接\n" in content
                                        else ""
                                    )
                                    if next_line and not next_line.startswith("#"):
                                        article_url = next_line.strip()
                                    break

                            # 提取订阅链接数量
                            subscription_count = 0
                            for line in content.split("\n"):
                                if line.startswith("## 订阅链接\n"):
                                    subscription_section = (
                                        content.split("## 订阅链接\n")[1].split("\n")[
                                            1:
                                        ]
                                        if "## 订阅链接\n" in content
                                        else []
                                    )
                                    subscription_count = len(
                                        [
                                            l
                                            for l in subscription_section
                                            if l.strip() and not l.startswith("#")
                                        ]
                                    )
                                    break

                            commit_lines.append(f"\n✓ {site_name}:")
                            if article_url:
                                commit_lines.append(f"  文章: {article_url}")
                            if subscription_count > 0:
                                commit_lines.append(
                                    f"  订阅链接: {subscription_count} 个"
                                )
                            else:
                                commit_lines.append(f"  订阅链接: 无")
                    else:
                        failed_sites.append(site_name)
                        commit_lines.append(f"\n✗ {site_name}: 未获取到数据")

                # 汇总统计
                commit_lines.append("\n" + "=" * 60)
                commit_lines.append(f"成功: {len(success_sites)} 个网站")
                commit_lines.append(f"失败: {len(failed_sites)} 个网站")
                if failed_sites:
                    commit_lines.append(f"失败网站: {', '.join(failed_sites)}")

                # 节点统计
                node_count = len(self.all_nodes)
                commit_lines.append(f"\n总节点数: {node_count}")

                # 组合提交信息
                commit_message = "\n".join(commit_lines)

                repo.index.commit(commit_message)

                origin = repo.remote(name="origin")
                origin.push()

                self.logger.info(f"成功推送到GitHub")
                self.logger.info(f"提交信息:\n{commit_message}")
            else:
                self.logger.info("没有变化需要提交")

            return True

        except Exception as e:
            self.logger.error(f"更新GitHub失败: {str(e)}")
            return False

    def run(self, target_dates=None):
        """运行完整的收集流程"""
        if target_dates is None:
            target_dates = [datetime.now()]

        try:
            # 1. 收集所有网站的节点（新策略：依次执行，按网站保存文件）
            all_nodes = self.collect_all_nodes()

            if not all_nodes:
                self.logger.warning("未收集到任何节点")
                return False

            # 2. 同步所有节点到根目录
            date_suffix = datetime.now().strftime("%Y%m%d")
            sync_success = self.file_handler.sync_latest_to_root(date_suffix)

            if sync_success:
                self.logger.info(
                    f"所有节点已同步到根目录: result/nodetotal.txt ({len(all_nodes)} 个)"
                )
            else:
                self.logger.warning("同步节点到根目录失败")

            # 3. 清理临时文件
            clean_success = self.file_handler.clean_root_temp_files()

            if clean_success:
                self.logger.info(f"已清理临时文件")

            self.logger.info("收集流程完成")
            return True

        except Exception as e:
            self.logger.error(f"运行收集流程时发生错误: {str(e)}")
            return False

    def _load_existing_articles(self, date_str=None):
        """加载现有的文章链接缓存"""
        # 使用file_handler的新方法
        date_suffix = None
        if date_str:
            date_suffix = date_str.replace("-", "")

        return self.file_handler.load_existing_articles(date_suffix)

    def _load_existing_subscriptions(self, date_str=None):
        """加载现有的订阅链接缓存"""
        # 使用file_handler的新方法
        date_suffix = None
        if date_str:
            date_suffix = date_str.replace("-", "")

        return self.file_handler.load_existing_subscriptions(date_suffix)

    def _find_existing_article(self, existing_articles, website_name, date_str):
        """查找现有的文章链接"""
        # 直接使用网站名称作为键名（与缓存解析逻辑一致）
        if website_name in existing_articles:
            return existing_articles[website_name]

        return None

    def _find_existing_subscriptions(
        self, existing_subscriptions, website_name, article_url
    ):
        """查找现有的订阅链接"""
        key = f"{website_name}_{article_url}"
        return existing_subscriptions.get(key, [])

    def _extract_region_for_collection(self, node: str) -> str:
        """从节点中提取地区信息（收集阶段使用）"""
        try:
            # 简单的基于端口的地区判断
            if ":" in node:
                # 移除协议部分
                rest = node.split("://", 1)[1] if "://" in node else node

                # 移除名称部分
                rest = rest.rsplit("#", 1)[0] if "#" in rest else rest

                # 提取端口
                if "@" in rest:
                    rest = rest.split("@", 1)[1]

                if ":" in rest:
                    port_str = (
                        rest.split(":")[1].split("?")[0].split("/")[0].rstrip("/")
                    )
                    try:
                        port = int(port_str)

                        # 基于端口范围判断地区
                        if 10000 <= port <= 19999:
                            return "US"  # 美国常用端口范围
                        elif 20000 <= port <= 29999:
                            return "HK"  # 香港常用端口范围
                        elif 30000 <= port <= 39999:
                            return "JP"  # 日本常用端口范围
                        elif 40000 <= port <= 49999:
                            return "SG"  # 新加坡常用端口范围
                        elif port >= 50000:
                            return "EU"  # 欧洲常用端口范围
                    except ValueError:
                        pass

            # 默认返回US
            return "US"
        except:
            return "US"

    def _generate_simple_node_name(self, region: str, number: int) -> str:
        """生成简单节点名称（收集阶段使用）"""
        # 国旗映射
        flags = {
            "HK": "🇭🇰",
            "US": "🇺🇸",
            "JP": "🇯🇵",
            "SG": "🇸🇬",
            "TW": "🇨🇳",
            "KR": "🇰🇷",
            "DE": "🇩🇪",
            "GB": "🇬🇧",
            "FR": "🇫🇷",
            "CA": "🇨🇦",
            "NL": "🇳🇱",
            "RU": "🇷🇺",
            "IN": "🇮🇳",
            "BR": "🇧🇷",
            "AU": "🇦🇺",
            "EU": "🇪🇺",
        }

        flag = flags.get(region, "🇺🇸")

        # 简单格式：国旗_区域_数字
        return f"{flag}{region}_{number}"

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
            if node.startswith("vmess://"):
                import base64
                import json

                data = node[8:]
                data += "=" * (-len(data) % 4)
                decoded = base64.b64decode(data).decode("utf-8")
                config = json.loads(decoded)
                return config.get("add"), config.get("port")

            elif (
                node.startswith("vless://")
                or node.startswith("trojan://")
                or node.startswith("hysteria://")
            ):
                import urllib.parse

                parsed = urllib.parse.urlparse(node)
                return parsed.hostname, parsed.port

            elif node.startswith("ss://"):
                import urllib.parse
                import base64

                if "#" in node:
                    node = node.split("#")[0]

                parsed = urllib.parse.urlparse(node)

                if parsed.hostname and parsed.port:
                    return parsed.hostname, parsed.port
                else:
                    data = node[5:]
                    data += "=" * (-len(data) % 4)
                    decoded = base64.b64decode(data).decode("utf-8")

                    if ":" in decoded:
                        parts = decoded.split(":")
                        if len(parts) >= 2:
                            host = parts[0]
                            port_str = (
                                parts[1].split("@")[0] if "@" in parts[1] else parts[1]
                            )
                            return host, int(port_str)

            return None, None

        except Exception as e:
            self.logger.error(f"提取主机端口失败: {str(e)}")
            return None, None


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="免费V2Ray节点收集器")
    parser.add_argument("--update-github", action="store_true", help="更新GitHub仓库")
    parser.add_argument(
        "--sites", nargs="+", help="指定要收集的网站", choices=list(WEBSITES.keys())
    )
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
    success = collector.run(target_dates=target_dates)

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
