# W1 Day 2 微任务执行卡（已完成 ✅）

- **日期**：2026-11-27
- **最终聚焦靶标**：**`Scrape/spa/spa6`（`spa6.py` + `js/spa6_webpack.js`）** —— 永久在线、免登录的经典 Webpack 靶场（已移除过期失效的小红书旧代码，避免无正反馈的死磕）。
- **完成记录**：已吃透 `async with`、`Semaphore`、`TaskGroup`、`curl_cffi` 并沉淀至 `docs/notes/w01_day2_async.md`。

---

## 一、 第 1 段：现代异步与指纹封装走读 ✅
- [x] `sign_client.py`：`__aenter__` / `__aexit__` 异步上下文释放连接池、`httpx.Limits` 复用长连接、`trust_env=False` 跳过系统代理。
- [x] `http_client.py`：`curl_cffi` 纯协议模拟 Chrome TLS/HTTP2 指纹（无需浏览器与 CDP）。
- [x] `run_demo.py`：`asyncio.Semaphore` 并发阀门 + `asyncio.TaskGroup` 结构化并发任务组。

---

## 二、 第 2 段：`Scrape/spa6` 迁移前侦察契约表 ✅

| 侦察项 | 实测侦察结论（已完成） |
| :--- | :--- |
| **1. 核心入口函数与入参** | 原 `spa6_webpack.js` 无模块导出函数，核心计算入参为页码 `page`（或换算后的 `offset`） |
| **2. JS 侧外部依赖** | 纯 JS，无额外 npm 依赖 |
| **3. 输出字段与请求方式** | 生成字符串 `token`，直接拼进 URL Query 发起 GET 请求 |
| **4. 拟定 Fastify 接入契约（待周末编码实现）** | **当前尚未接入**；周末落地约定：请求 `POST /sign/spa6_webpack` 传 `{"payload": {"page": 1}}`，返回 `{"result": {"token": "..."}}`，并在 `spa6_webpack.js` 末尾补齐 `module.exports = { description, sign }` |

---

## 三、 周末半天实战计划（3~4 小时 · 高正反馈闭环）

1. **主线闭环（约 2.5 小时）：打通 `Scrape/spa6` 端到端现代采集流水线**
   - [ ] 将旧仓库 `spa6_webpack.js` 模块化接入 `sign_service/providers/spa6_webpack.js`（补齐 `module.exports`）。
   - [ ] 在 `src/spider_lab/cases/w01_spa6/` 中用 `Semaphore + TaskGroup` 通用骨架 + `SignServiceClient` + `BrowserLikeHttpClient (curl_cffi)` 并发抓完 `https://spa6.scrape.center/` 全部 10 页电影列表。
   - [ ] 将抓取结果逐条灌入 `CrawlRecord`（Pydantic v2）清洗并生成 `dedup_fingerprint` 去重指纹，导出标准 `movies.jsonl`（模拟路线 B 原始层落盘）。
   - [ ] 参照 `docs/templates/recall_card.md` 写完你的第一张「三分钟唤醒卡片」，提交 Git Commit！
2. **轻量热身（约 30 分钟）：`env_proxy.js` 补环境沙箱体验 ✅**
   - [x] 不碰失效的商业老代码，通过 `sign_service/sandbox/demo_env_proxy.js` 实测 `watchEnv` 吐 `[MISSING!]`、`onlyMissing: true` 降噪与 `protectToString` 伪装 `[native code]`（模拟风控 6/6 通关，复盘笔记见 `docs/notes/w01_env_proxy_warmup.md`）。
