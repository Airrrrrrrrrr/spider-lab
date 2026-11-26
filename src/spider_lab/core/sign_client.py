"""异步常驻签名微服务客户端（彻底替代低效的 execjs 与临时文件落盘 subprocess）。"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(slots=True, frozen=True)
class SignResult:
    """签名服务返回结果结构。"""

    provider: str
    data: dict[str, Any]
    node_cost_ms: float
    roundtrip_ms: float


class SignServiceClient:
    """对接本地/内网 Node.js Fastify 签名服务的异步连接池客户端。"""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:3001",
        timeout: float = 5.0,
        max_connections: int = 100,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_connections,
        )
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            limits=limits,
            trust_env=False,  # 本地内网 RPC 禁用系统代理注册表轮询，显著降低 Windows 延迟
        )

    async def __aenter__(self) -> SignServiceClient:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def health(self) -> dict[str, Any]:
        """检查 Node.js 签名微服务存活状态与运行时版本。"""
        resp = await self._client.get("/health")
        resp.raise_for_status()
        return resp.json()

    async def sign(self, provider: str, payload: dict[str, Any]) -> SignResult:
        """调用指定 provider 生成加密签名或动态 Cookie。"""
        start = time.perf_counter()
        resp = await self._client.post(f"/sign/{provider}", json={"payload": payload})
        roundtrip_ms = (time.perf_counter() - start) * 1000

        if resp.status_code != 200:
            detail = resp.text
            raise RuntimeError(
                f"签名服务调用失败 [provider={provider}, status={resp.status_code}]: {detail}"
            )

        body = resp.json()
        return SignResult(
            provider=provider,
            data=body["result"],
            node_cost_ms=float(body.get("cost_ms", 0.0)),
            roundtrip_ms=round(roundtrip_ms, 3),
        )
