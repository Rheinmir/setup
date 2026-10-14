import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { loadCatalog } from "../src/catalog.ts";
import { buildServer } from "../src/server.ts";
import { createApp } from "../src/http.ts";
import { NodeSource } from "../src/source-node.ts";

const cat = loadCatalog();
const base = mkdtempSync(join(tmpdir(), "ovs-srv-"));
process.env.WORKSPACES_DIR = base; // workspace.ts đọc env lúc gọi, nên đặt ở đây là đủ
mkdirSync(join(base, "demo", "llmwiki", "wiki"), { recursive: true });
writeFileSync(join(base, "demo", "llmwiki", "wiki", "index.md"), "# i\n");

async function connect(mode: "read" | "core" | "all") {
  const [ct, st] = InMemoryTransport.createLinkedPair();
  const server = buildServer({ catalog: cat, mode });
  const client = new Client({ name: "test", version: "0" });
  await Promise.all([server.connect(st), client.connect(ct)]);
  return { client, server };
}

test("core mode: every skill is a prompt, resources resolve, 11 tools", async () => {
  const { client, server } = await connect("core");
  const prompts = await client.listPrompts();
  assert.ok(prompts.prompts.length >= 100, `prompts ${prompts.prompts.length}`);
  assert.equal(prompts.prompts.length, cat.skills.length);
  const tools = await client.listTools();
  assert.deepEqual(tools.tools.map((t) => t.name).sort(), ["orca_graph", "rule_check", "rules_list", "skill_find", "skill_get", "skills_list", "tool_help", "tool_run", "tools_list", "workspace_list", "workspace_sync"]);
  const catalog = await client.readResource({ uri: "overstack://catalog" });
  const parsed = JSON.parse((catalog.contents[0] as { text: string }).text) as { skills: unknown[]; rules: unknown[]; tools: unknown[] };
  assert.equal(parsed.skills.length, cat.skills.length);
  const skill = await client.readResource({ uri: "overstack://skill/plan" });
  assert.match((skill.contents[0] as { text: string }).text, /^---\nname: plan/);
  const templates = await client.listResourceTemplates();
  assert.deepEqual(templates.resourceTemplates.map((t) => t.uriTemplate).sort(), ["overstack://rule/{id}", "overstack://skill/{name}", "overstack://tool/{name}"]);
  const prompt = await client.getPrompt({ name: "md-to-html", arguments: { task: "render README" } });
  assert.match((prompt.messages[0]!.content as { text: string }).text, /Task: render README/);
  await client.close(); await server.close();
});

test("read mode (hostname công khai): chỉ 7 tool đọc, không tool_run/rule_check/workspace_sync/orca_graph", async () => {
  const { client, server } = await connect("read");
  const tools = await client.listTools();
  assert.deepEqual(tools.tools.map((t) => t.name).sort(), ["rules_list", "skill_find", "skill_get", "skills_list", "tool_help", "tools_list", "workspace_list"]);
  const g = await client.callTool({ name: "skill_get", arguments: { name: "lint" } });
  assert.match((g.content as Array<{ text: string }>)[0]!.text, /name: lint/);
  await client.close(); await server.close();
});

test("skill_find ranks md-to-html for a markdown→html task; skill_get and tool_help answer by name", async () => {
  const { client, server } = await connect("core");
  const r = await client.callTool({ name: "skill_find", arguments: { query: "render markdown to html", k: 5 } });
  const hits = JSON.parse((r.content as Array<{ text: string }>)[0]!.text) as Array<{ name: string }>;
  assert.ok(hits.slice(0, 5).some((h) => h.name === "md-to-html"), JSON.stringify(hits));
  const g = await client.callTool({ name: "skill_get", arguments: { name: "/plan" } });
  assert.match((g.content as Array<{ text: string }>)[0]!.text, /name: plan/);
  const h = await client.callTool({ name: "tool_help", arguments: { name: "wiki-health.py" } });
  const help = JSON.parse((h.content as Array<{ text: string }>)[0]!.text) as { options: Array<{ flags: string[] }> };
  assert.ok(help.options.some((o) => o.flags.includes("--wiki-dir")));
  const missing = await client.callTool({ name: "skill_get", arguments: { name: "no-such-skill" } });
  assert.equal(missing.isError, true);
  await client.close(); await server.close();
});

test("tool_run refuses an unknown tool, a bad workspace and an escaping path; runs wiki-health in a workspace", async () => {
  const { client, server } = await connect("core");
  const unknown = await client.callTool({ name: "tool_run", arguments: { name: "rm", args: [], workspace: "demo" } });
  assert.equal(unknown.isError, true);
  const badWs = await client.callTool({ name: "tool_run", arguments: { name: "wiki-health", args: [], workspace: "nope" } });
  assert.equal(badWs.isError, true);
  const escape = await client.callTool({ name: "tool_run", arguments: { name: "wiki-health", args: ["--wiki-dir", "../../etc"], workspace: "demo" } });
  assert.equal(escape.isError, true);
  const ok = await client.callTool({ name: "tool_run", arguments: { name: "wiki-health", args: ["--wiki-dir", "llmwiki/wiki"], workspace: "demo" } });
  const res = JSON.parse((ok.content as Array<{ text: string }>)[0]!.text) as { rc: number; argv: string[] };
  assert.equal(res.rc, 0);
  assert.equal(res.argv[0], "harness/scripts/wiki-health.py");
  const rule = await client.callTool({ name: "rule_check", arguments: { rule: "R9", workspace: "demo", files: ["llmwiki/wiki/index.md"] } });
  const rr = JSON.parse((rule.content as Array<{ text: string }>)[0]!.text) as { pass: boolean; rule: string };
  assert.equal(rr.rule, "R9");
  assert.equal(typeof rr.pass, "boolean");
  const noValidator = await client.callTool({ name: "rule_check", arguments: { rule: "R4", workspace: "demo", files: ["x"] } });
  assert.equal(noValidator.isError, true);
  await client.close(); await server.close();
});

test("all mode: one tool per catalog script on top of core", async () => {
  const { client, server } = await connect("all");
  const tools = await client.listTools();
  assert.ok(tools.tools.length >= cat.tools.length + 11, `tools ${tools.tools.length}`);
  assert.ok(tools.tools.some((t) => t.name === "wiki-health"));
  await client.close(); await server.close();
});

test("http: /healthz open, everything else 401 without the bearer, /mcp initializes with it", async () => {
  const token = "t".repeat(32);
  const app = createApp({ token, catalog: cat, mode: "core", source: new NodeSource(undefined, cat), build: (o) => buildServer(o) });
  const health = await app.request("/healthz");
  assert.equal(health.status, 200);
  assert.equal(((await health.json()) as { ok: boolean }).ok, true);
  assert.equal((await app.request("/")).status, 401);
  assert.equal((await app.request("/mcp", { method: "POST", body: "{}" })).status, 401);
  const init = await app.request("/mcp", { method: "POST", headers: { authorization: `Bearer ${token}`, "content-type": "application/json", accept: "application/json, text/event-stream" },
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "initialize", params: { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "t", version: "0" } } }) });
  const raw = await init.text();
  assert.equal(init.status, 200, raw);
  const body = JSON.parse(raw) as { result: { serverInfo: { name: string } } };
  assert.equal(body.result.serverInfo.name, "overstack");
  assert.throws(() => createApp({ token: "short", catalog: cat, source: new NodeSource(undefined, cat) }), /OVERSTACK_MCP_TOKEN/);
});
