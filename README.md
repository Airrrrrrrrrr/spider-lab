# Spider Lab — 现代爬虫逆向工程化与 AI 数据架构实验室

本仓库用于承接 **16 周可持续进阶计划（路线 B：数据架构与 AI 赋能）**，将过往单脚本逆向经验升级为**高并发跨语言微服务 + 现代异步指纹采集 + 高质量数据流水线**。

完整六层知识体系与 16 周打卡清单见：[docs/roadmap.md](./docs/roadmap.md)

---

## 一、 双轨环境隔离铁律（保护本机工作用 Python 3.6.8）

本机全局环境变量中的 `python` 保持为日常工作所需的 **`Python 3.6.8`**，**不做任何修改**。

在本仓库中，一律通过 **`uv`** 调用项目内独立的 `.venv`（**`Python 3.12`**）：

| 场景 | 执行命令 | 实际运行的解释器 |
| :--- | :--- | :--- |
| **日常公司项目（任意其他目录）** | `python xxx.py` / `scrapy crawl ...` | 全局 `Python 3.6.8`（零影响） |
| **本仓库运行脚本** | `uv run python -m spider_lab.cases.w01_rpc_benchmark.run_demo` | 隔离 `.venv` (`Python 3.12`) |
| **本仓库安装新库** | `uv add <package>` | 仅写入本仓库 `.venv` 与 `pyproject.toml` |
| **本仓库运行测试 / 代码检查** | `uv run pytest` / `uv run ruff check .` | 隔离 `.venv` (`Python 3.12`) |
| **一键核验双轨隔离状态** | `python scripts/verify_isolation.py` 与 `uv run python scripts/verify_isolation.py` | 直观对比全局 3.6.8 与项目 3.12 |

> **提示**：如果你在 VS Code / Antigravity 中打开本项目，可将工作区 Python 解释器指向本目录下的 `.venv\Scripts\python.exe`（仅对当前文件夹生效）。

---

## 二、 目录结构说明

```text
spider/
├── .python-version              # 供 uv 自动识别 Python 3.12（不影响全局 cmd/powershell 的 python）
├── pyproject.toml               # Python 3.12 依赖管理 (httpx / curl_cffi / pydantic v2 / loguru)
├── docs/
│   ├── roadmap.md               # 六层知识体系与 16 周路线图（锁定路线 B：数据架构与 AI 赋能）
│   └── templates/recall_card.md # 「三分钟唤醒卡片」标准复盘模板
├── sign_service/                # Node.js + Fastify 常驻高性能签名微服务（彻底替代 execjs / 写临时文件）
│   ├── server.js                # 统一签名网关 (/health, /providers, /sign/:provider)
│   ├── sandbox/env_proxy.js     # 升级版 Proxy 补环境监控与 toString Symbol 保护底座
│   └── providers/               # 独立算法/补环境模块槽位（含 demo_hmac、qq_music_webpack、xhs_mnsv2）
├── src/spider_lab/
│   ├── core/sign_client.py      # 异步连接池签名客户端 (对接 Node Fastify 服务)
│   ├── core/http_client.py      # 基于 curl_cffi 的 Chrome TLS/JA3 & HTTP/2 指纹请求封装
│   ├── models/record.py         # Pydantic v2 强类型采集数据校验与幂等指纹模型
│   └── cases/w01_rpc_benchmark/ # 第 1 周破冰联调与并发基准压测案例
├── scripts/verify_isolation.py  # 双轨环境零污染自检脚本
└── tests/                       # 自动化单元测试
```

---

## 三、 第 1 周（W1）快速启动与打卡指南

### 1. 启动联调与压测演示
打开两个终端（工作目录均为本仓库根目录）：

```powershell
# 终端 1：启动 Node.js Fastify 常驻签名微服务（默认监听 127.0.0.1:3001）
npm --prefix sign_service start

# 终端 2：使用隔离的 Python 3.12 运行异步并发签名压测 + TLS 指纹验证
uv run python -m spider_lab.cases.w01_rpc_benchmark.run_demo
```

### 2. 本周微任务拆解（每晚 30 分钟 + 周末半天）
- [ ] **周内微任务 1（30m）**：阅读 `src/spider_lab/models/record.py` 与 `core/` 下两个封装，熟悉 Python 3.12 类型注解、`asyncio.TaskGroup` 与 `Pydantic v2` 校验器写法。
- [ ] **周内微任务 2（30m）**：从旧仓库拉取 `音乐/QQ/QQMusic.js`，梳理其 Webpack 导出入口与入参格式。
- [ ] **周末半天实战（3~4h）**：
  1. 将 `QQMusic` Webpack 签名填入 `sign_service/providers/qq_music_webpack.js`；
  2. 将旧仓库 `小红薯` 补环境代码接入 `sign_service/providers/xhs_mnsv2.js`（尝试配合 `sandbox/env_proxy.js` 清理旧版 `eval` 代理）；
  3. 参照 `docs/templates/recall_card.md` 为这两个旧案补齐「三分钟唤醒卡片」，提交你的第一次重构 Git Commit！
