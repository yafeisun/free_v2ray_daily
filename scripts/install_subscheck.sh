#!/bin/bash
# -*- coding: utf-8 -*-
"""
Subs-Check 安装脚本
"""

set -e

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SUBSCHECK_DIR="${PROJECT_ROOT}/subscheck"
BINARY_DIR="${SUBSCHECK_DIR}/bin"
CONFIG_DIR="${SUBSCHECK_DIR}/config"

echo "======================================"
echo "Subs-Check 安装脚本"
echo "======================================"
echo "项目根目录: ${PROJECT_ROOT}"
echo "Subs-Check目录: ${SUBSCHECK_DIR}"
echo "二进制目录: ${BINARY_DIR}"
echo "配置目录: ${CONFIG_DIR}"
echo "======================================"

# 创建目录
echo "创建目录..."
mkdir -p "${BINARY_DIR}"
mkdir -p "${CONFIG_DIR}"

# 确定下载URL
OS_TYPE=$(uname -s)
ARCH_TYPE=$(uname -m)

echo "检测到操作系统: ${OS_TYPE}"
echo "检测到架构: ${ARCH_TYPE}"

DOWNLOAD_URL=""

if [ "${OS_TYPE}" = "Linux" ]; then
    if [ "${ARCH_TYPE}" = "x86_64" ]; then
        DOWNLOAD_URL="https://github.com/beck-8/subs-check/releases/latest/download/subs-check_Linux_x86_64.tar.gz"
    elif [ "${ARCH_TYPE}" = "aarch64" ] || [ "${ARCH_TYPE}" = "arm64" ]; then
        DOWNLOAD_URL="https://github.com/beck-8/subs-check/releases/latest/download/subs-check_Linux_arm64.tar.gz"
    else
        echo "不支持的架构: ${ARCH_TYPE}"
        exit 1
    fi
elif [ "${OS_TYPE}" = "Darwin" ]; then
    if [ "${ARCH_TYPE}" = "x86_64" ]; then
        DOWNLOAD_URL="https://github.com/beck-8/subs-check/releases/latest/download/subs-check_Darwin_x86_64.tar.gz"
    elif [ "${ARCH_TYPE}" = "arm64" ]; then
        DOWNLOAD_URL="https://github.com/beck-8/subs-check/releases/latest/download/subs-check_Darwin_arm64.tar.gz"
    else
        echo "不支持的架构: ${ARCH_TYPE}"
        exit 1
    fi
else
    echo "不支持的操作系统: ${OS_TYPE}"
    exit 1
fi

echo "下载URL: ${DOWNLOAD_URL}"

# 下载文件
echo "下载subs-check..."
cd "${BINARY_DIR}"
curl -L -o subs-check.tar.gz "${DOWNLOAD_URL}"

# 解压文件
echo "解压文件..."
if [ "${OS_TYPE}" = "Linux" ] || [ "${OS_TYPE}" = "Darwin" ]; then
    tar -xzf subs-check.tar.gz
fi

# 设置执行权限
chmod +x subs-check

# 清理临时文件
rm -f subs-check.tar.gz

echo "======================================"
echo "安装完成！"
echo "二进制文件: ${BINARY_DIR}/subs-check"
echo "配置文件: ${CONFIG_DIR}/config.yaml"
echo "======================================"
echo "运行测试: ${BINARY_DIR}/subs-check -f ${CONFIG_DIR}/config.yaml"
echo "======================================"
