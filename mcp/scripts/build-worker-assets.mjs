#!/usr/bin/env node
/**
 * Gom static assets cho Worker (mode read) vào mcp/worker/assets/ — Workers không có đĩa, mọi thứ server đọc phải nằm ở đây:
 *   catalog.json          (bỏ đường tuyệt đối của máy sinh)
 *   skills/<path>         SKILL.md của mọi skill trong catalog (đọc từ OVERSTACK_SKILLS_ROOT > catalog.skillsRoot > <root>/skills)
 *   skills-index.json     [{name, head}] — 4000 ký tự đầu mỗi SKILL.md cho skill_find (1 fetch thay vì 106)
 *   harness/version.json · harness/policy.yaml · fdk/CAPABILITIES.md · validator .py của từng rule
 * Thiếu một skill là lỗi (exit 1): không được deploy catalog hứa 106 mà assets có 100.
 *   node scripts/build-worker-assets.mjs [--out worker/assets] [--catalog catalog.json]
 */
import { copyFileSync, existsSync, mkdirSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const MCP = resolve(HERE, "..");
const ROOT = resolve(process.env.OVERSTACK_ROOT ?? join(MCP, ".."));
const argv = process.argv.slice(2);
const arg = (k, d) => (argv.includes(k) ? argv[argv.indexOf(k) + 1] : d);
const OUT = resolve(MCP, arg("--out", "worker/assets"));
const CATALOG = resolve(MCP, arg("--catalog", "catalog.json"));
const HEAD_CHARS = 4000;

const cat = JSON.parse(readFileSync(CATALOG, "utf8"));
if (cat.schemaVersion !== 1) throw new Error(`catalog schemaVersion ${cat.schemaVersion} unsupported`);
const skillsRoot = process.env.OVERSTACK_SKILLS_ROOT ?? (cat.skillsRoot && existsSync(cat.skillsRoot) ? cat.skillsRoot : join(ROOT, "skills"));

rmSync(OUT, { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });
let files = 0, bytes = 0;
const put = (rel, text) => { const p = join(OUT, rel); mkdirSync(dirname(p), { recursive: true }); writeFileSync(p, text); files++; bytes += Buffer.byteLength(text); };
const copy = (rel, from) => { const p = join(OUT, rel); mkdirSync(dirname(p), { recursive: true }); copyFileSync(from, p); files++; bytes += statSync(from).size; };

// catalog: giữ nguyên nội dung, bỏ đường máy sinh (skillsRoot tuyệt đối) — Worker không dùng và không nên công bố
const pub = { ...cat, skillsRoot: undefined };
put("catalog.json", JSON.stringify(pub));

const missing = [], heads = [];
for (const s of cat.skills) {
  const src = s.path.startsWith("skills/") ? join(ROOT, s.path) : join(skillsRoot, s.path);
  if (!existsSync(src)) { missing.push(`${s.name} → ${src}`); continue; }
  const rel = s.path.startsWith("skills/") ? s.path : `skills/${s.path}`;
  const body = readFileSync(src, "utf8");
  put(rel, body);
  heads.push({ name: s.name, head: body.slice(0, HEAD_CHARS) });
}
if (missing.length) { console.error(`✗ ${missing.length} skill trong catalog không có trên đĩa (skills root ${skillsRoot}):\n  ` + missing.slice(0, 10).join("\n  ")); process.exit(1); }
put("skills-index.json", JSON.stringify(heads));

for (const rel of ["harness/version.json", "harness/policy.yaml", "fdk/CAPABILITIES.md"]) {
  const p = join(ROOT, rel);
  if (existsSync(p)) copy(rel, p); else console.warn(`⚠ thiếu ${rel} — resource tương ứng sẽ báo missing`);
}
let validators = 0;
for (const r of cat.rules) {
  if (!r.validatorPath) continue;
  const p = join(ROOT, r.validatorPath);
  if (existsSync(p)) { copy(r.validatorPath, p); validators++; }
}
const ver = JSON.parse(readFileSync(join(ROOT, "harness", "version.json"), "utf8")).template_version;
console.log(`→ ${OUT}: ${files} file · ${(bytes / 1024).toFixed(0)} KiB · ${cat.skills.length} skill (root ${skillsRoot}) · ${validators} validator · harness ${ver} · skills ${cat.skillsVersion?.version ?? "?"}`);
