// instructions = danh mục skill để Claude Code "biết" skill trên server như skill local (UAT 15/10: live 0/8 → mới 4/8 phiên gọi skill_get).
// Claude Code 2.1.300 cắt instructions ở 4096 ký tự (CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH) — khối phải lọt, đủ mọi skill model tự gọi.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { buildInstructions, skillHint, INSTRUCTIONS_BUDGET } from "../src/core.ts";

const cat = JSON.parse(readFileSync(new URL("../catalog.json", import.meta.url), "utf8"));
const invocable = cat.skills.filter((s: { modelInvocable: boolean }) => s.modelInvocable).map((s: { name: string }) => s.name);

test("instructions lọt giới hạn 4096 của Claude Code và liệt kê MỌI skill model tự gọi, mỗi skill một dòng có gợi ý", () => {
  const t = buildInstructions(cat, "read");
  assert.ok(INSTRUCTIONS_BUDGET < 4096 && t.length <= INSTRUCTIONS_BUDGET, `dài ${t.length}`);
  const lines = new Set(t.split("\n").slice(1).map((l) => l.split(":")[0]));
  for (const n of invocable) assert.ok(lines.has(n), `thiếu ${n}`);
  assert.ok(t.split("\n").slice(1).every((l) => /^[a-z0-9-]+: \S/.test(l)), "mỗi dòng phải là `tên: gợi ý`");
  assert.match(t, /skill_get \{name\}/);
  assert.ok(!/\btool_run\b/.test(t), "mode read không hứa tool_run");
});

test("ngân sách lớn hơn → gợi ý dài hơn; ngân sách nhỏ → chỉ tên, không bao giờ vượt", () => {
  const a = buildInstructions(cat, "read", undefined, 4000), b = buildInstructions(cat, "read", undefined, 9000);
  assert.ok(b.length > a.length && b.length <= 9000);
  for (const budget of [600, 1500, 2500]) assert.ok(buildInstructions(cat, "core", undefined, budget).length <= budget);
});

test("skillHint: bỏ câu mồi 'MUST USE when…', cắt ở ranh giới từ, có dấu …", () => {
  assert.equal(skillHint("MUST USE when user wants to research the web. More text.", 40), "research the web");
  const h = skillHint("Vẽ SƠ ĐỒ và BIỂU ĐỒ bằng máy, không để model tự bịa hình", 20);
  assert.ok(h.endsWith("…") && h.length <= 21 && !h.includes("  "));
});
