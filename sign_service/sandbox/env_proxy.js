/**
 * 标准化补环境代理与 Function.prototype.toString 保护底座
 *
 * 【对比你旧仓库 小红薯/proxy.js 的升级点】：
 * 1. 彻底移除粗糙的 eval 字符串拼接，改用原生 Proxy + WeakSet 防循环引用递归代理；
 * 2. 内置 Symbol/内置属性噪音白名单过滤，日志直接输出清晰的缺失属性路径（如 window.navigator.plugins -> undefined）；
 * 3. 完整闭环的 protectToString(fn, nativeName)，防止风控通过 fn.toString() 检测 Hook 或伪造的宿主函数。
 */

'use strict';

const NATIVE_STR_SYMBOL = Symbol('native_function_source');
const originalFunctionToString = Function.prototype.toString;

// 安装一次全局安全的 Function.prototype.toString 拦截器（自保护）
let isToStringPatched = false;
function installSafeToString() {
  if (isToStringPatched) return;
  const customToString = function toString() {
    if (typeof this === 'function' && this[NATIVE_STR_SYMBOL]) {
      return this[NATIVE_STR_SYMBOL];
    }
    return originalFunctionToString.call(this);
  };
  Object.defineProperty(customToString, NATIVE_STR_SYMBOL, {
    enumerable: false,
    configurable: false,
    writable: false,
    value: 'function toString() { [native code] }',
  });
  Object.defineProperty(Function.prototype, 'toString', {
    enumerable: false,
    configurable: true,
    writable: true,
    value: customToString,
  });
  isToStringPatched = true;
}

/**
 * 将自定义补环境函数伪装成浏览器原生 [native code] 函数
 * @param {Function} fn 目标函数
 * @param {string} [funcName] 显示的函数名（默认取 fn.name）
 */
function protectToString(fn, funcName) {
  installSafeToString();
  const name = funcName !== undefined ? funcName : fn.name || '';
  Object.defineProperty(fn, NATIVE_STR_SYMBOL, {
    enumerable: false,
    configurable: false,
    writable: false,
    value: `function ${name}() { [native code] }`,
  });
  return fn;
}

const IGNORED_PROPS = new Set([
  'Symbol(Symbol.toPrimitive)',
  'Symbol(Symbol.toStringTag)',
  'Symbol(nodejs.util.inspect.custom)',
  'valueOf',
  'toJSON',
]);

/**
 * 为宿主对象（window / document / navigator / location 等）挂载缺失属性监控代理
 * @param {object} target 被代理对象
 * @param {string} label 对象路径标签，例如 "window"
 * @param {{ silent?: boolean, onlyMissing?: boolean }} [options]
 */
function watchEnv(target, label = 'env', options = {}) {
  const { silent = false, onlyMissing = false } = options;
  const seen = new WeakSet();

  function wrap(obj, pathLabel) {
    if (obj === null || (typeof obj !== 'object' && typeof obj !== 'function')) {
      return obj;
    }
    if (seen.has(obj)) return obj;

    const proxy = new Proxy(obj, {
      get(t, prop, receiver) {
        const propName = String(prop);
        const val = Reflect.get(t, prop, receiver);

        if (!silent && !IGNORED_PROPS.has(propName)) {
          const isMissing = val === undefined && !(prop in t);
          if (!onlyMissing || isMissing) {
            const tag = isMissing ? '[MISSING!]' : '[GET]';
            console.log(`${tag} ${pathLabel}.${propName} -> (${typeof val})`, isMissing ? '' : val);
          }
        }
        if (val !== null && typeof val === 'object') {
          return wrap(val, `${pathLabel}.${propName}`);
        }
        return val;
      },
      set(t, prop, value, receiver) {
        if (!silent) {
          console.log(`[SET] ${pathLabel}.${String(prop)} = (${typeof value})`);
        }
        return Reflect.set(t, prop, value, receiver);
      },
    });

    seen.add(proxy);
    return proxy;
  }

  return wrap(target, label);
}

module.exports = {
  installSafeToString,
  protectToString,
  watchEnv,
};
