/**
 * Chạy một tool của catalog: `[runner, OVERSTACK_ROOT/<tool.path>, ...args]` bằng spawn (không shell), cwd = workspace,
 * env scrub, timeout và trần output. Tham số client đưa chỉ là chuỗi một dòng; tham số trông như đường dẫn phải nằm trong
 * workspace (hoặc /tmp) — chặn `..` và đường dẫn tuyệt đối ra ngoài.
 */
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { isAbsolute, join } from "node:path";
import type { CatalogTool } from "./catalog.ts";
import { OVERSTACK_ROOT } from "./catalog.ts";
import { insideWorkspace } from "./workspace.ts";

export const MAX_ARGS = 64;
export const MAX_ARG_LEN = 2000;
export const OUTPUT_CAP = 256 * 1024;
export const DEFAULT_TIMEOUT_MS = Number(process.env.OVERSTACK_TOOL_TIMEOUT_MS ?? 120_000);
export const MAX_TIMEOUT_MS = Number(process.env.OVERSTACK_TOOL_MAX_TIMEOUT_MS ?? 15 * 60_000);

export interface RunRequest { tool: CatalogTool; args: string[]; workspace: string; stdin?: string; timeoutMs?: number }
export interface RunResult { tool: string; argv: string[]; cwd: string; rc: number | null; signal: string | null; stdout: string; stderr: string; ms: number; truncated: boolean; timedOut: boolean }

/** Lý do một tham số bị từ chối, hoặc null. `wsDir` để soát các tham số trông như đường dẫn. */
export function argProblem(arg: string, wsDir: string): string | null {
  if (typeof arg !== "string") return "argument is not a string";
  if (arg.length > MAX_ARG_LEN) return `argument longer than ${MAX_ARG_LEN} chars`;
  if (/[\0\n\r]/.test(arg)) return "argument contains a control character";
  // `--out=path` → soát phần sau dấu =; `--flag` thuần thì bỏ qua
  const value = arg.startsWith("-") ? (arg.includes("=") ? arg.slice(arg.indexOf("=") + 1) : "") : arg;
  if (!value) return null;
  const looksPath = value.includes("/") || value.startsWith(".") || value.startsWith("~");
  if (!looksPath) return null;
  if (value.startsWith("~")) return `path ${value} uses ~ — give a workspace-relative path`;
  if (/^https?:\/\//.test(value)) return null;
  if (value.split("/").includes("..")) return `path ${value} contains ".."`;
  if (isAbsolute(value)) {
    if (value === "/tmp" || value.startsWith("/tmp/")) return null;
    if (value === "/dev/null") return null;
    return insideWorkspace(wsDir, value) ? null : `absolute path ${value} is outside the workspace`;
  }
  return insideWorkspace(wsDir, value) ? null : `path ${value} escapes the workspace`;
}

export function validateArgs(args: unknown, wsDir: string): string[] {
  if (!Array.isArray(args)) throw new Error("args must be an array of strings");
  if (args.length > MAX_ARGS) throw new Error(`more than ${MAX_ARGS} arguments`);
  for (const a of args) {
    const p = argProblem(a as string, wsDir);
    if (p) throw new Error(`refused argument ${JSON.stringify(String(a).slice(0, 80))}: ${p}`);
  }
  return args as string[];
}

/** Env tối giản cho tool: không mang secret của server vào process con. */
export function toolEnv(wsDir: string): NodeJS.ProcessEnv {
  const e: NodeJS.ProcessEnv = {
    PATH: process.env.PATH ?? "/usr/local/bin:/usr/bin:/bin",
    HOME: process.env.OVERSTACK_TOOL_HOME ?? process.env.HOME ?? "/tmp",
    LANG: "C.UTF-8", LC_ALL: "C.UTF-8", PYTHONDONTWRITEBYTECODE: "1", PYTHONUNBUFFERED: "1", NO_COLOR: "1", TERM: "dumb",
    OVERSTACK_ROOT, OVERSTACK_WORKSPACE: wsDir,
  };
  for (const k of ["ORCA_GRAPH_ENGINE_DIR", "ORCA_GRAPH_INSTALL_DIR", "PYTHONPATH"]) if (process.env[k]) e[k] = process.env[k];
  // engine orca-graph: trong container clone ở /opt/orca-graph/engine; trên máy dev ở ~/.orca-graph/repo/engine
  if (!e.ORCA_GRAPH_ENGINE_DIR) {
    for (const c of ["/opt/orca-graph/engine", join(process.env.HOME ?? "", ".orca-graph", "repo", "engine")]) {
      if (c && existsSync(join(c, "orca-graph.py"))) { e.ORCA_GRAPH_ENGINE_DIR = c; break; }
    }
  }
  return e;
}

export async function runTool(req: RunRequest, wsDir: string): Promise<RunResult> {
  const args = validateArgs(req.args, wsDir);
  const script = join(OVERSTACK_ROOT, req.tool.path);
  if (!existsSync(script)) throw new Error(`tool ${req.tool.name} missing on disk at ${req.tool.path} — regenerate the catalog`);
  const timeoutMs = Math.min(Math.max(1000, req.timeoutMs ?? DEFAULT_TIMEOUT_MS), MAX_TIMEOUT_MS);
  const argv = [req.tool.runner, script, ...args];
  const t0 = Date.now();
  return new Promise<RunResult>((resolveRun) => {
    const child = spawn(argv[0]!, argv.slice(1), { cwd: wsDir, env: toolEnv(wsDir), stdio: ["pipe", "pipe", "pipe"] });
    let out = "", err = "", truncated = false, timedOut = false;
    const take = (cur: string, chunk: Buffer) => {
      if (cur.length >= OUTPUT_CAP) { truncated = true; return cur; }
      const s = cur + chunk.toString("utf8");
      if (s.length > OUTPUT_CAP) { truncated = true; return s.slice(0, OUTPUT_CAP); }
      return s;
    };
    child.stdout.on("data", (c: Buffer) => { out = take(out, c); });
    child.stderr.on("data", (c: Buffer) => { err = take(err, c); });
    const timer = setTimeout(() => { timedOut = true; child.kill("SIGKILL"); }, timeoutMs);
    child.on("error", (e) => { clearTimeout(timer); resolveRun({ tool: req.tool.name, argv, cwd: wsDir, rc: null, signal: null, stdout: out, stderr: `${err}\n${e.message}`.trim(), ms: Date.now() - t0, truncated, timedOut }); });
    child.on("close", (rc, signal) => { clearTimeout(timer); resolveRun({ tool: req.tool.name, argv, cwd: wsDir, rc, signal, stdout: out, stderr: err, ms: Date.now() - t0, truncated, timedOut }); });
    if (req.stdin !== undefined) child.stdin.end(req.stdin); else child.stdin.end();
  });
}
