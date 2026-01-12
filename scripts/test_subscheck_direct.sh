#!/bin/bash

# 测试subs-check直接运行

echo "=== 测试subs-check直接运行 ==="

# 1. 启动HTTP服务器
echo "1. 启动HTTP服务器..."
python3 -m http.server 8888 --directory . &
HTTP_PID=$!
echo "HTTP服务器PID: $HTTP_PID"
sleep 3

# 2. 创建配置文件
echo "2. 创建配置文件..."
cat > subscheck/config/config.yaml << EOF
print-progress: true
concurrent: 20
check-interval: 120
timeout: 3000

alive-test-url: http://gstatic.com/generate_204
speed-test-url: ""
min-speed: 0
download-timeout: 1
download-mb: 0
total-speed-limit: 0

media-check: true
media-check-timeout: 10
platforms:
  - youtube
  - openai
  - gemini

rename-node: true
node-prefix: ""
success-limit: 0

output-dir: /home/geely/Documents/Github/free_v2ray_daily/output
listen-port: 0
save-method: local

enable-web-ui: false
api-key: ""

sub-store-port: 8299
sub-store-path: ""

github-proxy: ""
proxy: ""

keep-success-proxies: false
sub-urls-retry: 3
sub-urls-get-ua: clash.meta (https://github.com/beck-8/subs-check)

sub-urls:
  - http://127.0.0.1:8888/result/clash_subscription.yaml
EOF

# 3. 运行subs-check（60秒超时）
echo "3. 运行subs-check（60秒超时）..."
timeout 60 /home/geely/Documents/Github/free_v2ray_daily/subscheck/bin/subs-check -f /home/geely/Documents/Github/free_v2ray_daily/subscheck/config/config.yaml

# 4. 清理
echo "4. 清理..."
kill $HTTP_PID 2>/dev/null

echo "=== 测试完成 ==="