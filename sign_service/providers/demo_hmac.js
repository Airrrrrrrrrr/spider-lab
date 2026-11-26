/**
 * 开箱即用的基准验证签名器：模拟接口请求动态签名 (HMAC-SHA256 + Nonce + Timestamp)
 * 用于第 1 周验证 Python 3.12 (asyncio) <-> Node.js (Fastify) 常驻进程毫秒级并发吞吐能力。
 */

'use strict';

const crypto = require('node:crypto');

const SECRET_SALT = 'spider-lab-w01-benchmark-salt';

/**
 * @param {Record<string, any>} payload
 */
async function sign(payload = {}) {
  const ts = Date.now();
  const nonce = crypto.randomBytes(6).toString('hex');
  const canonical = JSON.stringify(payload);
  const raw = `${ts}|${nonce}|${canonical}`;
  const signature = crypto.createHmac('sha256', SECRET_SALT).update(raw).digest('hex');

  return {
    'x-sign': signature,
    'x-ts': String(ts),
    'x-nonce': nonce,
  };
}

module.exports = {
  description: '基准验证签名器（验证 Python <-> Node 常驻服务高并发链路）',
  sign,
};
