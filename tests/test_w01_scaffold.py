"""W1 基础脚手架自动化验收测试。"""

from __future__ import annotations

import sys

from spider_lab.core.http_client import BrowserLikeHttpClient
from spider_lab.models.record import CrawlRecord


def test_python_312_isolated_runtime() -> None:
    """确保测试运行在 Python 3.12 独立虚拟环境中，而非全局 3.6.8。"""
    assert sys.version_info[:2] == (3, 12)
    assert sys.prefix != sys.base_prefix


def test_crawl_record_cleaning_and_fingerprint() -> None:
    """验证 Pydantic v2 空白规整与确定性去重指纹。"""
    r1 = CrawlRecord(
        source_id="qq_music",
        item_id="0039MnYb0qxYhV",
        url="https://y.qq.com/n/ryqq/songDetail/0039MnYb0qxYhV",
        title="  晴天 \n\t 周杰伦  ",
        content="故事的小黄花",
    )
    r2 = CrawlRecord(
        source_id="qq_music",
        item_id="0039MnYb0qxYhV",
        url="https://y.qq.com/n/ryqq/songDetail/0039MnYb0qxYhV",
        title="晴天 周杰伦",
        content="故事的小黄花",
    )
    assert r1.title == "晴天 周杰伦"
    assert r1.dedup_fingerprint == r2.dedup_fingerprint
    assert len(r1.dedup_fingerprint) == 24


async def test_browser_like_client_context() -> None:
    """验证 curl_cffi 异步指纹会话可正常初始化与关闭。"""
    async with BrowserLikeHttpClient(impersonate="chrome") as client:
        assert client.impersonate == "chrome"
