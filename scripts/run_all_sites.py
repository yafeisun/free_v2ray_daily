#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量运行所有网站脚本
"""

import sys
import os
import subprocess
from datetime import datetime

# 网站列表
WEBSITES = [
    'freeclashnode',
    'mibei77', 
    'clashnodev2ray',
    'proxyqueen',
    'wanzhuanmi',
    'cfmem'
]

def main():
    """主函数"""
    print("=" * 60)
    print(f"开始批量运行所有网站脚本 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    success_count = 0
    failed_sites = []
    
    for site in WEBSITES:
        script_path = os.path.join(scripts_dir, f"{site}.py")
        
        if not os.path.exists(script_path):
            print(f"❌ {site}: 脚本文件不存在 {script_path}")
            failed_sites.append(site)
            continue
        
        print(f"\n🚀 运行 {site} 脚本...")
        print("-" * 40)
        
        try:
            # 运行脚本
            result = subprocess.run([sys.executable, script_path], 
                                  capture_output=True, 
                                  text=True, 
                                  encoding='utf-8')
            
            if result.returncode == 0:
                print(f"✅ {site}: 运行成功")
                success_count += 1
                # 显示输出
                if result.stdout.strip():
                    print("输出:", result.stdout.strip())
            else:
                print(f"❌ {site}: 运行失败")
                failed_sites.append(site)
                # 显示错误信息
                if result.stderr.strip():
                    print("错误:", result.stderr.strip())
                if result.stdout.strip():
                    print("输出:", result.stdout.strip())
                    
        except Exception as e:
            print(f"❌ {site}: 运行异常 - {str(e)}")
            failed_sites.append(site)
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("批量运行完成")
    print("=" * 60)
    print(f"✅ 成功: {success_count}/{len(WEBSITES)} 个网站")
    
    if failed_sites:
        print(f"❌ 失败: {len(failed_sites)} 个网站")
        print("失败网站:", ", ".join(failed_sites))
    
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return len(failed_sites) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)