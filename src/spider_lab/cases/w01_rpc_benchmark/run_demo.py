"""第 1 周破冰实测：旧版『每次拉起 Node 子进程 (execjs)』 vs 新版『Fastify 常驻服务 + asyncio』。"""

from __future__ import annotations

import asyncio
import subprocess
import sys
import time
from pathlib import Path

from loguru import logger

from spider_lab.core.http_client import BrowserLikeHttpClient
from spider_lab.core.sign_client import SignServiceClient
from spider_lab.models.record import CrawlRecord

PROJECT_ROOT = Path(__file__).resolve().parents[4]
SERVER_JS = PROJECT_ROOT / "sign_service" / "server.js"


def benchmark_legacy_subprocess(iterations: int = 15) -> tuple[float, float]:
    """模拟旧仓库 execjs / subprocess.run(['node', ...]) 每次冷启动 Node V8 的耗时。"""
    inline_js = (
        "const crypto=require('node:crypto');"
        "const s=crypto.createHmac('sha256','salt').update(process.argv[1]).digest('hex');"
        "console.log(s);"
    )
    t0 = time.perf_counter()
    for i in range(iterations):
        subprocess.run(
            ["node", "-e", inline_js, f'{{"page":{i}}}'],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
    total_ms = (time.perf_counter() - t0) * 1000
    qps = iterations / (total_ms / 1000)
    return total_ms, qps


async def ensure_sign_service(client: SignServiceClient) -> subprocess.Popen[str] | None:
    """检查本地签名服务是否已运行；若未启动则自动拉起临时子服务供演示使用。"""
    try:
        health = await client.health()
        logger.info(
            f"检测到已运行的常驻签名服务: Node {health['node_version']} (PID={health['pid']})"
        )
        return None
    except Exception:
        logger.info("未检测到已启动的 sign_service，正在自动拉起本地 Fastify 常驻签名进程...")
        proc = subprocess.Popen(
            ["node", str(SERVER_JS)],
            cwd=str(SERVER_JS.parent),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
        )
        for _ in range(30):
            await asyncio.sleep(0.15)
            try:
                health = await client.health()
                logger.success(
                    f"Fastify 常驻签名服务就绪: Node {health['node_version']} "
                    f"| 模块: {health['providers']}"
                )
                return proc
            except Exception:
                continue
        proc.kill()
        raise RuntimeError("自动拉起 sign_service 超时，请检查 sign_service 依赖是否已安装。")


async def benchmark_modern_rpc(
    client: SignServiceClient, total_requests: int = 200, concurrency: int = 25
) -> tuple[float, float]:
    """使用 Python 3.12 TaskGroup + 信号量并发调用常驻签名微服务。"""
    sem = asyncio.Semaphore(concurrency)
    # 预热一次连接池
    await client.sign("demo_hmac", {"warmup": True})

    async def worker(idx: int) -> None:
        async with sem:
            res = await client.sign("demo_hmac", {"keyword": "爬虫架构进阶", "page": idx})
            assert "x-sign" in res.data

    t0 = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        for i in range(total_requests):
            tg.create_task(worker(i))
    total_ms = (time.perf_counter() - t0) * 1000
    qps = total_requests / (total_ms / 1000)
    return total_ms, qps


async def main() -> None:
    logger.info(f"当前运行环境: Python {sys.version.split()[0]} -> {sys.executable}")

    # 1. 演示路线 B 底座：Pydantic v2 结构化清洗与幂等去重指纹
    sample = CrawlRecord(
        source_id="xhs_notes",
        item_id="688983380000000003025cde",
        url="https://www.xiaohongshu.com/explore/688983380000000003025cde",
        title="  Python 3.12   现代爬虫与数据工程\n实战笔记  ",
        content="告别 execjs 与硬编码 Cookie，迈向常驻微服务与流式数仓。",
    )
    logger.info(
        f"[Pydantic v2 清洗结果] title='{sample.title}' | 幂等去重指纹={sample.dedup_fingerprint}"
    )

    # 2. 验证 curl_cffi Chrome 指纹会话初始化
    async with BrowserLikeHttpClient(impersonate="chrome") as browser_http:
        logger.info(
            f"[TLS 指纹客户端就绪] BrowserLikeHttpClient impersonate='{browser_http.impersonate}'"
        )

    # 3. 性能基准对比：旧版冷启动子进程 vs 新版常驻 Fastify 微服务
    legacy_iters = 15
    logger.info(f"开始测试旧方案（模拟 execjs 每次拉起 Node 子进程，共 {legacy_iters} 次）...")
    legacy_ms, legacy_qps = benchmark_legacy_subprocess(legacy_iters)

    proc: subprocess.Popen[str] | None = None
    async with SignServiceClient() as sign_client:
        try:
            proc = await ensure_sign_service(sign_client)
            modern_iters = 200
            logger.info(
                f"开始测试新方案（Python 3.12 协程并发请求常驻 Fastify，共 {modern_iters} 次）..."
            )
            modern_ms, modern_qps = await benchmark_modern_rpc(sign_client, modern_iters)
        finally:
            if proc is not None:
                proc.terminate()
                proc.wait(timeout=5)

    speedup = modern_qps / legacy_qps if legacy_qps > 0 else 0.0
    print("\n" + "=" * 72)
    print("W1 跨语言签名架构压测报告")
    print("-" * 72)
    print(
        f"旧方案 (subprocess/execjs 模式) : {legacy_iters:>4} 次耗时 {legacy_ms:>8.1f} ms "
        f"| 吞吐量 ~ {legacy_qps:>7.1f} req/s"
    )
    print(
        f"新方案 (Fastify 常驻 + asyncio) : {modern_iters:>4} 次耗时 {modern_ms:>8.1f} ms "
        f"| 吞吐量 ~ {modern_qps:>7.1f} req/s"
    )
    print(f"性能提升倍数                    : 约 {speedup:.1f}x 倍加速！")
    print("=" * 72)


if __name__ == "__main__":
    asyncio.run(main())
