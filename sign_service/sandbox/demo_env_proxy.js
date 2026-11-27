/**
 * W1 轻量热身：env_proxy.js 补环境沙箱体验实验
 *
 * 运行命令（在 D:\spider 根目录执行）：
 *   node sign_service/sandbox/demo_env_proxy.js
 *
 * 实验目标：
 *   1. 观察 watchEnv 如何用 Proxy 自动吐出 [GET] / [MISSING!] / [SET] 轨迹；
 *   2. 观察 protectToString 如何用 Symbol 伪装 [native code]，并实现 Function.prototype.toString 自保护；
 *   3. 动手修复下方 3 处 TODO，让模拟风控检测从 3/6 变成 6/6 全部通过！
 */

'use strict';

const { watchEnv, protectToString } = require('./env_proxy');

// =========================================================
// 第一部分：构造伪造浏览器环境（你的“补环境工作台”）
// =========================================================
const rawWindow = {
  navigator: {
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0',
    webdriver: false,
    plugins: [0]
    // TODO 1: 运行后查看 [MISSING!] 日志，补齐缺失的插件数组（至少 1 个元素）
  },
  screen:{
      width: 1024,
      length: 1440
  },
  document: {
    cookie: 'session_id=demo_123',
    // TODO 3: 用 protectToString(..., 'createElement') 包裹下面的函数，防止 toString 检测暴露源码
    createElement: protectToString(function createElement(tag) {
      return { tagName: String(tag).toUpperCase() };
    }, 'createElement'),
  },
  // 对照组示例：已经用 protectToString 伪装成浏览器原生函数
  atob: protectToString(function atob(b64) {
    return Buffer.from(b64, 'base64').toString('utf8');
  }, 'atob'),
  // TODO 2: 运行后查看 [MISSING!] 日志，补齐缺失的屏幕对象（要求 width >= 1024）
};

// 给环境套上监控代理（实战噪音大时，可把 onlyMissing 改为 true 只盯缺失属性）
const proxyWindow = watchEnv(rawWindow, 'window', { onlyMissing: true });

// =========================================================
// 第二部分：模拟网页风控脚本的环境检测逻辑（无需修改）
// =========================================================
function mockAntiBotCheck(win) {
  const results = [];
  const nav = win.navigator;
  const doc = win.document;

  // 检查 1 & 2：基础 navigator 指纹（已补齐）
  results.push({
    name: '1. navigator.userAgent 包含 Chrome',
    pass: typeof nav.userAgent === 'string' && nav.userAgent.includes('Chrome'),
  });
  results.push({
    name: '2. navigator.webdriver 为 false',
    pass: nav.webdriver === false,
  });

  // 检查 3 & 4：深度环境探测（未补齐，触发 [MISSING!] 报警）
  results.push({
    name: '3. navigator.plugins 非空',
    pass: Array.isArray(nav.plugins) && nav.plugins.length > 0,
  });
  results.push({
    name: '4. screen.width >= 1024',
    pass: Boolean(win.screen && win.screen.width >= 1024),
  });

  // 检查 5：检测补出来的函数是不是“假原生函数”
  const createElStr = doc.createElement.toString();
  const createElWorks = doc.createElement('div')?.tagName === 'DIV';
  results.push({
    name: '5. document.createElement 伪装为 [native code]',
    pass: createElWorks && /\[native code\]/.test(createElStr),
    detail: createElStr.replace(/\s+/g, ' ').slice(0, 65),
  });

  // 检查 6：对照组 —— protectToString 与 Function.prototype.toString 自保护
  const atobStr = win.atob.toString();
  const toStringSelf = Function.prototype.toString.toString();
  results.push({
    name: '6. atob 与 Function.prototype.toString 自保护',
    pass:
      win.atob('aGVsbG8=') === 'hello' &&
      atobStr === 'function atob() { [native code] }' &&
      toStringSelf === 'function toString() { [native code] }',
    detail: `atob => ${atobStr} | toString => ${toStringSelf}`,
  });

  // 模拟风控往 window 写状态标记（触发 [SET] 日志）
  win._anti_bot_done = true;

  return results;
}

// =========================================================
// 第三部分：运行并输出检测报告
// =========================================================
console.log('=== [1] Proxy 环境访问轨迹日志 ===');
const checks = mockAntiBotCheck(proxyWindow);

console.log('\n=== [2] 模拟风控检测报告 ===');
let passed = 0;
for (const item of checks) {
  if (item.pass) passed += 1;
  const icon = item.pass ? '✅' : '❌';
  console.log(`${icon} ${item.name}`);
  if (item.detail) {
    console.log(`   ↳ 实测返回值: ${item.detail}`);
  }
}

console.log(`\n总计通过: ${passed} / ${checks.length}`);
if (passed === checks.length) {
  console.log('🎉 全部通过！成功骗过模拟风控检测！');
} else {
  console.log('⚠️ 被风控识别为补环境！请对照上面的 [MISSING!] 和实测返回值，修补代码中的 TODO 1~3 后再跑一次。');
}
