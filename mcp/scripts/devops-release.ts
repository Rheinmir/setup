/**
 * Lái deploy overstack-mcp qua MCP của devops-agent (không ssh, không rsync):
 *   DEVOPS_AGENT_URL=http://<host>:8787/mcp DEVOPS_AGENT_TOKEN=… npx tsx scripts/devops-release.ts release [ref]
 *       → asset_upsert (kind service, name overstack-mcp, facts repo/ref/stack/dir) rồi flow_run stack_release
 *         (hostops_stack_fetch: git fetch ref vào /home/rhein/stacks/overstack-mcp, tạo thư mục lần đầu;
 *          hostops_stack_deploy: docker compose up -d --build). Ở autonomy `ask`, hai lệnh ghi chờ duyệt trên web UI.
 *   … devops-release.ts status      → flow stacks_list + stack_source cho stack overstack-mcp (state, health, sha đang chạy)
 *   … devops-release.ts wait [sec]  → poll status tới khi service healthy (mặc định 900 s), rc 0/1
 * Token của devops-agent là của NGƯỜI VẬN HÀNH; script không in nó. Mặc định STACK=overstack-mcp, REPO=https://github.com/Rheinmir/setup.
 */
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const URL_ = process.env.DEVOPS_AGENT_URL;
const TOKEN = process.env.DEVOPS_AGENT_TOKEN;
if (!URL_ || !TOKEN) { console.error("need DEVOPS_AGENT_URL (…/mcp) and DEVOPS_AGENT_TOKEN"); process.exit(2); }
const STACK = process.env.STACK ?? "overstack-mcp";
const REPO = process.env.REPO ?? "https://github.com/Rheinmir/setup";
const STACKS_DIR = process.env.STACKS_DIR ?? "/home/rhein/stacks";
const [cmd = "status", arg] = process.argv.slice(2);

const client = new Client({ name: "overstack-mcp-release", version: "0" });
await client.connect(new StreamableHTTPClientTransport(new URL(URL_), { requestInit: { headers: { authorization: `Bearer ${TOKEN}` } } }));
const txt = (r: unknown) => (((r as { content?: Array<{ type: string; text?: string }> }).content) ?? []).filter((c) => c.type === "text").map((c) => c.text ?? "").join("\n");
// stack_release = fetch + deploy (deploy chờ tới 40 s rồi trả job): nâng timeout request lên 10 phút thay vì 60 s mặc định của SDK
const call = async (name: string, args: Record<string, unknown>) => { const r = await client.callTool({ name, arguments: args }, undefined, { timeout: 600_000 }); const t = txt(r); if (r.isError) throw new Error(`${name}: ${t.slice(0, 800)}`); try { return JSON.parse(t) as Record<string, unknown>; } catch { return { text: t }; } };

interface Service { service: string; container: string; state: string; status: string; health?: string; ports: string[] }
interface StackRow { name: string; dir: string; composeFile: string | null; hasEnv: boolean; services?: Service[]; error?: string }

async function status(): Promise<{ stack?: StackRow; source?: Record<string, unknown> }> {
  const list = await call("flow_run", { name: "stacks_list", params: {} }) as { steps?: Array<{ output?: { stacks?: StackRow[] } }> };
  const stack = list.steps?.[0]?.output?.stacks?.find((s) => s.name === STACK);
  let source: Record<string, unknown> | undefined;
  if (stack) {
    try { const src = await call("flow_run", { name: "stack_source", params: { asset: STACK } }) as { steps?: Array<{ output?: Record<string, unknown> }> }; source = src.steps?.[0]?.output; } catch (e) { source = { error: (e as Error).message.slice(0, 300) }; }
  }
  return { stack, source };
}
const healthy = (s?: StackRow) => !!s?.services?.length && s.services.every((x) => x.state === "running" && (x.health ?? "healthy") === "healthy");
const brief = (s: { stack?: StackRow; source?: Record<string, unknown> }) => s.stack
  ? `${STACK}: ${s.stack.services?.map((x) => `${x.service}=${x.state}${x.health ? `/${x.health}` : ""}${x.ports.length ? ` ${x.ports.join(",")}` : ""}`).join(" · ") || "(no services yet)"}  env=${s.stack.hasEnv} compose=${s.stack.composeFile}  src=${JSON.stringify(s.source ?? {}).slice(0, 300)}`
  : `${STACK}: not staged under ${STACKS_DIR}`;

if (cmd === "status") {
  console.log(brief(await status()));
} else if (cmd === "wait") {
  const deadline = Date.now() + Number(arg ?? 900) * 1000;
  let last = "";
  while (Date.now() < deadline) {
    const s = await status(); const b = brief(s);
    if (b !== last) { console.log(new Date().toISOString().slice(11, 19), b); last = b; }
    if (healthy(s.stack)) { console.log("healthy"); await client.close(); process.exit(0); }
    await new Promise((r) => setTimeout(r, 15_000));
  }
  console.log("timeout"); await client.close(); process.exit(1);
} else if (cmd === "release") {
  const ref = arg ?? "orca";
  const inv = await call("inventory_get", {}) as { assets: Array<{ id: string; name: string; facts: Record<string, string>; tags: string[] }> };
  const existing = inv.assets.find((a) => a.name === STACK);
  const asset = await call("asset_upsert", { ...(existing ? { id: existing.id } : {}), kind: "service", name: STACK, facts: { ...(existing?.facts ?? {}), stack: STACK, dir: `${STACKS_DIR}/${STACK}`, repo: REPO, ref, mcp: "http://overstack-mcp:8791/mcp" }, tags: [...new Set([...(existing?.tags ?? []), "mcp", "stack"])] });
  console.log("asset:", JSON.stringify(asset).slice(0, 300));
  const rel = await call("flow_run", { name: "stack_release", params: { asset: STACK } }) as { ok?: boolean; steps?: Array<{ tool: string; status: string; output?: unknown; error?: string }> };
  for (const st of rel.steps ?? []) console.log(`${st.status === "ok" ? "✔" : "…"} ${st.tool} ${st.status}  ${JSON.stringify(st.output ?? st.error ?? "").slice(0, 600)}`);
  console.log(brief(await status()));
} else {
  console.error(`unknown command ${cmd}; use release [ref] | status | wait [sec]`); process.exit(2);
}
await client.close();
