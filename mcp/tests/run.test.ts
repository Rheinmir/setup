import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { findTool, loadCatalog } from "../src/catalog.ts";
import { argProblem, runTool, toolEnv, validateArgs } from "../src/run.ts";

const cat = loadCatalog();
const ws = mkdtempSync(join(tmpdir(), "ovs-run-"));
mkdirSync(join(ws, "llmwiki", "wiki", "concepts"), { recursive: true });
writeFileSync(join(ws, "llmwiki", "wiki", "index.md"), "# index\n\n- [[concepts/a]]\n");
writeFileSync(join(ws, "llmwiki", "wiki", "concepts", "a.md"), "---\ntype: concept\n---\n# a\n\n## Origin\n- test\n");

test("arguments: one line, bounded, paths inside the workspace or /tmp", () => {
  assert.equal(argProblem("--wiki-dir", ws), null);
  assert.equal(argProblem("llmwiki/wiki", ws), null);
  assert.equal(argProblem("--out=llmwiki/out.json", ws), null);
  assert.equal(argProblem("/tmp/x.json", ws), null);
  assert.equal(argProblem("https://github.com/Rheinmir/setup", ws), null);
  assert.match(argProblem("a\nb", ws)!, /control character/);
  assert.match(argProblem("../other", ws)!, /\.\./);
  assert.match(argProblem("/etc/passwd", ws)!, /outside the workspace/);
  assert.match(argProblem("--out=/etc/x", ws)!, /outside the workspace/);
  assert.match(argProblem("~/x", ws)!, /~/);
  assert.match(argProblem("x".repeat(2001), ws)!, /longer/);
  assert.throws(() => validateArgs(new Array(65).fill("a"), ws), /more than 64/);
  assert.throws(() => validateArgs("not-array", ws), /array/);
});

test("tool env carries no server secrets", () => {
  process.env.OVERSTACK_MCP_TOKEN = "secret-token-should-not-leak";
  const env = toolEnv(ws);
  assert.equal(env.OVERSTACK_MCP_TOKEN, undefined);
  assert.equal(env.OVERSTACK_WORKSPACE, ws);
  assert.ok(env.OVERSTACK_ROOT);
});

test("runs a catalog tool inside the workspace and returns rc/stdout/stderr", async () => {
  const tool = findTool(cat, "wiki-health")!;
  assert.ok(tool, "wiki-health in catalog");
  const r = await runTool({ tool, args: ["--wiki-dir", "llmwiki/wiki"], workspace: "x" }, ws);
  assert.equal(r.rc, 0, r.stderr);
  assert.equal(r.cwd, ws);
  assert.ok(r.stdout.includes("{"), "JSON report on stdout");
  assert.equal(r.timedOut, false);
});

test("a validator reads argv files and exits 2 on a violation", async () => {
  const tool = findTool(cat, "okf_frontmatter")!;
  writeFileSync(join(ws, "llmwiki", "wiki", "concepts", "bad.md"), "# no frontmatter\n");
  const bad = await runTool({ tool, args: ["llmwiki/wiki/concepts/bad.md"], workspace: "x" }, ws);
  assert.equal(bad.rc, 2);
  const good = await runTool({ tool, args: ["llmwiki/wiki/concepts/a.md"], workspace: "x" }, ws);
  assert.equal(good.rc, 0, good.stderr);
});

test("timeouts kill the child and say so", async () => {
  const tool = findTool(cat, "wiki-health")!;
  const r = await runTool({ tool: { ...tool, runner: "python3", path: "mcp/tests/fixtures/sleep.py" }, args: [], workspace: "x", timeoutMs: 1000 }, ws);
  assert.equal(r.timedOut, true);
  assert.notEqual(r.rc, 0);
});
