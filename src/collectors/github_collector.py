#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub项目节点聚合器
从开源VPN项目自动获取节点列表
"""

import asyncio
import aiohttp
import json
import re
import base64
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

from .multi_source_collector import MultiSourceCollector
from src.utils.logger import get_logger


class GitHubCollector(MultiSourceCollector):
    """GitHub项目节点收集器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # GitHub配置
        self.repositories = config.get(
            "repositories",
            [
                # 高质量节点项目示例
                {
                    "owner": "v2ray",
                    "repo": "v2ray-core",
                    "files": ["release.txt", "nodes.txt", "subscription.txt"],
                },
                {
                    "owner": "Loyalsoldier",
                    "repo": "v2ray_node_list",
                    "files": ["v2ray/*.txt", "nodes/*.txt"],
                },
            ],
        )

        self.github_token = config.get("github_token")
        self.api_base = "https://api.github.com"
        self.raw_base = "https://raw.githubusercontent.com"

        # 请求配置
        self.timeout = config.get("timeout", 30)
        self.max_files = config.get("max_files", 50)

        # 节点模式
        self.node_patterns = [
            r"(vmess://[^\s\n\r]+)",
            r"(vless://[^\s\n\r]+)",
            r"(trojan://[^\s\n\r]+)",
            r"(hysteria2?://[^\s\n\r]+)",
            r"(ss://[^\s\n\r]+)",
            r"(ssr://[^\s\n\r]+)",
        ]

        self.session = None

    def validate_source(self) -> bool:
        """验证GitHub API是否可用"""
        return True  # GitHub API通常是可用的

    async def collect_nodes(self) -> List[Dict[str, Any]]:
        """从GitHub项目收集节点"""
        self.logger.info(f"开始从GitHub收集节点，仓库数: {len(self.repositories)}")

        all_nodes = []

        try:
            # 创建会话
            headers = {
                "User-Agent": "GitHub-Collector/1.0",
                "Accept": "application/vnd.github.v3+json",
            }

            if self.github_token:
                headers["Authorization"] = f"token {self.github_token}"

            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout), headers=headers
            )

            # 并发获取所有仓库的节点
            tasks = []
            for repo in self.repositories:
                task = asyncio.create_task(self.collect_from_repository(repo))
                tasks.append((repo["repo"], task))

            # 等待所有任务完成
            repo_results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(repo_results):
                repo_name = self.repositories[i]["repo"]
                if isinstance(result, Exception):
                    self.logger.error(f"仓库 {repo_name} 收集失败: {str(result)}")
                elif result:
                    all_nodes.extend(result)
                    self.logger.info(f"仓库 {repo_name}: {len(result)} 个节点")

            # 清理
            await self.session.close()

        except Exception as e:
            self.logger.error(f"GitHub收集异常: {str(e)}")

        return all_nodes

    async def collect_from_repository(
        self, repo: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """从单个仓库收集节点"""
        nodes = []

        try:
            owner = repo["owner"]
            repo_name = repo["repo"]
            target_files = repo.get("files", ["*.txt", "*.md"])

            self.logger.info(f"处理仓库: {owner}/{repo_name}")

            # 获取仓库文件列表
            files = await self.get_repository_files(owner, repo_name)

            # 过滤目标文件
            relevant_files = []
            for file_info in files:
                file_path = file_info["path"]

                # 检查文件名匹配
                if any(
                    self.match_file_pattern(file_path, pattern)
                    for pattern in target_files
                ):
                    relevant_files.append(file_info)

            # 限制文件数量
            if len(relevant_files) > self.max_files:
                relevant_files = relevant_files[: self.max_files]

            # 从文件中提取节点
            for file_info in relevant_files:
                file_nodes = await self.extract_nodes_from_file(
                    owner, repo_name, file_info
                )
                nodes.extend(file_nodes)

                if file_nodes:
                    self.logger.debug(
                        f"从文件 {file_info['path']} 提取到 {len(file_nodes)} 个节点"
                    )

        except Exception as e:
            self.logger.error(
                f"从仓库 {repo['owner']}/{repo['repo']} 收集失败: {str(e)}"
            )

        return nodes

    async def get_repository_files(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """获取仓库文件列表"""
        files = []

        try:
            # 获取目录内容
            url = f"{self.api_base}/repos/{owner}/{repo}/contents"

            async with self.session.get(url) as response:
                if response.status != 200:
                    self.logger.warning(f"获取仓库内容失败: {response.status}")
                    return files

                data = await response.json()

                if isinstance(data, list):
                    files.extend(data)
                elif isinstance(data, dict) and "message" not in data:
                    # 单个文件
                    files.append(data)

                # 递归获取子目录
                for item in files[:]:  # 使用切片避免修改正在迭代的列表
                    if item.get("type") == "dir":
                        sub_files = await self.get_directory_contents(
                            owner, repo, item["path"]
                        )
                        files.extend(sub_files)
                        files.remove(item)  # 移除目录项

        except Exception as e:
            self.logger.error(f"获取仓库文件异常: {str(e)}")

        return files

    async def get_directory_contents(
        self, owner: str, repo: str, path: str
    ) -> List[Dict[str, Any]]:
        """获取目录内容"""
        files = []

        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/contents/{path}"

            async with self.session.get(url) as response:
                if response.status != 200:
                    return files

                data = await response.json()

                if isinstance(data, list):
                    files.extend(data)
                elif isinstance(data, dict):
                    files.append(data)

        except Exception as e:
            self.logger.error(f"获取目录内容异常: {str(e)}")

        return files

    async def extract_nodes_from_file(
        self, owner: str, repo: str, file_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """从文件中提取节点"""
        nodes = []

        try:
            file_path = file_info["path"]
            download_url = f"{self.raw_base}/{owner}/{repo}/main/{file_path}"

            # 尝试不同的分支
            branches = ["main", "master", "develop"]
            for branch in branches:
                url = f"{self.raw_base}/{owner}/{repo}/{branch}/{file_path}"

                async with self.session.get(url) as response:
                    if response.status == 200:
                        download_url = url
                        content = await response.text()
                        break
                    elif branch == branches[-1]:
                        content = ""
                        break
                continue

            if not content:
                return nodes

            # 提取节点
            extracted_nodes = self.extract_nodes_from_content(content)

            # 转换为标准格式
            for node_text in extracted_nodes:
                node = {
                    "url": node_text,
                    "source": "github",
                    "source_repo": f"{owner}/{repo}",
                    "source_file": file_path,
                    "source_url": download_url,
                    "created_at": file_info.get(
                        "created_at", datetime.now().isoformat()
                    ),
                    "updated_at": file_info.get(
                        "updated_at", datetime.now().isoformat()
                    ),
                    "source_type": "github",
                    "reliability": 0.9,  # GitHub项目通常较可靠
                    "freshness": self.calculate_file_freshness(file_info),
                    "metadata": {
                        "repo": f"{owner}/{repo}",
                        "file": file_path,
                        "size": file_info.get("size", 0),
                        "sha": file_info.get("sha", ""),
                    },
                }
                nodes.append(node)

        except Exception as e:
            self.logger.error(f"从文件 {file_info['path']} 提取节点失败: {str(e)}")

        return nodes

    def extract_nodes_from_content(self, content: str) -> List[str]:
        """从内容中提取节点"""
        nodes = []

        # 直接匹配节点协议
        for pattern in self.node_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            nodes.extend(matches)

        # 处理Base64编码内容
        base64_matches = re.findall(r"([A-Za-z0-9+/]{100,}={0,2})", content)
        for base64_text in base64_matches:
            if self.is_likely_base64_nodes(base64_text):
                try:
                    decoded = base64.b64decode(
                        base64_text + "=" * (-len(base64_text) % 4)
                    ).decode("utf-8", errors="ignore")
                    decoded_nodes = self.extract_nodes_from_content(decoded)
                    nodes.extend(decoded_nodes)
                except:
                    pass

        # 去重
        return list(set(nodes))

    def is_likely_base64_nodes(self, text: str) -> bool:
        """判断Base64文本是否可能包含节点"""
        try:
            decoded = base64.b64decode(text + "=" * (-len(text) % 4)).decode(
                "utf-8", errors="ignore"
            )

            # 检查是否包含节点协议
            protocols = ["vmess://", "vless://", "trojan://", "ss://", "ssr://"]
            return any(proto in decoded.lower() for proto in protocols)
        except:
            return False

    def calculate_file_freshness(self, file_info: Dict[str, Any]) -> float:
        """计算文件新鲜度评分"""
        updated_at = file_info.get("updated_at")

        if not updated_at:
            return 0.7

        try:
            update_time = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            age_hours = (datetime.now() - update_time).total_seconds() / 3600

            if age_hours < 24:
                return 1.0
            elif age_hours < 168:  # 1周
                return 0.8
            elif age_hours < 720:  # 1月
                return 0.6
            elif age_hours < 2160:  # 3月
                return 0.4
            else:
                return 0.2
        except:
            return 0.5

    def match_file_pattern(self, file_path: str, pattern: str) -> bool:
        """匹配文件模式"""
        import fnmatch

        file_name = file_path.lower()
        pattern_lower = pattern.lower()

        return fnmatch.fnmatch(file_name, pattern_lower)


# 注册GitHub收集器的工厂函数
def create_github_collector(config: Dict[str, Any]) -> GitHubCollector:
    """创建GitHub收集器实例"""
    return GitHubCollector(config)


# 在模块级别添加collect方法供主程序调用
def add_collect_method(collector):
    """为GitHub收集器添加collect方法"""

    def collect_method(self) -> List[str]:  # type: ignore
        """GitHub专用收集方法，支持Base64订阅链接检测"""
        return self.collect_with_base64_detection()

    # 动态添加方法
    collector.collect = collect_method.__get__(collector)


    def collect(self):  # type: ignore
        """简化收集方法"""
        try:
            # 尝试调用现有的节点获取方法
            if hasattr(self, 'get_v2ray_subscription_links') and hasattr(self, 'last_article_url'):
                links = self.get_v2ray_subscription_links(getattr(self, 'last_article_url', ''))
                nodes = []
                for link in links:
                    try:
                        nodes_from_link = self.get_nodes_from_subscription(link)
                        nodes.extend(nodes_from_link)
                    except:
                        pass
                
                return nodes
            
            # 如果有直接节点提取方法
            if hasattr(self, 'extract_direct_nodes'):
                page_content = getattr(self, 'fetch_page', lambda x: "")(self.base_url) if hasattr(self, 'base_url') else ""
                direct_nodes = self.extract_direct_nodes(page_content)
                return direct_nodes
                
        except Exception:
            return []
