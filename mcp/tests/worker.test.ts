/** Lõi đọc trên nguồn assets (Workers): cùng catalog, cùng skill body, skill_find qua chỉ mục tính sẵn; token so thời gian cố định. */
import assert from "node:assert/strict";
import { existsSync, mkdtempSync, readFileSync, readdirSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { execFileSync } from "node:child_process";
import { test } from "node:test";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { loadCatalog, OVERSTACK_ROOT, skillsRootDir } from "../src/catalog.ts";
import { buildCoreServer } from "../src/core.ts";
import { createApp } from "../src/http.ts";
import { AssetsSource, sameToken, skillRel } from "../src/source.ts";
import { NodeSource } from "../src/source-node.ts";

const cat = loadCatalog();
const haveSkills = existsSync(skillsRootDir(cat));

/** Binding ASSETS giả: phục vụ đúng cây thư mục do build-worker-assets.mjs gom (đường dẫn URL → file). */
function fakeAssets(dir: string) {
  return { async fetch(input: URL | string | Request) {
    const u = new URL(typeof input === "string" ? input : input instanceof URL ? input.href : input.url);
    const p = join(dir, decodeURIComponent(u.pathname));
    return existsSync(p) && statSync(p).isFile() ? new Response(readFileSync(p)) : new Response("not found", { status: 404 });
  } };
}

function walk(d: string): string[] { return readdirSync(d).flatMap((n) => (statSync(join(d, n)).isDirectory() ? walk(join(d, n)) : [join(d, n)])); }

test("sameToken: cùng độ dài khác nội dung → false; thiếu → false; đúng → true", () => {
  assert.equal(sameToken("a".repeat(32), "a".repeat(32)), true);
  assert.equal(sameToken("a".repeat(31) + "b", "a".repeat(32)), false);
  assert.equal(sameToken(undefined, "a".repeat(32)), false);
  assert.equal(sameToken("short", "a".repeat(32)), false);
});

test("build-worker-assets: mọi skill của catalog có mặt, chỉ mục tìm kiếm đủ 106 đầu, catalog không lộ đường máy sinh", { skip: !haveSkills && "không có skills checkout" }, () => {
  const out = mkdtempSync(join(tmpdir(), "ovs-assets-"));
  execFileSync(process.execPath, [join(OVERSTACK_ROOT, "mcp", "scripts", "build-worker-assets.mjs"), "--out", out], { stdio: "pipe" });
  for (const s of cat.skills) assert.ok(existsSync(join(out, skillRel(s))), `thiếu ${skillRel(s)}`);
  const idx = JSON.parse(readFileSync(join(out, "skills-index.json"), "utf8")) as Array<{ name: string; head: string }>;
  assert.equal(idx.length, cat.skills.length);
  assert.ok(idx.every((h) => h.head.length > 0 && h.head.length <= 4000));
  const pub = JSON.parse(readFileSync(join(out, "catalog.json"), "utf8")) as { skillsRoot?: string; skills: unknown[] };
  assert.equal(pub.skillsRoot, undefined);
  assert.equal(pub.skills.length, cat.skills.length);
  assert.ok(walk(out).length >= cat.skills.length + 3);
});

test("AssetsSource ≡ NodeSource: cùng skill body, cùng top-1 skill_find, resource policy/rule đọc được từ assets", { skip: !haveSkills && "không có skills checkout" }, async () => {
  const out = mkdtempSync(join(tmpdir(), "ovs-assets-"));
  execFileSync(process.execPath, [join(OVERSTACK_ROOT, "mcp", "scripts", "build-worker-assets.mjs"), "--out", out], { stdio: "pipe" });
  const assets = new AssetsSource(fakeAssets(out), "https://overstack-mcp.example.workers.dev");
  const node = new NodeSource(OVERSTACK_ROOT, cat);
  const s = cat.skills.find((x) => x.name === "md-to-html") ?? cat.skills[0]!;
  assert.equal(await assets.skillBody(s), await node.skillBody(s));
  assert.equal(await assets.harnessVersion(), await node.harnessVersion());
  assert.equal((await assets.skillHeads()).length, (await node.skillHeads()).length);

  const [ct, st] = InMemoryTransport.createLinkedPair();
  const server = buildCoreServer({ catalog: cat, mode: "read", source: assets });
  const client = new Client({ name: "t", version: "0" });
  await Promise.all([server.connect(st), client.connect(ct)]);
  const tools = (await client.listTools()).tools.map((t) => t.name).sort();
  assert.deepEqual(tools, ["rules_list", "skill_find", "skill_get", "skills_list", "tool_help", "tools_list"]);
  const find = await client.callTool({ name: "skill_find", arguments: { query: "render markdown file to standalone html with mermaid", k: 3 } });
  const hits = JSON.parse((find.content as Array<{ text: string }>)[0]!.text) as Array<{ name: string }>;
  assert.equal(hits[0]?.name, "md-to-html", JSON.stringify(hits));
  const policy = await client.readResource({ uri: "overstack://policy" });
  const asText = (c: { text?: string } | { blob?: string }) => ("text" in c ? String(c.text) : "");
  assert.match(asText(policy.contents[0]!), /rules|R1/);
  const rule = cat.rules.find((r) => r.validatorPath)!;
  const rr = await client.readResource({ uri: `overstack://rule/${rule.id}` });
  assert.ok(JSON.parse(asText(rr.contents[0]!)).validatorDoc, "validatorDoc từ .py trong assets");
  await client.close(); await server.close();
});

test("đọc công khai (Worker không secret): /mcp không bearer vẫn 200 ở mode read; mode core bỏ qua anonymous và vẫn 401", async () => {
  const node = new NodeSource(OVERSTACK_ROOT, cat);
  const open = createApp({ token: "", catalog: cat, mode: "read", source: node, anonymous: true });
  const h = (await (await open.request("/healthz")).json()) as { tokenSource: string; anonymous: boolean; mode: string };
  assert.equal(h.tokenSource, "none"); assert.equal(h.anonymous, true); assert.equal(h.mode, "read");
  const init = await open.request("/mcp", { method: "POST", headers: { "content-type": "application/json", accept: "application/json, text/event-stream" },
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "tools/list" }) });
  assert.equal(init.status, 200);
  const names = ((await init.json()) as { result: { tools: Array<{ name: string }> } }).result.tools.map((t) => t.name).sort();
  assert.deepEqual(names, ["rules_list", "skill_find", "skill_get", "skills_list", "tool_help", "tools_list"]);
  assert.throws(() => createApp({ token: "", catalog: cat, mode: "core", source: node, anonymous: true }), /OVERSTACK_MCP_TOKEN/, "core không bao giờ công khai");
  const guarded = createApp({ token: "t".repeat(32), catalog: cat, mode: "core", source: node, anonymous: true });
  assert.equal((await guarded.request("/mcp", { method: "POST", body: "{}" })).status, 401);
});
