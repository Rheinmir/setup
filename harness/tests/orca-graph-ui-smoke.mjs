// orca-graph-ui-smoke — thẻ test 5 bước cho control-room + daemon, chạy THẬT bằng Playwright
// (standalone .mjs theo /playwright-verify, không qua test runner). Mỗi bước in PASS/FAIL + lý do.
//   NODE_PATH=$(npm root -g) node harness/tests/orca-graph-ui-smoke.mjs
// Dựng 2 "dự án" trong thư mục tạm, ORCA_GRAPH_HOME riêng → không đụng registry/daemon thật.
import { createRequire } from 'node:module';
// playwright nằm ở <repo>/scratchpad/node_modules (do /playwright-verify cài) hoặc global (NODE_PATH) — thử lần lượt
const _req = createRequire(new URL('../../scratchpad/_.js', import.meta.url));
const { chromium } = (() => { try { return _req('playwright'); } catch { return createRequire(import.meta.url)('playwright'); } })();
import { spawn, spawnSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';

const ROOT = resolve(new URL('../..', import.meta.url).pathname);
const OG = join(ROOT, 'harness/scripts/orca-graph.py');
const ROOM = join(ROOT, 'fdk/tools/build-control-room.py');
const VIZ = join(ROOT, 'fdk/tools/graph-viz.py');
const T = mkdtempSync(join(tmpdir(), 'og-ui-'));
const HOME = join(T, 'home');
const env = { ...process.env, ORCA_GRAPH_HOME: HOME };
const PLAN = `# X
### Task 1: A
**Files:**
- Tạo: \`a.py\`
**Interfaces:**
- Consumes: —
- Produces: \`fa()\`
**Verify:** \`true\`
### Task 2: B
**Files:**
- Sửa: \`b.py\`
**Interfaces:**
- Consumes: \`fa()\`
- Produces: \`fb()\`
**Depends:** Task 1
**Verify:** \`true\`
`;
const results = [];
const step = (n, ok, why) => { results.push([n, ok, why]); console.log(`${ok ? 'PASS' : 'FAIL'} ${n}${why ? ' — ' + why : ''}`); };
const py = (args, opts = {}) => spawnSync('python3', args, { cwd: ROOT, env, encoding: 'utf8', ...opts });
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

for (const p of ['p1', 'p2']) { mkdirSync(join(T, p, 'html', 'orca-graph'), { recursive: true }); writeFileSync(join(T, p, 'job-PLAN.md'), PLAN); }
const D1 = join(T, 'p1'), D2 = join(T, 'p2'), OUT = join(T, 'control-room.html');
writeFileSync(join(D2, 'job-PLAN.md'), PLAN.replace('**Verify:** `true`', '**Verify:** `false`'));   // p2: verify fail → reconcile trả về ready
py([OG, '--dir', D1, 'build', join(D1, 'job-PLAN.md')]); py([OG, '--dir', D2, 'build', join(D2, 'job-PLAN.md')]);
py([VIZ, join(D1, 'job.graph.json'), '-o', join(D1, 'html/orca-graph/job.graph.html')]);
const room = () => py([ROOM, '--dirs', D1, D2, '-o', OUT]);

const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1380, height: 900 } });
const errs = []; pg.on('pageerror', e => errs.push(e.message)); pg.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
const open = async () => { room(); await pg.goto('file://' + OUT); await pg.waitForTimeout(200); };

// 1. Mở trang: 4 mục sidebar, bảng "Đang chạy" trống, daemon chưa chạy
await open();
const nav = await pg.locator('nav a').allTextContents();
step('1 mở trang', ['Đang chạy', 'Tiến độ', 'Nợ mở', 'Hôm nay'].every(x => nav.includes(x)) && (await pg.locator('text=Không có node nào đang chạy').count()) === 1,
  `sidebar=${nav.slice(0, 4).join('/')}`);

// 2. run 1 node headless → hàng hiện với lease + daemon pid
const a1 = spawn('python3', [OG, '--dir', D1, 'run', 'job', 't1', '--hb', '1', '--lease-sec', '3', '--', 'sh', '-c', 'sleep 25'], { cwd: ROOT, env, stdio: 'ignore' });
await sleep(2500); await open();
const row1 = pg.locator('.p-run table, table').first().locator('tr', { hasText: 'p1/job' });
const lease1 = (await row1.textContent()) || '';
step('2 run 1 node', (await row1.count()) === 1 && /đã giao/.test(lease1) && /\d+ s/.test(lease1) && /daemon\s*pid \d+/.test(await pg.textContent('body')),
  lease1.replace(/\s+/g, ' ').slice(0, 90));

// 3. phiên 2, dự án khác → 2 hàng, 2/4, chỉ 1 daemon
const a2 = spawn('python3', [OG, '--dir', D2, 'run', 'job', 't1', '--hb', '1', '--lease-sec', '3', '--', 'sh', '-c', 'sleep 25'], { cwd: ROOT, env, stdio: 'ignore' });
await sleep(2500); await open();
const rows = await pg.locator('.p-run table, table').first().locator('tr:has-text("đã giao")').count();
const badge = await pg.locator('h2#chay .badge').textContent();
const pids = readFileSync(join(HOME, 'daemon.lock'), 'utf8').trim();
step('3 đa phiên', rows === 2 && badge.trim() === '2/4' && /^\d+$/.test(pids), `rows=${rows} badge=${badge.trim()} daemon=${pids}`);

// 4. giết agent giữa chừng (pkill -f giết cả wrapper vì dòng lệnh chứa 'sleep 25' → đúng ca agent chết không kịp báo)
//    → lease 3 s hết → reaper đưa về unknown → có verify thì reconcile ngay: p1 (true) → done, p2 (false) → ready
spawnSync('pkill', ['-f', 'sleep 25']);
await sleep(4000);
const w = py([OG, 'watch', '--once']).stdout;
await open();
const prog = (await pg.locator('.p-prog table, h2#tien-do ~ table').first().textContent()).replace(/\s+/g, ' ');
step('4 giết agent', /reconcile p1\/job\/t1 → done|reconcile job\/t1 → done/.test(w) && /p1\/job 1\/2/.test(prog) && /p2\/job 0\/2/.test(prog),
  `watch: ${(w.match(/reconcile.*/g) || []).join(' | ')} · ${prog.slice(0, 80)}`);

// 5. bấm xuyên trang: link graph → trang chi tiết → bấm node → thẻ; gạt theme rồi quay lại vẫn dark
await pg.locator('a:has-text("job")').first().click();
await pg.waitForTimeout(300);
await pg.click('svg .node[data-id="t1"]'); await pg.waitForTimeout(200);
const card = await pg.locator('#node-inspector').textContent();
await pg.click('.theme-switch'); await pg.waitForTimeout(150);
const isDark = await pg.evaluate(() => document.documentElement.getAttribute('data-theme'));
step('5 bấm xuyên trang', /t1 — A/.test(card) && isDark === 'dark' && errs.length === 0, `card="${card.slice(0, 20)}…" theme=${isDark} errs=${errs.length}`);

await b.close();
for (const p of [a1, a2]) { try { p.kill('SIGKILL'); } catch {} }
try { const pid = +readFileSync(join(HOME, 'daemon.lock'), 'utf8'); if (pid) process.kill(pid, 'SIGKILL'); } catch {}
rmSync(T, { recursive: true, force: true });
const fails = results.filter(r => !r[1]).length;
console.log(`— ${results.length - fails}/${results.length} bước PASS`);
process.exit(fails ? 1 : 0);
