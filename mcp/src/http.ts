/**
 * Streamable HTTP: `ALL /mcp` sau bearer token (stateless, một phiên mỗi request — cùng khuôn với devops-agent),
 * `GET /healthz` không cần token, `GET /` trả thông tin phiên bản. Token so sánh thời gian cố định.
 * Không import gì của Node: file này đi vào bundle Worker. Node (main.ts) truyền NodeSource + buildServer; Worker truyền
 * AssetsSource + buildCoreServer.
 */
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { WebStandardStreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js";
import { Hono } from "hono";
import type { Catalog } from "./catalog.ts";
import { buildCoreServer, toolModeFromEnv, VERSION } from "./core.ts";
import type { CoreOptions, ToolMode } from "./core.ts";
import { sameToken } from "./source.ts";
import type { Source } from "./source.ts";

export { sameToken };

export interface HttpOptions {
  token: string; tokenSource?: "env" | "file" | "generated";
  catalog: Catalog; mode?: ToolMode; source: Source;
  /** template_version của harness cho /healthz (Node: NodeSource.harnessVersion(); Worker: assets harness/version.json). */
  harness?: string | null;
  /** Dựng McpServer mỗi request: Node = buildServer (có tool chạy), Worker = buildCoreServer (chỉ đọc). Mặc định lõi đọc. */
  build?: (o: CoreOptions) => McpServer;
  workspacesDir?: string;
}

export function createApp(opts: HttpOptions): Hono {
  if (!opts.token || opts.token.length < 16) throw new Error("OVERSTACK_MCP_TOKEN must be set (≥ 16 chars) — generate one: openssl rand -hex 32");
  const { catalog, source } = opts;
  const mode = opts.mode ?? toolModeFromEnv();
  const build = opts.build ?? buildCoreServer;
  const app = new Hono();
  // tokenSource nói cho operator biết token nằm ở đâu (env hay file trong volume) — không bao giờ lộ giá trị
  // Nguồn phiên bản đồng nhất cho mọi dev (PLAN 141026 T5): harness = template_version, skills = version.json của Rheinmir/skills.
  app.get("/healthz", (c) => c.json({ ok: true, name: "overstack-mcp", version: VERSION, harness: opts.harness ?? null, template_version: opts.harness ?? null,
    skills: { count: catalog.skills.length, version: catalog.skillsVersion?.version ?? null, catalog_sha: catalog.skillsVersion?.catalog_sha ?? null },
    rules: catalog.rules.length, tools: catalog.tools.length, mode, tokenSource: opts.tokenSource ?? "env" }));
  app.use("*", async (c, next) => {
    const bearer = c.req.header("authorization")?.replace(/^Bearer\s+/i, "");
    if (!sameToken(bearer, opts.token)) return c.json({ error: "unauthorized" }, 401);
    return next();
  });
  app.get("/", (c) => c.json({ name: "overstack-mcp", version: VERSION, mcp: "/mcp", workspacesDir: opts.workspacesDir ?? null, mode }));
  app.all("/mcp", async (c) => {
    const transport = new WebStandardStreamableHTTPServerTransport({ sessionIdGenerator: undefined, enableJsonResponse: true });
    const server = build({ catalog, mode, source, workspacesHint: opts.workspacesDir });
    await server.connect(transport);
    try { return await transport.handleRequest(c.req.raw); } finally { c.req.raw.signal.addEventListener("abort", () => void server.close()); }
  });
  return app;
}
