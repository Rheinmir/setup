/**
 * Lái deploy overstack-mcp qua MCP của devops-agent (không ssh, không rsync):
 *   DEVOPS_AGENT_URL=http://<host>:8787/mcp DEVOPS_AGENT_TOKEN=… npx tsx scripts/devops-release.ts release [ref]
 *       → asset_upsert (kind service, name overstack-mcp, facts repo/ref/stack/dir) rồi flow_run stack_release
 *         (hostops_stack_fetch: git fetch ref vào /home/rhein/stacks/overstack-mcp, tạo thư mục lần đầu;
 *          hostops_stack_deploy: docker compose up -d --build). Hai lệnh ghi của flow LUÔN chờ người duyệt trên web UI
 *          (mỗi approval hết hạn sau 15 phút); release không chặn: phát flow rồi poll status + approvals tới healthy (RELEASE_WAIT s).
 *   … devops-release.ts status      → flow stacks_list + stack_source cho stack overstack-mcp (state, health, sha đang chạy)
 *   … devops-release.ts wait [sec]  → poll status tới khi service healthy (mặc định 900 s), in approval đang chờ; rc 0/1
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

interface Approval { id: string; action: string; detail: string; status: string; createdAt: string; decidedAt?: string }
/**
 * APPROVE=yes: tự duyệt approval của STACK qua REST `POST /api/approvals/:id` (cùng bearer; MCP cố ý không lộ approval_decide).
 * Chỉ dùng khi người vận hành đã đồng ý trước cho đúng lần release này — approval hết hạn sau 15 phút nếu không ai bấm trên web UI.
 */
const AUTO_APPROVE = process.env.APPROVE === "yes";
async function approve(id: string): Promise<void> {
  const origin = new URL(URL_!).origin;
  const r = await fetch(`${origin}/api/approvals/${id}`, { method: "POST", headers: { authorization: `Bearer ${TOKEN}`, "content-type": "application/json" }, body: JSON.stringify({ approve: true }) });
  if (!r.ok) throw new Error(`approve ${id}: HTTP ${r.status} ${(await r.text()).slice(0, 200)}`);
}
/** Approval của devops-agent liên quan tới STACK (fetch/deploy), mới nhất trước; hết hạn sau 15 phút nếu không ai duyệt. */
async function approvals(): Promise<Approval[]> {
  const r = await client.callTool({ name: "approvals_list", arguments: {} }, undefined, { timeout: 60_000 });
  let rows: Approval[] = [];
  try { rows = JSON.parse(txt(r)) as Approval[]; } catch { rows = []; }
  return rows.filter((a) => a.detail.includes(`"stack":"${STACK}"`));
}
/** Poll tới khi stack healthy; in approval pending (người duyệt trên web UI) và dừng rc 1 nếu approval mới nhất hết hạn/bị từ chối. */
async function waitHealthy(seconds: number, since: number): Promise<never> {
  const deadline = Date.now() + seconds * 1000;
  let last = "";
  while (Date.now() < deadline) {
    const s = await status(); let ap = (await approvals()).filter((a) => Date.parse(a.createdAt) >= since);
    if (AUTO_APPROVE) {
      for (const a of ap.filter((x) => x.status === "pending")) { await approve(a.id); console.log(`  ✔ đã duyệt ${a.action} id=${a.id} (APPROVE=yes, người vận hành đã đồng ý trước)`); }
      if (ap.some((x) => x.status === "pending")) ap = (await approvals()).filter((a) => Date.parse(a.createdAt) >= since);
    }
    const pend = ap.filter((a) => a.status === "pending").map((a) => `  ⏳ chờ duyệt ${a.action} id=${a.id} (hạn 15 phút từ ${a.createdAt.slice(11, 19)}Z)`);
    const b = [brief(s), ...pend].join("\n");
    if (b !== last) { console.log(new Date().toISOString().slice(11, 19), b); last = b; }
    if (healthy(s.stack)) { console.log("healthy"); await client.close(); process.exit(0); }
    const dead = ap.find((a) => a.status === "expired" || a.status === "rejected");
    if (dead && !pend.length && !healthy(s.stack)) { console.log(`approval ${dead.id} ${dead.status} → chạy lại: devops-release.ts release <ref>`); await client.close(); process.exit(1); }
    await new Promise((r) => setTimeout(r, 15_000));
  }
  console.log("timeout"); await client.close(); process.exit(1);
}
const brief = (s: { stack?: StackRow; source?: Record<string, unknown> }) => s.stack
  ? `${STACK}: ${s.stack.services?.map((x) => `${x.service}=${x.state}${x.health ? `/${x.health}` : ""}${x.ports.length ? ` ${x.ports.join(",")}` : ""}`).join(" · ") || "(no services yet)"}  env=${s.stack.hasEnv} compose=${s.stack.composeFile}  src=${JSON.stringify(s.source ?? {}).slice(0, 300)}`
  : `${STACK}: not staged under ${STACKS_DIR}`;

if (cmd === "status") {
  console.log(brief(await status()));
} else if (cmd === "wait") {
  await waitHealthy(Number(arg ?? 900), Date.now() - 3_600_000);
} else if (cmd === "release") {
  const ref = arg ?? "orca";
  const inv = await call("inventory_get", {}) as { assets: Array<{ id: string; name: string; facts: Record<string, string>; tags: string[] }> };
  const existing = inv.assets.find((a) => a.name === STACK);
  const asset = await call("asset_upsert", { ...(existing ? { id: existing.id } : {}), kind: "service", name: STACK, facts: { ...(existing?.facts ?? {}), stack: STACK, dir: `${STACKS_DIR}/${STACK}`, repo: REPO, ref, mcp: "http://overstack-mcp:8791/mcp" }, tags: [...new Set([...(existing?.tags ?? []), "mcp", "stack"])] });
  console.log("asset:", JSON.stringify(asset).slice(0, 300));
  // flow_run chặn phía server tới khi người duyệt (tối đa 15 phút) — lâu hơn trần 300 s headers của fetch trong Node,
  // nên KHÔNG await kết quả: flow vẫn chạy trên server khi client ngắt; theo tiến độ bằng poll status + approvals.
  const since = Date.now() - 5_000;
  void call("flow_run", { name: "stack_release", params: { asset: STACK } })
    .then((rel) => { for (const st of (rel as { steps?: Array<{ tool: string; status: string; output?: unknown; error?: string }> }).steps ?? []) console.log(`${st.status === "ok" ? "✔" : "…"} ${st.tool} ${st.status}  ${JSON.stringify(st.output ?? st.error ?? "").slice(0, 600)}`); })
    .catch((e: Error) => console.log(`(flow_run: ${e.message.slice(0, 120)} — flow vẫn chạy phía server, tiếp tục poll)`));
  await waitHealthy(Number(process.env.RELEASE_WAIT ?? 1800), since);
} else {
  console.error(`unknown command ${cmd}; use release [ref] | status | wait [sec]`); process.exit(2);
}
await client.close();
