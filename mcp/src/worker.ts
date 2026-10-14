/**
 * Entry Cloudflare Workers (mode read, không chạy gì): skill/rule/tool đọc từ static assets do `npm run worker:assets` gom
 * (catalog.json, skills/<path>/SKILL.md, skills-index.json, harness/version.json, harness/policy.yaml, fdk/CAPABILITIES.md,
 * validator .py). Mặc định ĐỌC CÔNG KHAI (nội dung là repo public; connect-mcp.sh của mọi máy dev trỏ về đây không cần token).
 * Đặt secret OVERSTACK_MCP_TOKEN (`wrangler secret put`) thì /mcp đòi bearer; /healthz luôn mở.
 * Cấu hình: worker/wrangler.jsonc. Chạy trọn trên Workers Free: không đĩa, không tiến trình con, một asset fetch mỗi skill đọc.
 */
import type { Hono } from "hono";
import { loadCatalogFromText } from "./catalog.ts";
import { buildCoreServer } from "./core.ts";
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
  const token = env.OVERSTACK_MCP_TOKEN ?? "";
  if (token && token.length < 16) throw new Error("OVERSTACK_MCP_TOKEN secret phải ≥ 16 ký tự (hoặc xoá để đọc công khai): npx wrangler secret delete OVERSTACK_MCP_TOKEN -c worker/wrangler.jsonc");
  return createApp({ token, tokenSource: "env", catalog, mode: "read", source, harness: await source.harnessVersion(), build: buildCoreServer, anonymous: !token });
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);
    app ??= init(env, url.origin).catch((e) => { app = undefined; throw e; });
    return (await app).fetch(req, env);
  },
};
