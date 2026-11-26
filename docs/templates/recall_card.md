# 「三分钟唤醒卡片」标准复盘模板

> 每次攻克或重构一个站点后，用 3 分钟填写此卡片（控制在 30 行以内）。哪怕半年不碰，打开卡片 3 分钟即可完整找回破局思路。

## 1. 目标概览
- **站点 / 案例名称**：`例如：小红书 Web 搜索接口 (x-s / x-t)`
- **防护类型标签**：`[Webpack / OB混淆 / 瑞数6 / JSVMP / TLS指纹 / Protobuf / 滑块协议]`
- **复盘日期**：`YYYY-MM-DD`

## 2. 风控特征一句话识别
- **触发条件与核心参数**：`例如：请求头携带 X-s (以 XYS_ 开头) 与 X-t (13位时间戳)，缺失或失配返回 406 / -100`
- **会话绑定关系**：`例如：强绑定 Cookie 中的 a1 与 web_session，Payload JSON 字符串参与摘要计算`

## 3. 最快定位切入路径（5 行以内）
1. `抓包过滤 /api/sns/web/v1/search/notes，观察 Initiator 调用栈`
2. `注入 Header Hook 拦截 X-s，断停在拦截器 request 阶段`
3. `向上回溯 2 层定位核心签名入口 window._webmsxyw(uri, data)`

## 4. 核心坑点与风控检测项
- **环境检测点**：`例如：检测 navigator.webdriver、document.all typeof 特性、Canvas 指纹、Function.prototype.toString`
- **编码/协议坑点**：`例如：POST JSON 序列化不能有多余空格（需 separators=(',', ':')），TLS 需模拟 Chrome 指纹`

## 5. 本地一键复现命令
```powershell
# 1. 启动常驻签名微服务
npm --prefix sign_service start

# 2. 使用隔离的 Python 3.12 运行采集器（不影响全局 Python 3.6.8）
uv run python -m spider_lab.cases.<case_name>.run
```
