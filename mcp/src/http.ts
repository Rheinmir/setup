/**
 * Streamable HTTP: `ALL /mcp` sau bearer token (stateless, một phiên mỗi request — cùng khuôn với devops-agent),
 * `GET /healthz` không cần token, `GET /` trả thông tin phiên bản. Token so sánh thời gian cố định.
 */
import { WebStandardStreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js";
import { timingSafeEqual } from "node:crypto";
import { Hono } from "hono";
import { buildServer, toolModeFromEnv, VERSION } from "./server.ts";
import type { ServerOptions } from "./server.ts";
import { loadCatalog } from "./catalog.ts";
import { workspacesDir } from "./workspace.ts";

export function sameToken(a: string | undefined, b: string): boolean {
  if (!a || a.length !== b.length) return false;
  return timingSafeEqual(Buffer.from(a), Buffer.from(b));
}

export interface HttpOptions extends ServerOptions { token: string; tokenSource?: "env" | "file" | "generated" }

export function createApp(opts: HttpOptions): Hono {
  if (!opts.token || opts.token.length < 16) throw new Error("OVERSTACK_MCP_TOKEN must be set (≥ 16 chars) — generate one: openssl rand -hex 32");
  const catalog = opts.catalog ?? loadCatalog();
  const mode = opts.mode ?? toolModeFromEnv();
  const app = new Hono();
  // tokenSource nói cho operator biết token nằm ở đâu (env hay file trong volume) — không bao giờ lộ giá trị
  app.get("/healthz", (c) => c.json({ ok: true, name: "overstack-mcp", version: VERSION, skills: catalog.skills.length, rules: catalog.rules.length, tools: catalog.tools.length, mode, tokenSource: opts.tokenSource ?? "env" }));
  app.use("*", async (c, next) => {
    const bearer = c.req.header("authorization")?.replace(/^Bearer\s+/i, "");
    if (!sameToken(bearer, opts.token)) return c.json({ error: "unauthorized" }, 401);
    return next();
  });
  app.get("/", (c) => c.json({ name: "overstack-mcp", version: VERSION, mcp: "/mcp", workspacesDir: workspacesDir(), mode }));
  app.all("/mcp", async (c) => {
    const transport = new WebStandardStreamableHTTPServerTransport({ sessionIdGenerator: undefined, enableJsonResponse: true });
    const server = buildServer({ ...opts, catalog, mode });
    await server.connect(transport);
    try { return await transport.handleRequest(c.req.raw); } finally { c.req.raw.signal.addEventListener("abort", () => void server.close()); }
  });
  return app;
}
