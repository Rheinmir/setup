/**
 * Workspace: thư mục con của WORKSPACES_DIR mà tool chạy bên trong (cwd). Mọi đường dẫn client đưa phải nằm trong đó.
 * `workspace_sync` kéo một repo (prefix trong OVERSTACK_GIT_ALLOW) vào workspace — cùng hợp đồng với `stack_sync` của
 * devops-agent: argv cố định, không prompt, không hook, token đi qua env và bị scrub khỏi log.
 */
import { execFile } from "node:child_process";
import { existsSync, mkdirSync, readdirSync, realpathSync, statSync } from "node:fs";
import { join, resolve, sep } from "node:path";
import { promisify } from "node:util";

const pexec = promisify(execFile);
/** Đọc lúc gọi (không phải lúc import) để test và entry đặt env trước khi dùng. */
export const workspacesDir = () => resolve(process.env.WORKSPACES_DIR ?? "/workspaces");
export const NAME = /^[a-z0-9][a-z0-9-]{1,40}$/;
const REF = /^(?!.*\.\.)[A-Za-z0-9][A-Za-z0-9._/-]{0,100}$/;
const REPO = /^https:\/\/[A-Za-z0-9.-]+\/[A-Za-z0-9._-]+\/[A-Za-z0-9._-]+?(\.git)?$/;

export const gitAllow = () => (process.env.OVERSTACK_GIT_ALLOW ?? "https://github.com/Rheinmir/").split(",").map((x) => x.trim()).filter(Boolean);

export interface WorkspaceInfo { name: string; dir: string; git: boolean; hasWiki: boolean; hasHarness: boolean }

export function listWorkspaces(dir = workspacesDir()): WorkspaceInfo[] {
  if (!existsSync(dir)) return [];
  return readdirSync(dir).filter((n) => NAME.test(n) && statSync(join(dir, n)).isDirectory()).map((name) => {
    const d = join(dir, name);
    return { name, dir: d, git: existsSync(join(d, ".git")), hasWiki: existsSync(join(d, ".llmwiki")) || existsSync(join(d, "llmwiki")), hasHarness: existsSync(join(d, ".harness")) || existsSync(join(d, "harness")) };
  });
}

/** Thư mục tuyệt đối của workspace; throw khi tên sai hoặc chưa tồn tại (misconfiguration fails loud). */
export function resolveWorkspace(name: string, dir = workspacesDir()): string {
  if (!NAME.test(name)) throw new Error(`invalid workspace name ${JSON.stringify(name)} (lowercase letters, digits, dashes; 2–41 chars)`);
  const d = join(dir, name);
  if (!existsSync(d) || !statSync(d).isDirectory()) throw new Error(`no workspace ${name} under ${dir} — workspace_sync it first, or mount it`);
  return d;
}

/** `rel` (đường dẫn client đưa) có nằm trong workspace không — so sau khi resolve, chặn `..` và symlink thoát ra ngoài. */
export function insideWorkspace(wsDir: string, rel: string): boolean {
  if (rel.includes("\0")) return false;
  const target = resolve(wsDir, rel);
  const root = realpathSync(wsDir);
  let real = target;
  // phần đã tồn tại thì realpath (bắt symlink), phần chưa tồn tại giữ nguyên
  let probe = target;
  while (!existsSync(probe)) { const parent = resolve(probe, ".."); if (parent === probe) break; probe = parent; }
  try { real = join(realpathSync(probe), target.slice(probe.length)); } catch { return false; }
  return real === root || real.startsWith(root + sep);
}

export function syncProblem(repo: string, ref: string, allow = gitAllow()): string | null {
  if (!REPO.test(repo)) return `invalid repo ${JSON.stringify(repo)} (https://host/owner/name only)`;
  if (!allow.some((p) => repo.startsWith(p))) return `refused: ${repo} is not in OVERSTACK_GIT_ALLOW (${allow.join(", ")})`;
  if (!REF.test(ref)) return `invalid ref ${JSON.stringify(ref)} (branch, tag or commit; no "..")`;
  return null;
}

function gitEnv(repo: string): NodeJS.ProcessEnv {
  const cfg: Array<[string, string]> = [["safe.directory", "*"], ["core.hooksPath", "/dev/null"]];
  const token = process.env.OVERSTACK_GIT_TOKEN;
  if (token && repo.startsWith("https://github.com/")) cfg.push(["http.extraHeader", `Authorization: Basic ${Buffer.from(`x-access-token:${token}`).toString("base64")}`]);
  const e: NodeJS.ProcessEnv = { PATH: process.env.PATH ?? "/usr/local/bin:/usr/bin:/bin", HOME: process.env.HOME ?? "/tmp", GIT_TERMINAL_PROMPT: "0", GIT_CONFIG_NOSYSTEM: "1", GIT_CONFIG_COUNT: String(cfg.length) };
  cfg.forEach(([k, v], i) => { e[`GIT_CONFIG_KEY_${i}`] = k; e[`GIT_CONFIG_VALUE_${i}`] = v; });
  return e;
}
const scrub = (t: string) => t.replace(/Authorization: Basic \S+/g, "Authorization: Basic ***").trim();

export interface SyncResult { ok: boolean; workspace: string; repo: string; ref: string; sha?: string; previous?: string | null; subject?: string; error?: string; log: string }

/** Đưa `ref` của `repo` vào workspace: init lần đầu, fetch đúng một ref (depth 1), checkout -f. File untracked giữ nguyên. */
export async function syncWorkspace(name: string, repo: string, ref: string, dir = workspacesDir()): Promise<SyncResult> {
  if (!NAME.test(name)) return { ok: false, workspace: name, repo, ref, error: `invalid workspace name ${JSON.stringify(name)}`, log: "" };
  const problem = syncProblem(repo, ref);
  if (problem) return { ok: false, workspace: name, repo, ref, error: problem, log: "" };
  const ws = join(dir, name);
  mkdirSync(ws, { recursive: true });
  const env = gitEnv(repo), log: string[] = [];
  const git = async (args: string[], timeout = 180_000) => {
    const r = await pexec("git", args, { cwd: ws, env, timeout, maxBuffer: 8 * 1024 * 1024 });
    log.push(`$ git ${args.join(" ")}`); return r.stdout.trim();
  };
  try {
    if (!existsSync(join(ws, ".git"))) await git(["init", "-q"]);
    await pexec("git", ["remote", "remove", "origin"], { cwd: ws, env }).catch(() => undefined);
    await git(["remote", "add", "origin", repo]);
    const previous = await git(["rev-parse", "HEAD"]).catch(() => null);
    await git(["fetch", "--depth", "1", "origin", ref]);
    await git(["checkout", "-q", "-f", "-B", "sync", "FETCH_HEAD"]);
    const sha = await git(["rev-parse", "HEAD"]);
    const subject = await git(["log", "-1", "--format=%s"]);
    return { ok: true, workspace: name, repo, ref, sha, previous, subject, log: log.join("\n") };
  } catch (e) {
    const x = e as { stderr?: string; message: string };
    return { ok: false, workspace: name, repo, ref, error: scrub(x.stderr || x.message).slice(-1500), log: log.join("\n") };
  }
}
