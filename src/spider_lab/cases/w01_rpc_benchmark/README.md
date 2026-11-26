# W01 唤醒卡片：跨语言签名微服务 vs 传统子进程压测对比

## 1. 目标概览
- **案例名称**：`W01 工程化破冰 — Fastify 常驻签名服务 vs 传统 execjs/subprocess 性能对比`
- **防护类型标签**：`[架构升级 / Node微服务 / Python3.12协程 / Pydantic建模]`
- **复盘日期**：`2026-11-26`

## 2. 核心痛点与重构动机
- **旧仓库痛点**：在过往 `药监局.py` 与 `小红薯/main.py` 中，每次请求都通过 `subprocess.run(['node', ...])` 或 `execjs` 重新拉起 V8 进程并编译大段 JS，单次开销高达数十至上百毫秒，无法支撑生产级异步并发。
- **新架构解法**：Node.js `Fastify` 进程一次加载补环境与 Webpack 模块常驻内存，Python 3.12 侧通过 `httpx.AsyncClient` 长连接池并发请求签名。

## 3. 本地一键运行命令
```powershell
# 直接单命令运行（若未手动启动 sign_service，脚本会自动临时拉起并在结束后优雅关闭）
uv run python -m spider_lab.cases.w01_rpc_benchmark.run_demo
```
