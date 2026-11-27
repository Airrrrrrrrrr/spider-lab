/**
 * 【W1 周末实战槽位 1】：迁移旧仓库 Airrrrrrrrrr/spider/Scrape/spa/js/spa6_webpack.js
 *
 * 为什么选 Scrape spa6 替代空占位的 QQMusic？
 * 1. 靶场 https://spa6.scrape.center/ 永久在线、免登录、无 Cookie 过期干扰；
 * 2. 非常适合跑通完整的「Node Fastify Webpack 签名 -> Python curl_cffi 异步抓取 -> Pydantic CrawlRecord 清洗」全链路！
 *
 * 重构目标：
 * 1. 迁移旧仓库 Scrape/spa/js/spa6_webpack.js 的 Webpack 加载器与 token 生成入口；
 * 2. 接收 Python 端传入的 { path: "/api/movie", offset: 0 }，计算并返回动态加密参数 { token: "..." }；
 * 3. 完成后写一张「三分钟唤醒卡片」沉淀到对应 case 目录。
 */

'use strict';

async function sign(payload = {}) {
  void payload;
  // TODO(W1): 将旧仓库 Scrape/spa/js/spa6_webpack.js 的加载器与 token 生成逻辑迁移至此
  throw new Error(
    'spa6_webpack 尚未填入算法逻辑！请按 W1 计划将旧仓库 Scrape/spa/js/spa6_webpack.js 迁移至此模块。'
  );
}

module.exports = {
  description: '[W1 待迁移] Scrape SPA6 Webpack 动态 token 签名模块（永久在线全链路闭环）',
  sign,
};
