#!/usr/bin/env python3
"""下载 subs-check 工具"""

import os
import sys
import requests
import tarfile

def download_file(url, filename, chunk_size=8192):
    """分块下载文件"""
    response = requests.get(url, stream=True, timeout=600)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                
                # 显示进度
                if total_size > 0:
                    progress = downloaded / total_size * 100
                    print(f"\r下载进度: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='')
    
    print()  # 换行

def main():
    """主函数"""
    # 创建目录
    os.makedirs('subscheck/bin', exist_ok=True)
    
    # 下载
    url = 'https://github.com/beck-8/subs-check/releases/latest/download/subs-check_Linux_x86_64.tar.gz'
    tar_file = 'subscheck/bin/subs-check.tar.gz'
    
    print(f"下载 {url}...")
    download_file(url, tar_file)
    
    # 解压
    print("解压...")
    with tarfile.open(tar_file, 'r:gz') as tar:
        tar.extractall('subscheck/bin')
    
    # 设置执行权限
    os.chmod('subscheck/bin/subs-check', 0o755)
    
    # 清理
    os.remove(tar_file)
    
    print("安装完成！")
    os.system('ls -lh subscheck/bin/subs-check')

if __name__ == '__main__':
    main()