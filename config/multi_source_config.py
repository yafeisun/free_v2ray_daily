# 多源节点收集配置
MULTI_SOURCE_CONFIG = {
    "telegram": {
        "name": "Telegram节点收集",
        "enabled": False,  # 需要环境变量配置
        "priority": 9,
        "bot_token": "",  # 从环境变量获取
        "channels": [
            # 示例频道（需要替换为实际的）
            "@nim_vpn_ir",
            "@Alpha_V2ray_Iran",
            "@V2RayRootFree",
            "@Farah_VPN",
        ],
        "keywords": ["vmess", "vless", "trojan", "ss://", "节点"],
        "api_delay": 1.0,
        "max_messages": 50,
        "update_interval": 1800,
    },
    "github": {
        "name": "GitHub项目聚合",
        "enabled": False,  # 需要环境变量配置
        "priority": 8,
        "github_token": "",  # 从环境变量获取
        "repositories": [
            {
                "owner": "Loyalsoldier",
                "repo": "v2ray_node_list",
                "files": ["*.txt", "nodes/*.txt"],
            },
            {"owner": "paimonhub", "repo": "v2ray-free", "files": ["*.txt", "*.md"]},
            {"owner": "ermaozi", "repo": "Free-VPN", "files": ["*.txt", "*.yaml"]},
        ],
        "timeout": 30,
        "max_files": 20,
    },
    "community": {
        "name": "社区贡献节点",
        "enabled": True,
        "priority": 7,
        "submission_endpoint": "/api/submit",
        "validation_enabled": True,
        "max_submissions_per_hour": 10,
        "require_email": False,
    },
    "validation": {
        "name": "实时节点验证",
        "enabled": True,
        "max_concurrent": 50,
        "connect_timeout": 5,
        "test_timeout": 30,
        "min_quality_score": 0.6,
        "enable_streaming_test": True,
        "enable_bandwidth_test": True,
        "enable_geo_detection": True,
    },
}
