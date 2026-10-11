/**
 * Smoke client cho overstack-mcp — chạy như một MCP client thật.
 *   npm run mcp:check -- stdio        spawn src/stdio.ts, nói chuyện qua stdio
 *   npm run mcp:check -- http         spawn src/main.ts trên cổng ngẫu nhiên, nói chuyện qua Streamable HTTP + bearer
 *   npm run mcp:check -- both
 *   MCP_URL=http://host:8791/mcp OVERSTACK_MCP_TOKEN=… npm run mcp:check -- remote   # server đã chạy sẵn (container, k8s2)
 * Kiểm: initialize · tools/list ≥ 11 · prompts/list = số skill · resources/read overstack://catalog · skill_find top-5 có
 * md-to-html · tool_run wiki-health trong workspace $CHECK_WORKSPACE (mặc định: workspace đầu tiên có .llmwiki) trả rc số.
 * rc 0 khi mọi bước qua; in từng bước để đọc trong CI.
 */
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { spawn, type ChildProcess } from "node:child_process";
import { randomBytes } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const MCP_DIR = join(dirname(fileURLToPath(import.meta.url)), "..");
const mode = process.argv[2] ?? "both";
const wsEnv = process.env.WORKSPACES_DIR;
let failures = 0;
const step = (name: string, ok: boolean, detail = "") => { failures += ok ? 0 : 1; console.log(`${ok ? "✔" : "✖"} ${name}${detail ? `  ${detail}` : ""}`); };
// callTool trả union (content[] | toolResult) — chỉ đọc content text
const textOf = (r: unknown) => (((r as { content?: Array<{ type: string; text?: string }> }).content) ?? []).filter((c) => c.type === "text").map((c) => c.text ?? "").join("\n");

async function exercise(client: Client, label: string) {
  const tools = await client.listTools();
  step(`${label} tools/list`, tools.tools.length >= 11, `${tools.tools.length} tools`);
  const prompts = await client.listPrompts();
  step(`${label} prompts/list`, prompts.prompts.length >= 100, `${prompts.prompts.length} prompts`);
  const cat = await client.readResource({ uri: "overstack://catalog" });
  const parsed = JSON.parse((cat.contents[0] as { text: string }).text) as { skills: unknown[]; rules: unknown[]; tools: unknown[] };
  step(`${label} resources/read overstack://catalog`, parsed.skills.length >= 100 && parsed.rules.length >= 22, `${parsed.skills.length} skills · ${parsed.rules.length} rules · ${parsed.tools.length} tools`);
  const find = await client.callTool({ name: "skill_find", arguments: { query: "render markdown to html", k: 5 } });
  const hits = JSON.parse(textOf(find)) as Array<{ name: string; score: number }>;
  step(`${label} skill_find`, hits.some((h) => h.name === "md-to-html"), hits.map((h) => `${h.name}:${h.score}`).join(" "));
  const wsList = await client.callTool({ name: "workspace_list", arguments: {} });
  const workspaces = JSON.parse(textOf(wsList)) as Array<{ name: string; hasWiki: boolean }>;
  const ws = process.env.CHECK_WORKSPACE ?? workspaces.find((w) => w.hasWiki)?.name ?? workspaces[0]?.name;
  step(`${label} workspace_list`, workspaces.length > 0, `${workspaces.length} workspaces${ws ? `, using ${ws}` : ""}`);
  if (ws) {
    const wikiDir = (JSON.parse(textOf(wsList)) as Array<{ name: string; hasWiki: boolean }>).find((w) => w.name === ws)?.hasWiki ? ".llmwiki/wiki" : "llmwiki/wiki";
    const run = await client.callTool({ name: "tool_run", arguments: { name: "wiki-health", args: ["--wiki-dir", wikiDir], workspace: ws } });
    const text = textOf(run);
    let rc: unknown = null; try { rc = (JSON.parse(text) as { rc: unknown }).rc; } catch { rc = null; }
    step(`${label} tool_run wiki-health`, !run.isError && Number.isInteger(rc), `rc=${String(rc)}${run.isError ? ` ${text.slice(0, 200)}` : ""}`);
    const rule = await client.callTool({ name: "rule_check", arguments: { rule: "R9", workspace: ws, files: [`${wikiDir}/index.md`] } });
    const rt = textOf(rule);
    step(`${label} rule_check R9`, !rule.isError && /"pass":\s*(true|false)/.test(rt), rt.match(/"pass":\s*\w+/)?.[0] ?? rt.slice(0, 120));
  } else {
    step(`${label} tool_run (skipped: no workspace under WORKSPACES_DIR)`, false, wsEnv ?? "(unset)");
  }
}

async function stdio() {
  const transport = new StdioClientTransport({ command: "node", args: ["--import", "tsx", join(MCP_DIR, "src", "stdio.ts")], env: { ...process.env as Record<string, string> }, stderr: "pipe" });
  const client = new Client({ name: "mcp-check", version: "0" });
  await client.connect(transport);
  step("stdio initialize", client.getServerVersion()?.name === "overstack", JSON.stringify(client.getServerVersion()));
  await exercise(client, "stdio");
  await client.close();
}

async function waitHealthy(url: string, ms = 20_000) {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) {
    try { const r = await fetch(url); if (r.ok) return (await r.json()) as Record<string, unknown>; } catch { /* not up yet */ }
    await new Promise((r) => setTimeout(r, 300));
  }
  throw new Error(`server not healthy at ${url} after ${ms} ms`);
}

async function httpAgainst(base: string, token: string, label: string) {
  const health = await waitHealthy(`${base}/healthz`);
  step(`${label} /healthz`, health.ok === true, JSON.stringify(health));
  const noToken = await fetch(`${base}/mcp`, { method: "POST", headers: { "content-type": "application/json", accept: "application/json, text/event-stream" }, body: "{}" });
  step(`${label} /mcp without token → 401`, noToken.status === 401, String(noToken.status));
  const transport = new StreamableHTTPClientTransport(new URL(`${base}/mcp`), { requestInit: { headers: { authorization: `Bearer ${token}` } } });
  const client = new Client({ name: "mcp-check", version: "0" });
  await client.connect(transport);
  step(`${label} initialize`, client.getServerVersion()?.name === "overstack", JSON.stringify(client.getServerVersion()));
  await exercise(client, label);
  await client.close();
}

async function http() {
  const port = 20000 + Math.floor(Math.random() * 20000);
  const token = randomBytes(24).toString("hex");
  const child: ChildProcess = spawn("node", ["--import", "tsx", join(MCP_DIR, "src", "main.ts")], { env: { ...process.env, PORT: String(port), BIND: "127.0.0.1", OVERSTACK_MCP_TOKEN: token }, stdio: ["ignore", "pipe", "pipe"] });
  child.stderr?.on("data", (d: Buffer) => process.stderr.write(`[server] ${d}`));
  try { await httpAgainst(`http://127.0.0.1:${port}`, token, "http"); } finally { child.kill("SIGTERM"); }
}

async function remote() {
  const url = process.env.MCP_URL;
  const token = process.env.OVERSTACK_MCP_TOKEN;
  if (!url || !token) throw new Error("remote mode needs MCP_URL (…/mcp) and OVERSTACK_MCP_TOKEN");
  await httpAgainst(url.replace(/\/mcp\/?$/, ""), token, "remote");
}

try {
  if (mode === "stdio" || mode === "both") await stdio();
  if (mode === "http" || mode === "both") await http();
  if (mode === "remote") await remote();
} catch (e) {
  step(`fatal (${mode})`, false, (e as Error).message);
}
console.log(failures === 0 ? "\nmcp-check: OK" : `\nmcp-check: ${failures} step(s) failed`);
process.exit(failures === 0 ? 0 : 1);
