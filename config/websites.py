#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网站配置文件
"""

# 目标网站列表
WEBSITES = {
    "freeclashnode": {
        "name": "FreeClashNode",
        "url": "https://www.freeclashnode.com/free-node/",
        "enabled": True,
        "selectors": [
            '.post-title a',
            'h2 a',
            '.entry-title a',
            'article h2 a'
        ],
        "patterns": [
            r'node\.freeclashnode\.com/uploads/\d{4}/\d{2}/[^\\s\\<]*\.(?:txt|yaml|json)'
        ]
    },
    "mibei77": {
        "name": "米贝节点",
        "url": "https://www.mibei77.com/",
        "enabled": True,
        "selectors": [
            '.post h2 a',
            '.entry-title a',
            'h1 a',
            '.post-title a'
        ],
        "patterns": [
            r'https?://[^\s\'"]*?/sub[^\s\'"]*?',
            r'https?://[^\s\'"]*?/subscribe[^\s\'"]*?'
        ]
    },
    "clashnodev2ray": {
        "name": "ClashNodeV2Ray",
        "url": "https://clashnodev2ray.github.io/",
        "enabled": True,
        "selectors": [
            'a[href*="/2025/12/23/"]',
            'h1 a',
            '.post-title a',
            'article h1 a',
            'h2 a'
        ],
        "patterns": [
            r'vmess://[^\s\n\r]+',
            r'vless://[^\s\n\r]+',
            r'trojan://[^\s\n\r]+'
        ]
    },
    "proxyqueen": {
        "name": "ProxyQueen",
        "url": "https://www.proxyqueen.top/",
        "enabled": True,
        "selectors": [
            '.post-title a',
            'h2 a',
            '.entry-header a',
            'article h2 a'
        ],
        "patterns": [
            r'https?://[^\s\'"]*?(?:vmess|vless|trojan|hysteria|ss)[^\s\'"]*'
        ]
    },
    "wanzhuanmi": {
        "name": "玩转迷",
        "url": "https://wanzhuanmi.com/",
        "enabled": True,
        "selectors": [
            'a[href*="/archives/1259"]',
            'a[href*="/archives/"]',
            '.post-title a',
            'h2 a',
            '.entry-title a',
            'article h2 a'
        ],
        "patterns": [
            r'https?://[^\s\'"]*?\.(?:top|com|org|net|io|gg|tk|ml)[^\s\'"]*(?:/sub|/api|/link)[^\s\'"]*'
        ]
    },
    "cfmem": {
        "name": "CFMem",
        "url": "https://www.cfmem.com/",
        "enabled": True,
        "selectors": [
            '.post-title a',
            'h2 a',
            '.entry-title a',
            'article h2 a',
            '.content h2 a'
        ],
        "patterns": [
            r'https?://[^\s\'"]*?\.txt[^\s\'"]*',
            r'https?://[^\s\'"]*?/sub[^\s\'"]*',
            r'https?://[^\s\'"]*?/subscribe[^\s\'"]*'
        ]
    }
}

# 通用选择器（当特定网站选择器失败时使用）
UNIVERSAL_SELECTORS = [
    'article:first-child a',
    '.post:first-child a',
    '.entry-title:first-child a',
    'h1 a',
    'h2:first-child a',
    '.latest-post a',
    'a[href*="/post/"]',
    'a[href*="/article/"]',
    'a[href*="/node/"]',
    'a[href*="/free/"]'
]

# 时间选择器（用于查找最新文章）
TIME_SELECTORS = [
    'time',
    '.post-date',
    '.entry-date',
    '.published',
    '[datetime]'
]

# 订阅链接关键词
SUBSCRIPTION_KEYWORDS = [
    '订阅', 'subscription', 'sub', 'link', '节点', 'nodes', '配置', 'config'
]

# 订阅链接模式
SUBSCRIPTION_PATTERNS = [
    r'https?://[^\s\'"\.]*\.?[^\s\'"]*(?:/sub|/subscribe|/link|/api|/node|/v2)[^\s\'"]*',
    r'["\']((?:https?://[^\s\'"]*?/sub[^\s\'"]*?))["\']',
    r'["\']((?:https?://[^\s\'"]*?/subscribe[^\s\'"]*?))["\']',
    r'["\']((?:https?://[^\s\'"]*?/link[^\s\'"]*?))["\']',
    r'["\']((?:https?://[^\s\'"]*?/api[^\s\'"]*?))["\']',
    r'["\']((?:https?://[^\s\'"]*?\.txt))["\']',  # 通用.txt文件模式
    r'https?://[^\s\'"\)]*\.txt',  # 独立的.txt文件模式
]

# 节点协议模式
NODE_PATTERNS = [
    r'(vmess://[^\s\n\r]+)',
    r'(vless://[^\s\n\r]+)',
    r'(trojan://[^\s\n\r]+)',
    r'(hysteria2://[^\s\n\r]+)',
    r'(hysteria://[^\s\n\r]+)',
    r'(ss://[^\s\n\r]+)',
    r'(ssr://[^\s\n\r]+)'
]

# 代码块选择器
CODE_BLOCK_SELECTORS = [
    r'<(?:code|pre)[^>]*>(.*?)</(?:code|pre)>',
    r'<div[^>]*class="[^"]*(?:node|config|subscription)[^"]*"[^>]*>(.*?)</div>',
    r'<textarea[^>]*>(.*?)</textarea>',
    r'<input[^>]*value="([^"]*(?:vmess|vless|trojan|hysteria|ss://)[^"]*)"',
]

# Base64模式
BASE64_PATTERNS = [
    r'([A-Za-z0-9+/]{50,}={0,2})',
]