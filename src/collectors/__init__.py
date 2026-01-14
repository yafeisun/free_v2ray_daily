# 爬虫模块初始化文件

from .clashnodecc import ClashNodeCCCollector
from .cfmem import CfmemCollector
from .clashnodev2ray import ClashNodeV2RayCollector
from .freeclashnode import FreeClashNodeCollector
from .mibei77 import Mibei77Collector
from .proxyqueen import ProxyQueenCollector
from .wanzhuanmi import WanzhuanmiCollector
from .datiya import DatiyaCollector
from .telegeam import TelegeamCollector
from .clashgithub import ClashGithubCollector
from .freev2raynode import FreeV2rayNodeCollector
from .eighty_five_la import EightyFiveLaCollector
from .oneclash import OneClashCollector

# 收集器映射表
COLLECTOR_MAPPING = {
    "freeclashnode": FreeClashNodeCollector,
    "mibei77": Mibei77Collector,
    "clashnodev2ray": ClashNodeV2RayCollector,
    "proxyqueen": ProxyQueenCollector,
    "wanzhuanmi": WanzhuanmiCollector,
    "cfmem": CfmemCollector,
    "clashnodecc": ClashNodeCCCollector,
    "datiya": DatiyaCollector,
    "telegeam": TelegeamCollector,
    "clashgithub": ClashGithubCollector,
    "oneclash": OneClashCollector,
    "freev2raynode": FreeV2rayNodeCollector,
    "85la": EightyFiveLaCollector,
}


def get_collector_instance(site_key: str, site_config: dict):
    """获取收集器实例"""
    collector_key = site_config.get("collector_key", site_key)
    collector_class = COLLECTOR_MAPPING.get(collector_key)

    if collector_class:
        return collector_class(site_config)
    else:
        print(f"❌ 未找到收集器: {collector_key}")
        return None


def run_collector(site_key: str, site_config: dict) -> bool:
    """运行收集器"""
    collector = get_collector_instance(site_key, site_config)
    if not collector:
        return False

    try:
        print(f"🚀 开始收集 {site_config['name']}...")
        result = collector.collect()
        if result:
            print(f"✅ {site_config['name']} 收集完成")
            return True
        else:
            print(f"❌ {site_config['name']} 收集失败")
            return False
    except Exception as e:
        print(f"❌ {site_config['name']} 运行异常: {e}")
        return False


def list_available_collectors():
    """列出所有可用的收集器"""
    return list(COLLECTOR_MAPPING.keys())
