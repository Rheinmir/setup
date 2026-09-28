---
name: live-mcp-bridge
description: "Nối agent vào app web ĐANG MỞ qua một MCP server tự viết (stdio JSON-RPC, 0 dependency) + cầu HTTP/SSE localhost: agent đọc/ghi thẳng state (thiết kế, canvas, form, board…) trong tab dev, người dùng sửa tay thì agent đọc lại được, có validate + undo. Gọi khi user nói 'mcp cho app này', 'agent sửa trực tiếp trên app', 'live edit qua mcp', 'nối claude vào canvas/editor', 'mcp bridge', 'agent tạo component rồi tôi tự sửa', hoặc /live-mcp-bridge."
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: live-mcp-bridge

## WHAT

### Purpose và context
- **Purpose:** cho agent đọc/ghi thẳng state của một app web đang mở trong tab dev (thiết kế trên canvas, board, form, cây component…), còn người dùng vẫn sửa tay trên chính app đó. Agent luôn đọc được bản mới nhất, kể cả phần người vừa sửa.
- **Trigger:** "làm mcp cho app này", "agent tạo component rồi tôi tự edit", "nối claude vào canvas/editor đang mở", "live edit qua mcp". Hay gặp ngay sau khi app đã có đường "link/JSON cho agent" một chiều (agent sinh file → người mở), vì skill này biến đường đó thành hai chiều, sống.
- **Non-goals:** không deploy MCP lên remote/production; không đồng bộ nhiều người (CRDT, presence); không cài `@modelcontextprotocol/sdk` (3 method JSON-RPC tự viết là đủ); không dùng cho app không có state tuần tự hoá được thành JSON.

### Mental model
```
Claude Code ⇄ stdio JSON-RPC ⇄ mcp/server.mjs ⇄ HTTP 127.0.0.1:<port> ⇄ tab dev (EventSource + fetch)
   tools/call get_state            latest ← POST /doc (debounce, mỗi lần state đổi)
   tools/call set_state   ──SSE /events {id,state}──▶ validate → import (undo được) → POST /ack {id,ok,error}
```
Một process làm hai việc: nói MCP qua stdin/stdout với agent, và mở một cầu HTTP nhỏ cho tab app. Server chỉ giữ **bản state mới nhất tab gửi lên**, không lưu gì khác. App vẫn là nguồn chân lý: nó tự validate và tự import bằng đường replace sẵn có (có undo), rồi báo ok/lỗi về cho agent.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | state tuần tự hoá được | có | một object JSON đại diện cả tài liệu (vd `{frames, groups, theme}`) |
| In | validator | có | hàm `isValid(x)` phía client; chưa có thì viết (kiểm shape tối thiểu app dựa vào) |
| In | đường replace-cả-tài-liệu | có | hàm import/open-file sẵn có của app, tốt nhất là undo được |
| In | tài liệu định dạng cho agent | nên có | file md mô tả schema (vd `public/agent.md`) để tool `get_guide` trả về |
| Out | `mcp/server.mjs` + `.mcp.json` | có | server 0-dependency, đăng ký cho Claude Code |
| Out | hook client chỉ-bật-ở-dev | có | EventSource + POST state, gate theo `NODE_ENV`/env var |
| Out | bằng chứng e2e | có | script Playwright: set hợp lệ → hiện trên app; set sai → bị từ chối; get trả đúng bản vừa set |

### Rules và capabilities
- RULE-01 (MUST): stdout của server CHỈ chứa JSON-RPC (mỗi dòng một message). Mọi log đi `console.error`, nếu không Claude Code parse hỏng và ngắt server.
- RULE-02 (MUST): cầu HTTP bind `127.0.0.1`, CORS **allowlist** đúng origin dev (cả `localhost` lẫn `127.0.0.1`), không dùng `*`. POST JSON phải qua preflight nên trang lạ không đẩy được state vào app.
- RULE-03 (MUST): client validate state nhận về TRƯỚC khi import, rồi ack `{ok:false,error}` có câu sửa cụ thể. `set_state` chờ ack (timeout ~5 s) để agent biết thành công thật, không bắn-và-quên.
- RULE-04 (MUST): import đi qua đúng đường replace/undo sẵn có của app, không set state vòng ngoài. Người dùng phải bỏ được bản agent vừa đẩy.
- RULE-05 (MUST): client chỉ bật ở dev (hoặc khi env var được set). Bản build/production không được mở kết nối tới localhost.
- RULE-06 (SHOULD): chỉ POST state khi SSE đang mở, và tự thử kết nối lại thưa (~15 s) thay vì dùng retry 3 s của EventSource, để console dev không ngập `ERR_CONNECTION_REFUSED` khi không có phiên agent.
- Capabilities: sửa code app (một effect client), ghi 2 file mới, chạy app dev + Playwright để kiểm.

### Failure boundaries
- App không có state gom được về một JSON → **blocked**: báo user, đề xuất gom state trước (việc riêng).
- Không có đường replace/undo → **partial**: vẫn làm, nhưng import thẳng vào state và nói rõ người dùng không undo được.
- Cổng bridge đã bị chiếm (2 phiên Claude Code cùng lúc) → server log `EADDRINUSE` ra stderr, tool trả lỗi "No app is connected". Đây là giới hạn đã biết, ghi vào báo cáo cho user.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | judgment | codebase app | tìm 4 thứ: object state gộp, validator, hàm replace/import (+undo), tài liệu schema | 4 điểm neo `file:line` | thiếu state gộp → blocked |
| W02 | effect | template server | chép `mcp/server.mjs` (dưới), đổi `PORT`/`ORIGIN`/đường guide/tên tool cho khớp domain | server chạy được | — |
| W03 | effect | điểm neo W01 | thêm effect client dev-only (dưới) vào component giữ state | app tự nối cầu | typecheck đỏ → sửa |
| W04 | effect | — | `.mcp.json` ở root: `{"mcpServers":{"<app>":{"command":"node","args":["mcp/server.mjs"]}}}` | Claude Code thấy server sau khi restart | — |
| W05 | deterministic | app dev đang chạy | chạy script e2e Playwright (dưới) | 4 dòng kỳ vọng đều đúng | sai → sửa, tối đa 3 vòng rồi báo |
| W06 | judgment | kết quả | báo user: restart Claude Code + approve server, cách dùng, giới hạn (replace cả tài liệu, 1 phiên/cổng) | — | — |

**Template server (`mcp/server.mjs`, Node ≥18, 0 dependency):**
```js
import { createServer } from "node:http";
import { readFileSync } from "node:fs";
import { randomUUID } from "node:crypto";
import { createInterface } from "node:readline";

const PORT = Number(process.env.APP_BRIDGE_PORT ?? 3939);
const ORIGIN = process.env.APP_ORIGIN ?? "http://localhost:3000";
const ORIGINS = new Set([ORIGIN, ORIGIN.replace("localhost", "127.0.0.1")]);
const GUIDE = new URL("../public/agent.md", import.meta.url); // tài liệu schema cho agent
let latest = null; const clients = new Set(); const pending = new Map();
const log = (...a) => console.error("[app-mcp]", ...a); // RULE-01: không bao giờ ghi stdout

const readBody = (req) => new Promise((ok, bad) => { let s = ""; req.on("data", (c) => (s += c)); req.on("end", () => { try { ok(JSON.parse(s)); } catch (e) { bad(e); } }); });
const http = createServer(async (req, res) => {
  if (ORIGINS.has(req.headers.origin)) res.setHeader("Access-Control-Allow-Origin", req.headers.origin);
  res.setHeader("Access-Control-Allow-Headers", "content-type");
  if (req.method === "OPTIONS") return res.writeHead(204).end();
  if (req.method === "GET" && req.url === "/events") {
    res.writeHead(200, { "content-type": "text/event-stream", "cache-control": "no-cache", connection: "keep-alive" });
    res.write(": connected\n\n"); clients.add(res); req.on("close", () => clients.delete(res)); return;
  }
  if (req.method === "POST" && (req.url === "/doc" || req.url === "/ack")) {
    try { const b = await readBody(req); if (req.url === "/doc") latest = b; else pending.get(b.id)?.(b); return res.writeHead(204).end(); }
    catch { return res.writeHead(400).end(); }
  }
  res.writeHead(404).end();
});
http.on("error", (e) => log(`bridge not started on ${PORT}: ${e.message}`));
http.listen(PORT, "127.0.0.1");

function push(state) {
  if (!clients.size) return Promise.resolve({ ok: false, error: `No app is connected. Open ${ORIGIN}.` });
  const id = randomUUID();
  return new Promise((resolve) => {
    const t = setTimeout(() => { pending.delete(id); resolve({ ok: false, error: "The app did not answer within 5 s." }); }, 5000);
    pending.set(id, (ack) => { clearTimeout(t); pending.delete(id); resolve(ack); });
    for (const c of clients) c.write(`data: ${JSON.stringify({ id, design: state })}\n\n`);
  });
}

const TOOLS = [
  { name: "get_guide", description: "The document format. Read once before writing.", inputSchema: { type: "object", properties: {} } },
  { name: "get_design", description: "The document open in the app now, including the person's own edits. Read before changing it.", inputSchema: { type: "object", properties: {} } },
  { name: "set_design", description: "Replaces the document in the app. The person sees it at once and can undo. Send the whole document.",
    inputSchema: { type: "object", properties: { design: { type: "object" } }, required: ["design"] } },
];
const text = (t, isError = false) => ({ content: [{ type: "text", text: t }], ...(isError ? { isError } : {}) });
async function callTool(name, a) {
  if (name === "get_guide") return text(readFileSync(GUIDE, "utf8"));
  if (name === "get_design") return latest ? text(JSON.stringify(latest)) : text(`No app has reported yet. Open ${ORIGIN}.`, true);
  if (name === "set_design") { const ack = await push(typeof a?.design === "string" ? JSON.parse(a.design) : a?.design); return ack.ok ? text("Done.") : text(ack.error ?? "Rejected.", true); }
  return text(`Unknown tool ${name}`, true);
}
const send = (m) => process.stdout.write(JSON.stringify(m) + "\n");
createInterface({ input: process.stdin }).on("line", async (line) => {
  if (!line.trim()) return;
  let m; try { m = JSON.parse(line); } catch { return send({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } }); }
  const { id, method, params } = m; if (id === undefined) return; // notification
  try {
    let result;
    if (method === "initialize") result = { protocolVersion: params?.protocolVersion ?? "2025-06-18", capabilities: { tools: {} }, serverInfo: { name: "app", version: "0.1.0" } };
    else if (method === "ping") result = {};
    else if (method === "tools/list") result = { tools: TOOLS };
    else if (method === "tools/call") result = await callTool(params?.name, params?.arguments);
    else return send({ jsonrpc: "2.0", id, error: { code: -32601, message: `Method not found: ${method}` } });
    send({ jsonrpc: "2.0", id, result });
  } catch (e) { send({ jsonrpc: "2.0", id, result: text(String(e?.message ?? e), true) }); }
});
process.stdin.on("end", () => process.exit(0));
```

**Hook client (React, đặt trong component giữ state; `docRef` = ref tới state mới nhất, `isValid` = validator, `replaceDoc` = đường import undo được):**
```tsx
const BRIDGE = process.env.NEXT_PUBLIC_APP_BRIDGE ?? (process.env.NODE_ENV === "development" ? "http://127.0.0.1:3939" : "");
const bridgeOpen = useRef(false);
useEffect(() => {
  if (!BRIDGE) return;
  const post = (path: string, body: unknown) =>
    fetch(`${BRIDGE}${path}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) }).catch(() => {});
  let es: EventSource | null = null; let retry: ReturnType<typeof setTimeout> | undefined;
  const connect = () => {
    es = new EventSource(`${BRIDGE}/events`);
    es.onopen = () => { bridgeOpen.current = true; post("/doc", docRef.current); };
    es.onerror = () => { bridgeOpen.current = false; es?.close(); retry = setTimeout(connect, 15000); }; // RULE-06
    es.onmessage = (e) => {
      const { id, design } = JSON.parse(e.data);
      if (!isValid(design)) return void post("/ack", { id, ok: false, error: "Invalid document: <nói rõ field nào cần kiểm>" });
      replaceDoc(design); post("/ack", { id, ok: true });
    };
  };
  connect();
  return () => { bridgeOpen.current = false; clearTimeout(retry); es?.close(); };
}, []);
useEffect(() => {
  if (!BRIDGE) return;
  const t = setTimeout(() => bridgeOpen.current && fetch(`${BRIDGE}/doc`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(doc) }).catch(() => {}), 300);
  return () => clearTimeout(t);
}, [doc]);
```
Không phải React thì giữ nguyên ý: mở SSE một lần khi app sẵn sàng, POST state (debounce) mỗi lần nó đổi.

**Script e2e (W05)**, chạy bằng Playwright global như `/playwright-verify`: spawn `node mcp/server.mjs`, gửi `initialize` → `tools/list` → `set_design` khi CHƯA mở trang (kỳ vọng lỗi "No app is connected") → mở trang dev, đợi 3–4 s → `get_design` (có state) → `set_design` với state sai (kỳ vọng `isError`) → `set_design` state hợp lệ có một nhãn lạ → `page.getByText(nhãn).count() > 0` → `get_design` trả đúng bản vừa set.

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | conditional_required | app chưa có tài liệu schema cho agent | viết `public/agent.md` ngắn (kiểu phần tử, field bắt buộc, ví dụ) trước W02 | có sẵn → skip | W02 |
| B02 | user_optional | tài liệu lớn / sửa liên tục làm tốn token | thêm tool sửa-từng-phần (`add_item`, `update_item`…) áp patch rồi gọi cùng `push` | mặc định replace cả tài liệu | W05 |
| B03 | conditional_required | app có SSR / script chạy trước hydrate | tách lỗi hydration có sẵn khỏi lỗi của cầu: cầu chỉ chạy trong `useEffect` nên không gây mismatch | — | W05 |

### Validation và stopping
Máy kiểm: `typecheck` của app rc 0, bộ test sẵn có vẫn xanh, script e2e in đúng 4 kỳ vọng ở W05. Mắt kiểm: chụp ảnh sau `set_design` để xem state thật hiện ra. Tối đa 3 vòng sửa e2e, sau đó báo lại lỗi còn lại cho user thay vì vá tiếp.

### Examples
- **Positive:** M3E Canvas (Next.js, editor thiết kế Material 3) đã có `public/agent.md` + `isProject` + `arrive()` (import có nút giữ/bỏ). Thêm server + effect client + `.mcp.json`. E2E: set trước khi mở trang → "No editor is connected"; set sai → bị từ chối; set "Chi tiêu MCP" → hiện trên canvas; get trả `title: "Chi tiêu"`, 2 group. 722/722 test vẫn xanh.
- **Boundary/failure:** app giữ state rải trong 20 `useState` không có hàm gộp/replace → blocked ở W01, đề xuất gom state thành một object trước.
