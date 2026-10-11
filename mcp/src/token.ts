/**
 * Bearer token của /mcp. Thứ tự: OVERSTACK_MCP_TOKEN (env / .env của stack) → file `<WORKSPACES_DIR>/.overstack-mcp-token`
 * (volume, sống qua restart) → sinh mới (48 hex) và ghi file 0600. Nhờ đó stack deploy được qua devops-agent mà không cần
 * ai ghi .env trên host trước; operator đọc token bằng `docker exec overstack-mcp cat /workspaces/.overstack-mcp-token`.
 * Token < 16 ký tự bị từ chối (misconfiguration fails loud).
 */
import { randomBytes } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

export type TokenSource = "env" | "file" | "generated";
export const TOKEN_FILE = ".overstack-mcp-token";

export function resolveToken(workspacesDir: string, env: NodeJS.ProcessEnv = process.env): { token: string; source: TokenSource; path?: string } {
  const fromEnv = (env.OVERSTACK_MCP_TOKEN ?? "").trim();
  if (fromEnv) {
    if (fromEnv.length < 16) throw new Error("OVERSTACK_MCP_TOKEN must be ≥ 16 chars — generate one: openssl rand -hex 32");
    return { token: fromEnv, source: "env" };
  }
  const path = join(workspacesDir, TOKEN_FILE);
  if (existsSync(path)) {
    const t = readFileSync(path, "utf8").trim();
    if (t.length >= 16) return { token: t, source: "file", path };
  }
  const token = randomBytes(24).toString("hex");
  mkdirSync(workspacesDir, { recursive: true });
  writeFileSync(path, token + "\n", { mode: 0o600 });
  return { token, source: "generated", path };
}
