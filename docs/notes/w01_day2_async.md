# W01 Day 2 学习笔记：现代 Python 异步并发、`curl_cffi` 指纹与微服务契约

- **记录日期**：2026-11-27
- **关联代码**：`src/spider_lab/core/sign_client.py`、`src/spider_lab/core/http_client.py`、`src/spider_lab/cases/w01_rpc_benchmark/run_demo.py`

---

## 一、 核心概念复盘（费曼总结 + 精度校准）

### 1. `async with`（异步上下文管理器）
- **定位**：异步版的 `with open(...)`，依赖类的 `__aenter__`（进场）与 `__aexit__`（离场）方法。
- **工程价值**：退出代码块时**自动执行 `await` 释放异步资源**（如关闭 `httpx.AsyncClient` 连接池或 `curl_cffi` 会话），哪怕中间抛异常也不会发生连接泄漏或端口耗尽。
- **配合 `httpx.Limits` 连接池**：复用 TCP/TLS 长连接（Keep-Alive），省掉每次重复握手耗时；本地 RPC 客户端加 `trust_env=False` 可绕过系统代理并跳过 Windows 注册表代理查询开销。

### 2. `asyncio.Semaphore(N)`（并发限流信号量）
- **定位**：**并发阀门 / N 张入场券**（等价于 Scrapy `settings.py` 中的 `CONCURRENT_REQUESTS = N`）。
- **概念校准**：它本身**不创建 Worker**，而是限制同时进入 `async with sem:` 代码块的协程上限。哪怕外面塞了 10,000 个任务，同一时刻最多也只放行 N 个真正发请求，防打爆本机端口或触发目标风控。

### 3. `asyncio.TaskGroup`（结构化并发任务组）
- **定位**：**并发总管**（Python 3.11+ 引入）。
- **概念校准**：区别于先进先出的任务队列（`asyncio.Queue`），`TaskGroup` 用于把一批协程打包**同时并发发车并统一等待全部完成**；一旦组内某个任务抛异常，会自动取消清理其余残余任务，杜绝“僵尸协程”。

### 4. `curl_cffi` (`AsyncSession(impersonate="chrome")`)
- **定位**：**纯协议层高并发浏览器指纹伪造客户端**（零浏览器、不走 CDP、内存极低）。
- **核心优势**：底层集成与真实 Chrome 同源的 BoringSSL 加密库，能在纯 HTTP 请求阶段字节级模拟真实浏览器的 **TLS 握手指纹（JA3/JA4）与 HTTP/2 帧头特征**。

### 5. 统一签名网关为何用 `POST JSON` 信封？
- 单个简单站点（如 `spa6` 仅传 `page` 返回 `token`）看似用 Query 参数更省事；
- 但统一网关要兼容未来复杂的 POST Body、嵌套对象、中文或几 KB 长的动态 `<meta content>`（URL 有长度限制和转义坑），统一约定 `POST /sign/:provider` + `{"payload": {...}}` -> `{"result": {...}}` 可让 Python 端 `SignServiceClient` **一行不改通吃所有站点**。

---

## 二、 Python 3.12 异步爬虫通用 10 行骨架（直接套用）

```python
import asyncio

sem = asyncio.Semaphore(10)  # 等价于 Scrapy 的 CONCURRENT_REQUESTS = 10

async def fetch_one(page: int) -> str:
    async with sem:          # 领入场券，最多 10 个同时发请求
        # res = await client.get(...)
        return f"page-{page}"  # 离开块自动还券

async def main() -> None:
    async with asyncio.TaskGroup() as tg:  # 并发发车，等全部完成
        tasks = [tg.create_task(fetch_one(p)) for p in range(1, 51)]

    results = [t.result() for t in tasks]
```
