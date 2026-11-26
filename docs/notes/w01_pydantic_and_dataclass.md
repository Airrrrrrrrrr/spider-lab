# W01 学习笔记：Pydantic v2 (`BaseModel`) 与 `@dataclass` 选型与核心装饰器

- **记录日期**：2026-11-26
- **关联代码**：`src/spider_lab/models/record.py`、`src/spider_lab/core/sign_client.py`

---

## 一、 核心概念复盘（费曼总结）

### 1. `@field_validator("xxx")`（Pydantic v2）
- **定位**：对指定字段做**入口清洗与异常拦截/预警**。
- **机制**：构造 `BaseModel` 实例时自动执行；可返回清洗后的新值覆盖原字段，发现非法数据则抛出 `ValidationError`，供外层 `try...except` 捕获记日志或触发站点改版告警。
- **补充细节**：
  - 支持同时校验多个字段，如 `@field_validator("title", "content")`；
  - 字段本身是否允许为空，由类型声明和 `Field(...)` 决定（业务允许为空的字段应声明为 `str | None = Field(default=None)` 或 `str = Field(default="")`，避免误报）。

### 2. `@computed_field`（Pydantic v2，配合 `@property`）
- **定位**：用于**由已清洗字段动态组合计算、且下游序列化需要输出**的派生字段。
- **典型场景**：将清洗后的 `source_id`、`item_id`、`title`、`content` 拼接计算 SHA-256 幂等去重指纹（`dedup_fingerprint`）。
- **与普通 `@property` 的区别**：调用 `model_dump()` / `model_dump_json()` 导出字典或 JSON 入库（Mongo / Kafka / MySQL / ClickHouse）时，普通 `@property` 不会出现，而 `@computed_field` 会作为正式字段一并序列化输出。

### 3. `@dataclass(slots=True, frozen=True)`（Python 标准库）
- **定位**：用于**程序内部流转、确定不需要清洗**的纯数据结构（如签名服务返回值 `SignResult`、内部配置项；原生 Scrapy 2.0+ 也支持直接 `yield` `@dataclass` 作为 Item）。
- **优缺点精确区分**：
  - **优点**：写法极简（自动生成 `__init__` / `__repr__` / `__eq__`）；**加上 `slots=True` 可显著节省内存并加快属性访问**（不生成 `__dict__`）；**加上 `frozen=True` 可锁定只读，防止并发篡改**。
  - **缺点**：**不做运行时类型强制校验**，如果上游传入了错误类型，构造时不会拦截，问题会延迟到下游业务使用时才暴露。

---

## 二、 实战选型口诀

| 场景 | 推荐方案 | 核心原因 |
| :--- | :--- | :--- |
| 外部脏数据边界（网页抓取、接口解析、AI 结构化抽取、入库记录） | `Pydantic BaseModel` | 强类型质检 + 自动清洗 + 派生指纹 + 原生 JSON 序列化 |
| 内部受控小结构体（RPC 返回值、任务参数、无需清洗的纯数据容器） | `@dataclass(slots=True, frozen=True)` | 零校验开销、省内存（`slots=True`）、并发只读安全（`frozen=True`） |
