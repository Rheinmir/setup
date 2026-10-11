import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { resolveToken, TOKEN_FILE } from "../src/token.ts";

test("env token wins; a short one is refused", () => {
  const dir = mkdtempSync(join(tmpdir(), "ovs-tok-"));
  assert.deepEqual(resolveToken(dir, { OVERSTACK_MCP_TOKEN: "x".repeat(32) }), { token: "x".repeat(32), source: "env" });
  assert.throws(() => resolveToken(dir, { OVERSTACK_MCP_TOKEN: "short" }), /≥ 16/);
});

test("without env: generate once into the workspaces volume (0600), then reuse the file", () => {
  const dir = mkdtempSync(join(tmpdir(), "ovs-tok-"));
  const first = resolveToken(join(dir, "ws"), {});
  assert.equal(first.source, "generated");
  assert.equal(first.token.length, 48);
  assert.equal(first.path, join(dir, "ws", TOKEN_FILE));
  assert.equal(statSync(first.path!).mode & 0o777, 0o600);
  assert.equal(readFileSync(first.path!, "utf8").trim(), first.token);
  const again = resolveToken(join(dir, "ws"), {});
  assert.deepEqual(again, { token: first.token, source: "file", path: first.path });
});
