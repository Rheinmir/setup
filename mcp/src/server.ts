/**
 * overstack-mcp trên Node (stdio + Docker/HTTP): lõi đọc (src/core.ts) + phần CHẠY cần đĩa và tiến trình con:
 *   tools core: rule_check tool_run workspace_list workspace_sync orca_graph (mode core/all; read chỉ có workspace_list)
 *   all (OVERSTACK_TOOLS=all): thêm một tool mỗi script của catalog (tên = tên script), cùng input {args, workspace}
 * Worker (src/worker.ts) KHÔNG import file này — nó chỉ dùng core.ts.
 */
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { findRule, findTool, loadCatalog, OVERSTACK_ROOT } from "./catalog.ts";
import type { Catalog, CatalogTool } from "./catalog.ts";
import { buildCoreServer, fail, RO, text, toolModeFromEnv, VERSION } from "./core.ts";
import type { ToolMode } from "./core.ts";
import { runTool } from "./run.ts";
import type { RunResult } from "./run.ts";
import type { Source } from "./source.ts";
import { NodeSource } from "./source-node.ts";
import { listWorkspaces, resolveWorkspace, syncWorkspace, workspacesDir } from "./workspace.ts";

export { toolModeFromEnv, VERSION };
export type { ToolMode };
export interface ServerOptions { catalog?: Catalog; mode?: ToolMode; root?: string; version?: string; source?: Source }

const summarize = (r: RunResult) => ({ ...r, argv: r.argv.slice(1).map((a, i) => (i === 0 ? a.replace(OVERSTACK_ROOT + "/", "") : a)) });

export function buildServer(opts: ServerOptions = {}): McpServer {
  const cat = opts.catalog ?? loadCatalog();
  const root = opts.root ?? OVERSTACK_ROOT;
  const mode = opts.mode ?? toolModeFromEnv();
  const source = opts.source ?? new NodeSource(root, cat);
  const server = buildCoreServer({ catalog: cat, mode, source, version: opts.version, workspacesHint: workspacesDir() });
  registerExecTools(server, cat, mode);
  return server;
}

/** Tool cần đĩa/tiến trình con. workspace_list có ở mọi mode (chỉ đọc thư mục); phần còn lại tắt ở mode read. */
export function registerExecTools(server: McpServer, cat: Catalog, mode: ToolMode): void {
  if (mode !== "read") server.registerTool("rule_check", { title: "rule check", description: "Run one rule's validator on files of a workspace (paths relative to the workspace). rc 0 = pass, rc 2 = violation (reason in stderr). Rules without a validator cannot be checked.", inputSchema: { rule: z.string().min(1).describe("R9, okf-frontmatter or okf_frontmatter.py"), workspace: z.string().min(2), files: z.array(z.string()).min(1).max(200) }, annotations: { readOnlyHint: true, openWorldHint: false } },
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
  const runSchema = { name: z.string().min(1).describe("script name from tools_list, e.g. wiki-health"), args: z.array(z.string()).max(64).default([]).describe("argv after the script, one token each; paths relative to the workspace"), workspace: z.string().min(2).describe("workspace name under WORKSPACES_DIR"), stdin: z.string().optional().describe("text piped to stdin (validators accept hook JSON here)"), timeoutMs: z.number().int().min(1000).optional() };
  const runImpl = async ({ name, args, workspace, stdin, timeoutMs }: { name: string; args: string[]; workspace: string; stdin?: string; timeoutMs?: number }) => {
    const t = findTool(cat, name);
    if (!t) return fail(`no tool ${name}; see tools_list`);
    let wsDir: string; try { wsDir = resolveWorkspace(workspace); } catch (e) { return fail((e as Error).message); }
    try { return text(summarize(await runTool({ tool: t, args, workspace, stdin, timeoutMs }, wsDir))); } catch (e) { return fail((e as Error).message); }
  };
  if (mode !== "read") server.registerTool("tool_run", { title: "tool run", description: "Run one overstack script inside a workspace with a fixed argv (no shell). Returns rc, stdout, stderr (each capped at 256 KiB), duration, and whether it timed out. Scripts may write inside the workspace; nothing outside it.", inputSchema: runSchema, annotations: { readOnlyHint: false, destructiveHint: false, openWorldHint: false } }, runImpl);
  server.registerTool("workspace_list", { title: "workspace list", description: `Workspaces under ${workspacesDir()}: name, whether it is a git checkout, has .llmwiki and .harness.`, inputSchema: {}, annotations: RO },
    async () => text(listWorkspaces()));
  if (mode !== "read") server.registerTool("workspace_sync", { title: "workspace sync", description: "Pull one ref of a git repo into a workspace (created on first use): fetch --depth 1, checkout -f. Only repos whose URL starts with a prefix in OVERSTACK_GIT_ALLOW. Untracked files in the workspace are kept.", inputSchema: { name: z.string().min(2), repo: z.string().url(), ref: z.string().min(1).default("main") }, annotations: { readOnlyHint: false, destructiveHint: false, openWorldHint: true } },
    async ({ name, repo, ref }) => { const r = await syncWorkspace(name, repo, ref); return r.ok ? text(r) : fail(JSON.stringify(r, null, 2)); });
  if (mode !== "read") server.registerTool("orca_graph", { title: "orca graph", description: "orca-graph engine (build/ask/next/lock/set/run/audit/add-node…) on a workspace: argv after `orca-graph.py`, e.g. [\"build\", \".llmwiki/wiki/sources/draft/x-PLAN.md\"] or [\"ask\", \"<id>\", \"needs\"]. Store defaults to <workspace>/.llmwiki/graph.", inputSchema: { args: z.array(z.string()).min(1).max(64), workspace: z.string().min(2), timeoutMs: z.number().int().min(1000).optional() }, annotations: { readOnlyHint: false, destructiveHint: false, openWorldHint: false } },
    async ({ args, workspace, timeoutMs }) => runImpl({ name: "orca-graph", args, workspace, timeoutMs }));

  // ── tools: all — một tool mỗi script ───────────────────────────────────────
  if (mode === "all") {
    for (const t of cat.tools) {
      const desc = `${t.summary || t.file}${t.usage ? `\nusage: ${t.usage}` : ""}`.slice(0, 1000);
      server.registerTool(t.name, { title: t.file, description: desc, inputSchema: { args: runSchema.args, workspace: runSchema.workspace, stdin: runSchema.stdin, timeoutMs: runSchema.timeoutMs }, annotations: { readOnlyHint: t.kind === "validator", openWorldHint: false } },
        async ({ args, workspace, stdin, timeoutMs }) => runImpl({ name: t.name, args, workspace, stdin, timeoutMs }));
    }
  }
}
