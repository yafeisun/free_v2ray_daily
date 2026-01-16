#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为所有收集器添加今日文章查找和订阅链接提取功能
"""

import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 获取项目根目录（脚本在scripts/下，所以需要往上两级）
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def add_today_article_finder_to_collectors():
    """为所有收集器添加今日文章查找功能"""
    from pathlib import Path

    collectors_dir = PROJECT_ROOT / "src" / "collectors"
    
    # 需要修复的收集器文件
    collectors_to_fix = [
        'cfmem.py',
        'clashnodecc.py', 
        'clashnodev2ray.py',
        'datiya.py',
        'example_site.py',
        'freeclashnode.py',
        'freev2raynode.py',
        'github_collector.py',
        'mibei77.py',
        'multi_source_collector.py',
        'oneclash.py',
        'openproxylist_collector.py',
        'proxyqueen.py',
        'telegeam.py',
        'telegram_collector.py',
        'wanzhuanmi.py',
        'eighty_five_la.py'
    ]
    
    for filename in collectors_to_fix:
        file_path = collectors_dir / filename
        
        if not file_path.exists():
            print(f"文件不存在: {file_path}")
            continue
            
        content = file_path.read_text()
        
        # 检查是否已经有找今日文章的方法
        if 'get_today_article_url' in content:
            print(f"{filename} 已有今日文章查找功能")
            continue
        
        # 检查类的结构
        class_pattern = r'class\s+\w+.*?:'
        lines = content.split('\n')
        class_end_line = -1
        
        for i, line in enumerate(lines):
            if re.match(r'^\s*class\s+', line):
                class_end_line = i
            elif line.strip() and not line.startswith(' ') and not line.startswith('\t') and i > class_end_line:
                        class_end_line = i - 1
                break
        
        # 获取类的名称
        for line in lines[class_end_line+2:]:
            if re.match(r'^\s*class+(\w+)', line):
                class_name = re.findall(r'class\s+(\w+)', line)[0]
                break
        
        # 添加今日文章查找方法
        today_article_method = f'''
    def get_today_article_url(self) -> Optional[str]:  # type: ignore
        """获取今日文章链接的方法"""
        try:
            # 1. 构建日期模式
            today = datetime.now().strftime("%m%d")
            date_pattern = rf"{{today}}[\-_.]*"
            
            # 2. 使用已有的选择器查找今日文章
            for selector in self.selectors:
                try:
                    selector_result = selector.find_all()
                    if selector_result:
                        href = selector_result[0].get('href')
                        if href:
                            article_url = self._process_url(href)
                            self.logger.info(f"通过选择器找到今日文章: {{article_url}}")
                            return article_url
                except Exception as e:
                    self.logger.warning(f"选择器 {{selector}} 查找失败: {{e}}")
            
            # 3. 如果选择器没有找到，尝试直接匹配
            if not article_url:
                article_patterns = [
                    rf"{today}[\-_.]*\.html",
                    rf"{today}[\-_.]*\.htm",
                    rf"{today}.*{{class_name.lower()}}[\-_.]*\.(?:html|htm|shtml)",
                    # 其他通用模式
                    r'articles?[^\\s]*{{class_name.lower()}}[\-_.]*',
                    r'[^\\s]*node[\-_.]*',
                    r'订阅[^\\s]*',
                    r'free[\-_.]*[\-_.]*node',
                ]
                
                for pattern in article_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        # 找第一个匹配
                        article_url = matches[0]
                        self.logger.info(f"通过模式匹配找到今日文章: {{article_url}}")
                        return article_url
        except Exception as e:
            self.logger.error(f"获取今日文章链接失败: {{str(e)}}")
            return None
            
        except Exception as e:
            self.logger.error(f"查找今日文章时出错: {{str(e)}}")
            return None
'''
        today_article_method = f'''
    def get_today_article_url(self) -> Optional[str]:  # type: ignore
        """获取今日文章链接的方法"""
        try:
            # 1. 构建日期模式
            today = datetime.now().strftime("%m%d")
            date_pattern = rf"{today}[\-_.]*"
            
            # 2. 使用已有的选择器查找今日文章
            for selector in self.selectors:
                try:
                    selector_result = selector.find_all()
                    if selector_result:
                        href = selector_result[0].get('href')
                        if href:
                            article_url = self._process_url(href)
                            self.logger.info(f"通过选择器找到今日文章: {{article_url}}")
                            return article_url
                except Exception as e:
                    self.logger.warning(f"选择器 {{selector}} 查找失败: {{e}}")
            
            # 3. 如果选择器没有找到，尝试直接匹配
            if not article_url:
                article_patterns = [
                    rf"{today}[\-_.]*\.html",
                    rf"{today}[\-_.]*\.htm",
                    rf"{today}.*{self.name.lower()}[\-_.]*\.(?:html|htm|shtml)",
                    # 其他通用模式
                    r'articles?[^\\s]*{self.name}[^\\s]*[\-_.]*',
                    r'[^\\s]*node[\-_.]*',
                    r'订阅[^\\s]*',
                    r'free[\-_.]*[\-_.]*node',
                ]
                
                for pattern in article_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        # 找第一个匹配
                        article_url = matches[0]
                        self.logger.info(f"通过模式匹配找到今日文章: {{article_url}}")
                        return article_url
        except Exception as e:
            self.logger.error(f"获取今日文章链接失败: {{str(e)}}")
            return None
            
        except Exception as e:
            self.logger.error(f"查找今日文章时出错: {{str(e)}}")
            return None
'''
        
        # 在类的末尾添加方法
        lines.insert(class_end_line + 1, today_article_method)
        
        # 写回文件
        file_path.write_text('\n'.join(lines))
        print(f"✅ 为 {{class_name}} 添加了今日文章查找功能")
        
    except Exception as e:
        print(f"处理 {{filename}} 时出错: {{str(e)}}")

if __name__ == "__main__":
    add_today_article_finder_to_collectors()