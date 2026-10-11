/**
 * overstack-mcp: McpServer từ catalog.
 *   prompts   — một prompt mỗi skill (tên = tên skill), trả nguyên văn SKILL.md + task của người gọi
 *   resources — overstack://catalog · overstack://capabilities · overstack://policy · overstack://skill/{name} ·
 *               overstack://rule/{id} · overstack://tool/{name}
 *   tools     — core: skills_list skill_find skill_get rules_list rule_check tools_list tool_help tool_run
 *                     workspace_list workspace_sync orca_graph
 *               all (OVERSTACK_TOOLS=all): thêm một tool mỗi script của catalog (tên = tên script), cùng input {args, workspace}
 * Dùng chung cho stdio (src/stdio.ts) và Streamable HTTP (src/http.ts).
 */
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { z } from "zod";
import { findRule, findSkill, findTool, loadCatalog, OVERSTACK_ROOT, searchSkills, skillBody } from "./catalog.ts";
import type { Catalog, CatalogTool } from "./catalog.ts";
import { runTool } from "./run.ts";
import type { RunResult } from "./run.ts";
import { listWorkspaces, resolveWorkspace, syncWorkspace, workspacesDir } from "./workspace.ts";

export type ToolMode = "core" | "all";
export interface ServerOptions { catalog?: Catalog; mode?: ToolMode; root?: string; version?: string }

export const VERSION = "0.1.0";
const text = (v: unknown) => ({ content: [{ type: "text" as const, text: typeof v === "string" ? v : JSON.stringify(v, null, 2) }] });
const fail = (msg: string) => ({ isError: true, content: [{ type: "text" as const, text: msg }] });
const summarize = (r: RunResult) => ({ ...r, argv: r.argv.slice(1).map((a, i) => (i === 0 ? a.replace(OVERSTACK_ROOT + "/", "") : a)) });

export function toolModeFromEnv(): ToolMode { return process.env.OVERSTACK_TOOLS === "all" ? "all" : "core"; }

export function buildServer(opts: ServerOptions = {}): McpServer {
  const cat = opts.catalog ?? loadCatalog();
  const root = opts.root ?? OVERSTACK_ROOT;
  const mode = opts.mode ?? toolModeFromEnv();
  const server = new McpServer(
    { name: "overstack", version: opts.version ?? VERSION },
    {
      instructions: [
        `overstack toolbox: ${cat.skills.length} skills (prompts, resources overstack://skill/{name}), ${cat.rules.length} wiki rules (rule_check),`,
        `${cat.tools.length} scripts (tool_run; ${mode === "all" ? "also one tool each" : "list with tools_list, read flags with tool_help"}).`,
        `Every script runs inside a workspace under ${workspacesDir()}: list with workspace_list, pull a repo with workspace_sync,`,
        "pass workspace-relative paths. Start with skill_find for the task at hand, then read the skill resource before acting.",
        "A tool result carries rc/stdout/stderr verbatim; rc 2 from a validator means the rule is broken, not that the call failed.",
      ].join(" "),
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
      const p = join(root, rel);
      return { contents: [{ uri: uri.href, mimeType: mime, text: existsSync(p) ? readFileSync(p, "utf8") : `(${rel} missing on this server)` }] };
    });
  }
  server.registerResource("skill", new ResourceTemplate("overstack://skill/{name}", {
    list: async () => ({ resources: cat.skills.map((s) => ({ uri: `overstack://skill/${s.name}`, name: s.name, title: `/${s.name}`, description: s.description.slice(0, 300), mimeType: "text/markdown" })) }),
    complete: { name: async (v) => cat.skills.map((s) => s.name).filter((n) => n.startsWith(v)).slice(0, 50) },
  }), { title: "Skill (SKILL.md)", mimeType: "text/markdown" }, async (uri, vars) => {
    const s = findSkill(cat, String(vars.name));
    if (!s) throw new Error(`no skill ${String(vars.name)}`);
    return { contents: [{ uri: uri.href, mimeType: "text/markdown", text: skillBody(s, root) }] };
  });
  server.registerResource("rule", new ResourceTemplate("overstack://rule/{id}", {
    list: async () => ({ resources: cat.rules.map((r) => ({ uri: `overstack://rule/${r.id}`, name: r.id, title: `${r.id} ${r.name ?? ""}`.trim(), description: r.statement.slice(0, 300), mimeType: "application/json" })) }),
  }), { title: "Wiki rule", mimeType: "application/json" }, async (uri, vars) => {
    const r = findRule(cat, String(vars.id));
    if (!r) throw new Error(`no rule ${String(vars.id)}`);
    const src = r.validatorPath && existsSync(join(root, r.validatorPath)) ? readFileSync(join(root, r.validatorPath), "utf8").match(/^(?:#![^\n]*\n)?[\s\S]*?"""([\s\S]*?)"""/)?.[1]?.trim() : undefined;
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
      messages: [{ role: "user", content: { type: "text", text: `${skillBody(s, root)}\n\n---\nFollow the skill above.${task ? ` Task: ${task}` : ""}` } }],
    }));
  }

  // ── tools: core ────────────────────────────────────────────────────────────
  const ro = { readOnlyHint: true, idempotentHint: true, openWorldHint: false };
  server.registerTool("skills_list", { title: "skills list", description: `List the ${cat.skills.length} overstack skills (name, group, one-line description). Filter by group: wiki-loop, dev-loop, orchestrate, utils.`, inputSchema: { group: z.string().optional() }, annotations: ro },
    async ({ group }) => text(cat.skills.filter((s) => !group || s.group === group).map((s) => ({ name: s.name, group: s.group, modelInvocable: s.modelInvocable, description: s.description.slice(0, 240) }))));
  server.registerTool("skill_find", { title: "skill find", description: "Rank skills for a task (BM25 over name, description and SKILL.md). Returns the best k with scores; read overstack://skill/{name} next.", inputSchema: { query: z.string().min(1), k: z.number().int().min(1).max(20).default(5) }, annotations: ro },
    async ({ query, k }) => text(searchSkills(cat, query, k, root)));
  server.registerTool("skill_get", { title: "skill get", description: "Full SKILL.md of one skill, by name (with or without the leading slash).", inputSchema: { name: z.string().min(1) }, annotations: ro },
    async ({ name }) => { const s = findSkill(cat, name); return s ? text(skillBody(s, root)) : fail(`no skill ${name}; try skill_find`); });
  server.registerTool("rules_list", { title: "rules list", description: "The wiki rules of harness/policy.yaml: id, name, statement, where enforced, and whether rule_check can run its validator.", inputSchema: {}, annotations: ro },
    async () => text(cat.rules.map((r) => ({ id: r.id, name: r.name, checkable: !!r.validatorPath, enforce_at: r.enforce_at, applies_to: r.applies_to, statement: r.statement }))));
  server.registerTool("rule_check", { title: "rule check", description: "Run one rule's validator on files of a workspace (paths relative to the workspace). rc 0 = pass, rc 2 = violation (reason in stderr). Rules without a validator cannot be checked.", inputSchema: { rule: z.string().min(1).describe("R9, okf-frontmatter or okf_frontmatter.py"), workspace: z.string().min(2), files: z.array(z.string()).min(1).max(200) }, annotations: { readOnlyHint: true, openWorldHint: false } },
    async ({ rule, workspace, files }) => {
      const r = findRule(cat, rule);
      if (!r) return fail(`no rule ${rule}; see rules_list`);
      if (!r.validatorPath) return fail(`${r.id} ${r.name ?? ""} has no validator (${r.validator ?? "automation / pre-commit"}); it cannot be checked here`);
      const tool = cat.tools.find((t) => t.path === r.validatorPath) ?? ({ name: r.id, file: r.validatorPath.split("/").pop()!, kind: "validator", path: r.validatorPath, runner: "python3", summary: "", usage: null, options: [], positionals: [], help: null, helpRc: null, stdinJson: true } satisfies CatalogTool);
      let wsDir: string; try { wsDir = resolveWorkspace(workspace); } catch (e) { return fail((e as Error).message); }
      try {
        const res = await runTool({ tool, args: files, workspace }, wsDir);
        return text({ rule: r.id, name: r.name, pass: res.rc === 0, ...summarize(res) });
      } catch (e) { return fail((e as Error).message); }
    });
  server.registerTool("tools_list", { title: "tools list", description: `List the ${cat.tools.length} scripts (harness-script, fdk-tool, validator) with a one-line summary. Filter by kind or a substring of the name.`, inputSchema: { kind: z.enum(["harness-script", "fdk-tool", "validator"]).optional(), match: z.string().optional() }, annotations: ro },
    async ({ kind, match }) => text(cat.tools.filter((t) => (!kind || t.kind === kind) && (!match || t.name.includes(match) || t.summary.toLowerCase().includes(match.toLowerCase()))).map((t) => ({ name: t.name, kind: t.kind, runner: t.runner, hasHelp: !!t.help, summary: t.summary.slice(0, 200) }))));
  server.registerTool("tool_help", { title: "tool help", description: "Usage, flags and positionals of one script (parsed from --help), plus the raw help text.", inputSchema: { name: z.string().min(1) }, annotations: ro },
    async ({ name }) => { const t = findTool(cat, name); return t ? text({ name: t.name, path: t.path, runner: t.runner, usage: t.usage, summary: t.summary, options: t.options, positionals: t.positionals, stdinJson: t.stdinJson, help: t.help }) : fail(`no tool ${name}; see tools_list`); });
  const runSchema = { name: z.string().min(1).describe("script name from tools_list, e.g. wiki-health"), args: z.array(z.string()).max(64).default([]).describe("argv after the script, one token each; paths relative to the workspace"), workspace: z.string().min(2).describe("workspace name under WORKSPACES_DIR"), stdin: z.string().optional().describe("text piped to stdin (validators accept hook JSON here)"), timeoutMs: z.number().int().min(1000).optional() };
  const runImpl = async ({ name, args, workspace, stdin, timeoutMs }: { name: string; args: string[]; workspace: string; stdin?: string; timeoutMs?: number }) => {
    const t = findTool(cat, name);
    if (!t) return fail(`no tool ${name}; see tools_list`);
    let wsDir: string; try { wsDir = resolveWorkspace(workspace); } catch (e) { return fail((e as Error).message); }
    try { return text(summarize(await runTool({ tool: t, args, workspace, stdin, timeoutMs }, wsDir))); } catch (e) { return fail((e as Error).message); }
  };
  server.registerTool("tool_run", { title: "tool run", description: "Run one overstack script inside a workspace with a fixed argv (no shell). Returns rc, stdout, stderr (each capped at 256 KiB), duration, and whether it timed out. Scripts may write inside the workspace; nothing outside it.", inputSchema: runSchema, annotations: { readOnlyHint: false, destructiveHint: false, openWorldHint: false } }, runImpl);
  server.registerTool("workspace_list", { title: "workspace list", description: `Workspaces under ${workspacesDir()}: name, whether it is a git checkout, has .llmwiki and .harness.`, inputSchema: {}, annotations: ro },
    async () => text(listWorkspaces()));
  server.registerTool("workspace_sync", { title: "workspace sync", description: "Pull one ref of a git repo into a workspace (created on first use): fetch --depth 1, checkout -f. Only repos whose URL starts with a prefix in OVERSTACK_GIT_ALLOW. Untracked files in the workspace are kept.", inputSchema: { name: z.string().min(2), repo: z.string().url(), ref: z.string().min(1).default("main") }, annotations: { readOnlyHint: false, destructiveHint: false, openWorldHint: true } },
    async ({ name, repo, ref }) => { const r = await syncWorkspace(name, repo, ref); return r.ok ? text(r) : fail(JSON.stringify(r, null, 2)); });
  server.registerTool("orca_graph", { title: "orca graph", description: "orca-graph engine (build/ask/next/lock/set/run/audit/add-node…) on a workspace: argv after `orca-graph.py`, e.g. [\"build\", \".llmwiki/wiki/sources/draft/x-PLAN.md\"] or [\"ask\", \"<id>\", \"needs\"]. Store defaults to <workspace>/.llmwiki/graph.", inputSchema: { args: z.array(z.string()).min(1).max(64), workspace: z.string().min(2), timeoutMs: z.number().int().min(1000).optional() }, annotations: { readOnlyHint: false, destructiveHint: false, openWorldHint: false } },
    async ({ args, workspace, timeoutMs }) => runImpl({ name: "orca-graph", args, workspace, timeoutMs }));

  // ── tools: all — một tool mỗi script ───────────────────────────────────────
  if (mode === "all") {
    for (const t of cat.tools) {
      const desc = `${t.summary || t.file}${t.usage ? `\nusage: ${t.usage}` : ""}`.slice(0, 1000);
      server.registerTool(t.name, { title: t.file, description: desc, inputSchema: { args: runSchema.args, workspace: runSchema.workspace, stdin: runSchema.stdin, timeoutMs: runSchema.timeoutMs }, annotations: { readOnlyHint: t.kind === "validator", openWorldHint: false } },
        async ({ args, workspace, stdin, timeoutMs }) => runImpl({ name: t.name, args, workspace, stdin, timeoutMs }));
    }
  }
  return server;
}
