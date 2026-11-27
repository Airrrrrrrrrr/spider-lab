# W01 轻量热身笔记：`env_proxy.js` 补环境监控与 `toString` 自保护

- **记录日期**：2026-11-27
- **关联代码**：`sign_service/sandbox/env_proxy.js`、`sign_service/sandbox/demo_env_proxy.js`
- **实战成果**：通过 `demo_env_proxy.js` 定位 `[MISSING!]` 与 `toString()` 暴露点，完成 3 处环境补齐（`navigator.plugins`、`screen`、`protectToString(createElement)`）与 `onlyMissing: true` 降噪验证，模拟风控从 `3/6` 提升至 `6/6` 全通过。

---

## 一、 核心机制复盘（费曼总结 + 精度校准）

### 1. `Proxy` + `Reflect` 拦截与读写转发
- **基本套路**：对宿主对象挂 `Proxy`，在 `get` / `set` 钩子里先打日志桩，再用 `Reflect.get(t, prop, receiver)` / `Reflect.set(t, prop, value, receiver)` 透传给原对象，保证不破坏原始读写语义。
- **精准判定缺失**：不是单看 `val === undefined`，而是组合 `val === undefined && !(prop in t)` —— `in` 会沿原型链排查，确保只有“原型链上真的没有该属性”时才打 `[MISSING!]` 报警。

### 2. 多层嵌套属性是如何被监控到的？（关键校准）
- **容易忽略的点**：原生 `new Proxy(window, ...)` **默认是浅层的**，只能拦到第一层 `window.navigator`，管不到更深层的 `window.navigator.plugins`。
- **`watchEnv` 的解法（懒递归套壳）**：在 `get` 拦截器中，一旦发现读出的值 `val` 是非空 `object`，就立刻 `return wrap(val, `${pathLabel}.${propName}`)` 给子对象动态套上一层新的 `Proxy` 并拼接路径名；配合 `WeakSet` 避免重复包装或循环引用死循环。
- **降噪技巧**：真实站点一次加密会读几百个属性，把 `{ onlyMissing: true }` 打开即可屏蔽正常 `[GET]` 噪音，只盯缺失属性。

### 3. `protectToString` 与 `Function.prototype.toString` 自保护
- **为什么必须保护假函数**：浏览器原生函数调用 `.toString()` 会返回 `'function xxx() { [native code] }'`；Node 里自己补的函数一调 `.toString()` 就会暴露自定义源码，直接触发风控。
- **隐藏 Symbol 身份证**：创建外部无法伪造或枚举的 `const NATIVE_STR_SYMBOL = Symbol('native_function_source')`，通过 `Object.defineProperty`（`enumerable: false`）挂在补出来的函数上，改写 `Function.prototype.toString` 检查该 Symbol。
- **为什么连 `Function.prototype.toString` 自己也要贴标签？**
  - 高阶风控（瑞数、JSVMP 等）不仅检测 `document.createElement.toString()`，还会反查 `Function.prototype.toString.toString()`，验证你是否 Hook 过 `toString` 本身！
  - 给 `customToString` 自己贴上 `NATIVE_STR_SYMBOL` 后，自检也会返回 `'function toString() { [native code] }'`，彻底闭合反侦察漏洞。

---

## 二、 实战踩坑备忘与 W3 进阶伏笔

1. **真实浏览器属性名小细节**：浏览器里屏幕分辨率属性是 `window.screen.width` 和 `window.screen.height`（不是 `length`），实战补环境时建议直接从真实 Chrome 控制台核对属性名与描述符。
2. **留给 W3 重构 `env_proxy.js` 的进阶点**：
   - 当前用 `WeakSet` 只记录了 `proxy`，若原对象存在 `rawWindow.self = rawWindow`，访问 `proxyWindow.self === proxyWindow` 会因二次包装返回 `false`；W3 升级为 `WeakMap`（缓存 `rawObj -> proxy` 映射）并补充原型链 `Object.getOwnPropertyDescriptors` 校验。
