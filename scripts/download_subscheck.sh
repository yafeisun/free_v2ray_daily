#!/bin/bash
# 下载 subs-check 工具

echo "创建目录..."
mkdir -p subscheck/bin

echo "下载 subs-check..."
cd subscheck/bin

# 使用 curl 下载
curl -L -o subs-check.tar.gz \
  https://github.com/beck-8/subs-check/releases/latest/download/subs-check_Linux_x86_64.tar.gz

echo "解压..."
tar -xzf subs-check.tar.gz

echo "设置执行权限..."
chmod +x subs-check

echo "清理临时文件..."
rm -f subs-check.tar.gz

echo "安装完成！"
ls -lh subs-check