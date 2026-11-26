/**
 * 【W1 周末实战槽位 2】：迁移旧仓库 Airrrrrrrrrr/spider/小红薯 (x-s / x-t 补环境)
 *
 * 重构目标：
 * 1. 引入 ../sandbox/env_proxy.js 中的 protectToString 与 watchEnv（淘汰旧仓库里的 eval 代理拼接）；
 * 2. 将 a1 / web_session 等动态 Cookie 作为 payload 参数从 Python 侧传入，消灭硬编码死 Cookie；
 * 3. 返回 { 'x-s': ..., 'x-t': ... } 供 Python 端 curl_cffi 客户端发起高并发采集。
 */

'use strict';

const { protectToString, watchEnv } = require('../sandbox/env_proxy');

async function sign(payload = {}) {
  void protectToString;
  void watchEnv;
  void payload;
  // TODO(W1): 迁移旧仓库 小红薯/env.js + loadmnsv2.js 至独立上下文并返回 X-s / X-t
  throw new Error(
    'xhs_mnsv2 尚未填入补环境代码！请按 W1 计划将旧仓库 小红薯 模块迁移至此文件。'
  );
}

module.exports = {
  description: '[W1 待迁移] 小红书 x-s/x-t 补环境常驻服务模块',
  sign,
};
