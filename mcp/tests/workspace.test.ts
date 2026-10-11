import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { insideWorkspace, listWorkspaces, resolveWorkspace, syncProblem } from "../src/workspace.ts";

const base = mkdtempSync(join(tmpdir(), "ovs-ws-"));
mkdirSync(join(base, "demo", "llmwiki"), { recursive: true });
writeFileSync(join(base, "demo", "llmwiki", "index.md"), "# demo\n");
mkdirSync(join(base, "Bad_Name"));

test("workspace names: lowercase, digits, dashes only", () => {
  assert.equal(resolveWorkspace("demo", base), join(base, "demo"));
  assert.throws(() => resolveWorkspace("Bad_Name", base), /invalid workspace name/);
  assert.throws(() => resolveWorkspace("../etc", base), /invalid workspace name/);
  assert.throws(() => resolveWorkspace("missing", base), /no workspace missing/);
  assert.deepEqual(listWorkspaces(base).map((w) => w.name), ["demo"]);
});

test("paths escaping the workspace are refused, including through symlinks", () => {
  const ws = join(base, "demo");
  assert.equal(insideWorkspace(ws, "llmwiki/index.md"), true);
  assert.equal(insideWorkspace(ws, "new/dir/not/yet/there.md"), true);
  assert.equal(insideWorkspace(ws, "../Bad_Name"), false);
  assert.equal(insideWorkspace(ws, "/etc/passwd"), false);
  symlinkSync(tmpdir(), join(ws, "escape"));
  assert.equal(insideWorkspace(ws, "escape/x"), false);
});

test("workspace_sync allow-list mirrors hostops stack_sync", () => {
  assert.equal(syncProblem("https://github.com/Rheinmir/setup", "orca"), null);
  assert.match(syncProblem("https://github.com/evil/repo", "main")!, /not in OVERSTACK_GIT_ALLOW/);
  assert.match(syncProblem("git@github.com:Rheinmir/setup.git", "main")!, /invalid repo/);
  assert.match(syncProblem("https://github.com/Rheinmir/setup", "../x")!, /invalid ref/);
  assert.equal(syncProblem("https://example.com/a/b", "main", ["https://example.com/"]), null);
});
