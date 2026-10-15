/**
 * Lõi ĐỌC của overstack-mcp — mọi thứ không cần đĩa hay tiến trình con, chạy được trên Node lẫn Cloudflare Workers:
 *   prompts   — một prompt mỗi skill (tên = tên skill), trả nguyên văn SKILL.md + task của người gọi
 *   resources — overstack://catalog · overstack://capabilities · overstack://policy · overstack://skill/{name} ·
 *               overstack://rule/{id} · overstack://tool/{name}
 *   tools     — skills_list skill_find skill_get rules_list tools_list tool_help (6 tool đọc)
 * Phần chạy tool/workspace (rule_check, tool_run, workspace_*, orca_graph, mode all) ở src/server.ts (chỉ Node).
 */
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { findRule, findSkill, findTool, searchSkills } from "./catalog.ts";
import type { Catalog } from "./catalog.ts";
import type { Source } from "./source.ts";

export type ToolMode = "read" | "core" | "all";
export interface CoreOptions { catalog: Catalog; mode: ToolMode; source: Source; version?: string; workspacesHint?: string }

export const VERSION = "0.1.0";
export const text = (v: unknown) => ({ content: [{ type: "text" as const, text: typeof v === "string" ? v : JSON.stringify(v, null, 2) }] });
export const fail = (msg: string) => ({ isError: true, content: [{ type: "text" as const, text: msg }] });
export const RO = { readOnlyHint: true, idempotentHint: true, openWorldHint: false };

/** OVERSTACK_TOOLS: read (hostname công khai, không chạy gì) · core (mặc định) · all. Workers không có process → đọc qua globalThis. */
export function toolModeFromEnv(env: Record<string, string | undefined> | undefined = (globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env): ToolMode {
  const v = env?.OVERSTACK_TOOLS;
  return v === "all" ? "all" : v === "read" ? "read" : "core";
}

/** Claude Code chép `instructions` vào system prompt mỗi phiên nhưng CẮT ở 4096 ký tự (CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH,
 *  bản 2.1.300). Để skill trên server được "biết" như skill local, instructions = lời dặn ngắn + danh mục skill model tự gọi,
 *  mỗi dòng `tên: gợi ý` — gợi ý dài nhất sao cho cả khối ≤ ngân sách (OVERSTACK_INSTRUCTIONS_BUDGET, mặc định 4000). */
export const INSTRUCTIONS_BUDGET = 4000;
export function skillHint(description: string, n: number): string {
  let d = description.replace(/\s+/g, " ").trim();
  d = d.replace(/^(MUST USE|Use this skill|Use|Invoke|Trigger)\b[^,:]*?(when|for|to)\s+(the\s+)?(user\s+)?(wants?\s+to\s+|asks?\s+(to|for)\s+)?/i, "");
  d = d.split(/(?<=[.;])\s| — | Use when/)[0]!.replace(/[.]$/, "");
  if (d.length <= n) return d;
  const cut = d.slice(0, n), sp = cut.lastIndexOf(" ");
  return (sp > n / 2 ? cut.slice(0, sp) : cut).replace(/[,;:—-]+$/, "") + "…";
}
export function buildInstructions(cat: Catalog, mode: ToolMode, workspacesHint?: string, budget = budgetFromEnv()): string {
  const head = [
    `overstack: shared skill library (${cat.skills.length} skills) + harness catalog (${cat.rules.length} rules, ${cat.tools.length} tools).`,
    "Treat the skills below like your local skills: when the user's task matches one, call skill_get {name} and follow it BEFORE acting",
    "(a local skill with the same name wins). Unsure which → skill_find {query}.",
    mode === "read" ? "This endpoint runs nothing: rules_list/tools_list/tool_help describe the harness; install it locally to run tools." : `Run scripts with tool_run inside a workspace under ${workspacesHint ?? "WORKSPACES_DIR"} (workspace_list, workspace_sync).`,
    "Skills:",
  ].join(" ");
  const skills = cat.skills.filter((s) => s.modelInvocable).sort((a, b) => a.name.localeCompare(b.name));
  const render = (n: number) => head + "\n" + skills.map((s) => (n > 0 ? `${s.name}: ${skillHint(s.description, n)}` : s.name)).join("\n");
  for (let n = 160; n >= 12; n -= 4) { const t = render(n); if (t.length <= budget) return t; }
  const names = render(0);
  return names.length <= budget ? names : head.slice(0, budget);
}
function budgetFromEnv(): number {
  const v = Number((globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env?.OVERSTACK_INSTRUCTIONS_BUDGET);
  return Number.isFinite(v) && v >= 500 ? v : INSTRUCTIONS_BUDGET;
}

export function buildCoreServer(opts: CoreOptions): McpServer {
  const { catalog: cat, mode, source } = opts;
  const server = new McpServer(
    { name: "overstack", version: opts.version ?? VERSION },
    {
      instructions: buildInstructions(cat, mode, opts.workspacesHint),
    },
  );

  // ── resources ──────────────────────────────────────────────────────────────
  server.registerResource("catalog", "overstack://catalog", { title: "Overstack catalog", description: "Skills, rules and tools this server serves (names, groups, summaries).", mimeType: "application/json" }, async (uri) => ({
    contents: [{ uri: uri.href, mimeType: "application/json", text: JSON.stringify({
      skills: cat.skills.map((s) => ({ name: s.name, group: s.group, modelInvocable: s.modelInvocable, description: s.description })),
      rules: cat.rules.map((r) => ({ id: r.id, name: r.name, checkable: !!r.validatorPath, statement: r.statement })),
      tools: cat.tools.map((t) => ({ name: t.name, kind: t.kind, runner: t.runner, summary: t.summary.slice(0, 200) })),
    }, null, 1) }],
  }));
  for (const [name, rel, title, mime] of [["capabilities", "fdk/CAPABILITIES.md", "CAPABILITIES.md của overstack", "text/markdown"], ["policy", "harness/policy.yaml", "policy.yaml — 22 luật L0", "text/yaml"]] as const) {
    server.registerResource(name, `overstack://${name}`, { title, mimeType: mime }, async (uri) => {
      const body = await source.read(rel);
      return { contents: [{ uri: uri.href, mimeType: mime, text: body ?? `(${rel} missing on this server)` }] };
    });
  }
  server.registerResource("skill", new ResourceTemplate("overstack://skill/{name}", {
    list: async () => ({ resources: cat.skills.map((s) => ({ uri: `overstack://skill/${s.name}`, name: s.name, title: `/${s.name}`, description: s.description.slice(0, 300), mimeType: "text/markdown" })) }),
    complete: { name: async (v) => cat.skills.map((s) => s.name).filter((n) => n.startsWith(v)).slice(0, 50) },
  }), { title: "Skill (SKILL.md)", mimeType: "text/markdown" }, async (uri, vars) => {
    const s = findSkill(cat, String(vars.name));
    if (!s) throw new Error(`no skill ${String(vars.name)}`);
    return { contents: [{ uri: uri.href, mimeType: "text/markdown", text: await source.skillBody(s) }] };
  });
  server.registerResource("rule", new ResourceTemplate("overstack://rule/{id}", {
    list: async () => ({ resources: cat.rules.map((r) => ({ uri: `overstack://rule/${r.id}`, name: r.id, title: `${r.id} ${r.name ?? ""}`.trim(), description: r.statement.slice(0, 300), mimeType: "application/json" })) }),
  }), { title: "Wiki rule", mimeType: "application/json" }, async (uri, vars) => {
    const r = findRule(cat, String(vars.id));
    if (!r) throw new Error(`no rule ${String(vars.id)}`);
    const py = r.validatorPath ? await source.read(r.validatorPath) : null;
    const src = py?.match(/^(?:#![^\n]*\n)?[\s\S]*?"""([\s\S]*?)"""/)?.[1]?.trim();
    return { contents: [{ uri: uri.href, mimeType: "application/json", text: JSON.stringify({ ...r, validatorDoc: src }, null, 2) }] };
  });
  server.registerResource("tool", new ResourceTemplate("overstack://tool/{name}", {
    list: async () => ({ resources: cat.tools.map((t) => ({ uri: `overstack://tool/${t.name}`, name: t.name, title: t.file, description: t.summary.slice(0, 300), mimeType: "text/plain" })) }),
  }), { title: "Tool help (--help)", mimeType: "text/plain" }, async (uri, vars) => {
    const t = findTool(cat, String(vars.name));
    if (!t) throw new Error(`no tool ${String(vars.name)}`);
    return { contents: [{ uri: uri.href, mimeType: "text/plain", text: t.help ?? `${t.file}: ${t.summary || "(no --help; see source)"}` }] };
  });

  // ── prompts: một prompt mỗi skill ──────────────────────────────────────────
  for (const s of cat.skills) {
    server.registerPrompt(s.name, {
      title: `/${s.name}`,
      description: `${s.modelInvocable ? "" : "[user-invoked skill] "}${s.description}`.slice(0, 1000),
      argsSchema: { task: z.string().optional().describe("Việc cần làm với skill này (tuỳ chọn)") },
    }, async ({ task }) => ({
      description: `overstack skill /${s.name}`,
      messages: [{ role: "user", content: { type: "text", text: `${await source.skillBody(s)}\n\n---\nFollow the skill above.${task ? ` Task: ${task}` : ""}` } }],
    }));
  }

  // ── tools: đọc ─────────────────────────────────────────────────────────────
  server.registerTool("skills_list", { title: "skills list", description: `List the ${cat.skills.length} overstack skills installed for this environment (name, group, one-line description) — the ready-made procedures the team expects you to follow. Filter by group: wiki-loop, dev-loop, orchestrate, utils.`, inputSchema: { group: z.string().optional() }, annotations: RO },
    async ({ group }) => text(cat.skills.filter((s) => !group || s.group === group).map((s) => ({ name: s.name, group: s.group, modelInvocable: s.modelInvocable, description: s.description.slice(0, 240) }))));
  server.registerTool("skill_find", { title: "skill find", description: "CALL THIS FIRST whenever the user asks how to do something, whether a standard/ready-made way exists here, or before starting any task (render markdown→HTML, docs site, UI design, deploy, wiki, review, research…): ranks the team's skills for the task (BM25 over name, description and SKILL.md) and returns the best k with scores. A hit ≥ 8 means a procedure exists — fetch it with skill_get and follow it instead of improvising.", inputSchema: { query: z.string().min(1), k: z.number().int().min(1).max(20).default(5) }, annotations: RO },
    async ({ query, k }) => text(searchSkills(cat, query, k, await source.skillHeads())));
  server.registerTool("skill_get", { title: "skill get", description: "Full SKILL.md of one skill, by name (with or without the leading slash) — the exact procedure to follow. Use after skill_find, or when the user names a skill.", inputSchema: { name: z.string().min(1) }, annotations: RO },
    async ({ name }) => { const s = findSkill(cat, name); return s ? text(await source.skillBody(s)) : fail(`no skill ${name}; try skill_find`); });
  server.registerTool("rules_list", { title: "rules list", description: "The wiki rules of harness/policy.yaml: id, name, statement, where enforced, and whether rule_check can run its validator.", inputSchema: {}, annotations: RO },
    async () => text(cat.rules.map((r) => ({ id: r.id, name: r.name, checkable: !!r.validatorPath, enforce_at: r.enforce_at, applies_to: r.applies_to, statement: r.statement }))));
  server.registerTool("tools_list", { title: "tools list", description: `List the ${cat.tools.length} scripts (harness-script, fdk-tool, validator) with a one-line summary. Filter by kind or a substring of the name.`, inputSchema: { kind: z.enum(["harness-script", "fdk-tool", "validator"]).optional(), match: z.string().optional() }, annotations: RO },
    async ({ kind, match }) => text(cat.tools.filter((t) => (!kind || t.kind === kind) && (!match || t.name.includes(match) || t.summary.toLowerCase().includes(match.toLowerCase()))).map((t) => ({ name: t.name, kind: t.kind, runner: t.runner, hasHelp: !!t.help, summary: t.summary.slice(0, 200) }))));
  server.registerTool("tool_help", { title: "tool help", description: "Usage, flags and positionals of one script (parsed from --help), plus the raw help text.", inputSchema: { name: z.string().min(1) }, annotations: RO },
    async ({ name }) => { const t = findTool(cat, name); return t ? text({ name: t.name, path: t.path, runner: t.runner, usage: t.usage, summary: t.summary, options: t.options, positionals: t.positionals, stdinJson: t.stdinJson, help: t.help }) : fail(`no tool ${name}; see tools_list`); });
  return server;
}
