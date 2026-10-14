/**
 * Entry Cloudflare Workers (mode read, không chạy gì): skill/rule/tool đọc từ static assets do `npm run worker:assets` gom
 * (catalog.json, skills/<path>/SKILL.md, skills-index.json, harness/version.json, harness/policy.yaml, fdk/CAPABILITIES.md,
 * validator .py). Token: secret OVERSTACK_MCP_TOKEN (`wrangler secret put`); /healthz không cần token.
 * Cấu hình: worker/wrangler.jsonc. Chạy trọn trên Workers Free: không đĩa, không tiến trình con, một asset fetch mỗi skill đọc.
 */
import type { Hono } from "hono";
import { loadCatalogFromText } from "./catalog.ts";
import { buildCoreServer, VERSION } from "./core.ts";
import { createApp } from "./http.ts";
import { AssetsSource } from "./source.ts";
import type { AssetFetcher } from "./source.ts";

interface Env { ASSETS: AssetFetcher; OVERSTACK_MCP_TOKEN?: string; OVERSTACK_TOOLS?: string }

let app: Promise<Hono> | undefined;

async function init(env: Env, origin: string): Promise<Hono> {
  const source = new AssetsSource(env.ASSETS, origin);
  const raw = await source.read("catalog.json");
  if (!raw) throw new Error("assets thiếu catalog.json — chạy: npm run worker:assets rồi deploy lại");
  const catalog = loadCatalogFromText(raw);
  return createApp({ token: env.OVERSTACK_MCP_TOKEN ?? "", tokenSource: "env", catalog, mode: "read", source, harness: await source.harnessVersion(), build: buildCoreServer });
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);
    if (!env.OVERSTACK_MCP_TOKEN || env.OVERSTACK_MCP_TOKEN.length < 16) {
      // Chưa đặt secret: /healthz vẫn trả lời (để biết Worker sống), mọi đường khác nói rõ phải làm gì.
      if (url.pathname === "/healthz") return Response.json({ ok: false, name: "overstack-mcp", version: VERSION, error: "OVERSTACK_MCP_TOKEN secret not set" });
      return Response.json({ error: "OVERSTACK_MCP_TOKEN secret not set (≥ 16 chars): npx wrangler secret put OVERSTACK_MCP_TOKEN -c worker/wrangler.jsonc" }, { status: 503 });
    }
    app ??= init(env, url.origin).catch((e) => { app = undefined; throw e; });
    return (await app).fetch(req, env);
  },
};
