# W1 Day 2 微任务执行卡（预计耗时：30 分钟）

- **日期**：2026-11-27（周五晚）
- **核心目标**：吃透现代 Python 异步上下文（`async with` / `asyncio.TaskGroup` / `Semaphore`），并完成旧仓库 `QQMusic` 的迁移前侦察，让周末半天实战直接丝滑开写，不卡壳。

---

## 时间分配清单（按顺序打卡，到点即停，绝不熬夜）

### 第 1 段（0–10 分钟）：走读现代异步与 TLS 指纹客户端
重点阅读以下 3 个文件，带着问题看代码（不用背语法，看懂执行顺序即可）：
1. `src/spider_lab/core/sign_client.py`
   - 关注：`__aenter__` / `__aexit__` 异步上下文管理器、`httpx.Limits` 连接池、为什么加 `trust_env=False`。
2. `src/spider_lab/core/http_client.py`
   - 关注：`curl_cffi` 的 `AsyncSession(impersonate="chrome")` 与你以前在 `yrx_19.py` 用 `DrissionPage.SessionPage` 绕 TLS 指纹相比，轻量在哪里？
3. `src/spider_lab/cases/w01_rpc_benchmark/run_demo.py`
   - 关注：`asyncio.Semaphore(25)` 限流信号量 + `async with asyncio.TaskGroup() as tg:`（Python 3.11+ 新增的现代并发写法，对比 Scrapy 里的 `CONCURRENT_REQUESTS`）。

### 第 2 段（10–25 分钟）：旧案侦察（准备周末把 `QQMusic` 迁入 Fastify）
打开你过去 GitHub 仓库的 `Airrrrrrrrrr/spider` -> `音乐/QQ/QQMusic.py` 与 `QQMusic.js`，**只看这 4 个问题并填进下方表格**（明天先不动手大改代码，把接口契约理清即可）：

| 侦察项 | 你的填写（直接记录在这里） |
| :--- | :--- |
| **1. 核心加密函数名与入参** | 例如：`getSign(data_str)`，入参是请求体 JSON 字符串还是对象？ |
| **2. 旧代码如何调用 JS** | 例如：当年是不是用 `execjs.compile(...).call(...)`？依赖哪些 Node 外部包（如 `crypto-js` / `jsdom`）？ |
| **3. 输出字段与请求方式** | 例如：返回 `zzc...` 放在 URL query 的 `sign=` 参数里，POST `https://u.y.qq.com/cgi-bin/musics.fcg` |
| **4. 是否有硬编码 Cookie/动态值** | 哪些 Header/Cookie 是死写进去的，周末迁移时打算怎么从 Python 端动态传参？ |

> **顺带准备素材（2 分钟）**：直接把旧仓库的 `QQMusic.js` 复制一份放到 `sign_service/providers/` 同级参考，周末半天就可以直接改造成 `module.exports = { sign }` 接入 `server.js`！

### 第 3 段（25–30 分钟）：费曼自检（3 句话验收）
合上代码，尝试用自己的话回答下面 3 个问题（明天做完可以直接发给我帮你核对并记入笔记）：
1. 在 `run_demo.py` 里，如果去掉 `asyncio.Semaphore(25)` 直接用 `TaskGroup` 并发发 10,000 个请求，会发生什么？它对应 Scrapy 里的哪个配置项？
2. `async with SignServiceClient() as client:` 相比直接 `client = SignServiceClient()`，在工程上有什么好处？
3. 为什么把 `QQMusic.js` 放进 Fastify 常驻服务，会比旧仓库里每次调用 `execjs` 快得多？

---

## 周末半天实战预告（提前心里有数）
- **任务 1**：完成 `sign_service/providers/qq_music_webpack.js` 并用 `uv run` 跑通异步请求 + 写出第一张「三分钟唤醒卡片」。
- **任务 2**：按同样套路将 `小红薯` 补环境接入 `sign_service/providers/xhs_mnsv2.js`（顺便对比体验 `sandbox/env_proxy.js`）。
