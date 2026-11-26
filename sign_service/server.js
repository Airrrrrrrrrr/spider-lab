/**
 * Spider Lab 常驻高性能签名网关 (Fastify)
 *
 * 启动方式：npm --prefix sign_service start
 * 默认地址：http://127.0.0.1:3001
 */

'use strict';

const { performance } = require('node:perf_hooks');
const Fastify = require('fastify');

const providers = {
  demo_hmac: require('./providers/demo_hmac'),
  qq_music_webpack: require('./providers/qq_music_webpack'),
  xhs_mnsv2: require('./providers/xhs_mnsv2'),
};

function buildServer(opts = { logger: false }) {
  const app = Fastify(opts);

  app.get('/health', async () => ({
    status: 'ok',
    node_version: process.version,
    pid: process.pid,
    uptime_sec: Math.round(process.uptime()),
    providers: Object.keys(providers),
  }));

  app.get('/providers', async () =>
    Object.entries(providers).map(([name, mod]) => ({
      name,
      description: mod.description || '',
    }))
  );

  app.post('/sign/:provider', async (request, reply) => {
    const { provider } = request.params;
    const target = providers[provider];

    if (!target || typeof target.sign !== 'function') {
      return reply.code(404).send({
        error: `未知的签名 provider: ${provider}`,
        available: Object.keys(providers),
      });
    }

    const payload = (request.body && request.body.payload) || {};
    const t0 = performance.now();

    try {
      const result = await target.sign(payload);
      const costMs = Number((performance.now() - t0).toFixed(3));
      return {
        provider,
        cost_ms: costMs,
        result,
      };
    } catch (err) {
      return reply.code(500).send({
        provider,
        error: err && err.message ? err.message : String(err),
      });
    }
  });

  return app;
}

if (require.main === module) {
  const host = process.env.SIGN_HOST || '127.0.0.1';
  const port = Number(process.env.SIGN_PORT || 3001);
  const enableLog = process.env.SIGN_LOG === '1';
  const server = buildServer({ logger: enableLog });

  server.listen({ host, port }).then(() => {
    console.log(`[sign_service] Fastify listening on http://${host}:${port} (Node ${process.version})`);
  }).catch((err) => {
    console.error(err);
    process.exit(1);
  });
}

module.exports = { buildServer };
