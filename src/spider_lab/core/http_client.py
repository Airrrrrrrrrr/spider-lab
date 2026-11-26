"""基于 curl_cffi 的现代浏览器 TLS (JA3/JA4) 与 HTTP/2 指纹异步客户端封装。

设计初衷：
在过往练习（如猿人学 19 题）中曾借助较重的 DrissionPage SessionPage 绕过指纹校验；
现在直接在纯协议高并发层使用 curl_cffi 模拟真实 Chrome 握手特征。
"""

from __future__ import annotations

from typing import Any

from curl_cffi.requests import AsyncSession, Response


class BrowserLikeHttpClient:
    """自带浏览器级 TLS / HTTP2 指纹伪造的异步请求会话。"""

    def __init__(
        self,
        impersonate: str = "chrome",
        timeout: float = 15.0,
        headers: dict[str, str] | None = None,
        proxy: str | None = None,
    ) -> None:
        self.impersonate = impersonate
        self._session = AsyncSession(
            impersonate=impersonate,
            timeout=timeout,
            headers=headers or {},
            proxy=proxy,
        )

    async def __aenter__(self) -> BrowserLikeHttpClient:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._session.close()

    async def get(self, url: str, **kwargs: Any) -> Response:
        return await self._session.get(url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> Response:
        return await self._session.post(url, **kwargs)
