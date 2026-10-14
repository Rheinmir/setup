/**
 * Catalog của overstack: skill, rule, tool — đọc từ `mcp/catalog.json` do `scripts/gen-catalog.py` sinh từ đĩa.
 * Server chỉ phục vụ những gì có trong catalog; thêm skill/script vào repo → chạy lại generator, không sửa code.
 */
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

export interface CatalogSkill {
  name: string; dir: string; path: string; external: boolean; group: string; description: string; modelInvocable: boolean; bytes: number;
}
export interface CatalogRule {
  id: string; name: string | null; validator: string | null; validatorPath: string | null; statement: string;
  enforce_at: string[]; applies_to: string[]; scope: string | null;
}
export interface CatalogToolOption { flags: string[]; metavar: string | null; help: string }
export interface CatalogTool {
  name: string; file: string; kind: "harness-script" | "fdk-tool" | "validator"; path: string; runner: "python3" | "node" | "bash";
  summary: string; usage: string | null; options: CatalogToolOption[]; positionals: Array<{ name: string; help: string }>;
  help: string | null; helpRc: number | null; stdinJson: boolean;
}
export interface SkillsVersion { version: string | null; catalog_sha: string | null; count: number | null }
export interface Catalog { schemaVersion: number; root: string; skillsRoot?: string; skillsVersion?: SkillsVersion; skills: CatalogSkill[]; rules: CatalogRule[]; tools: CatalogTool[] }

const HERE = dirname(fileURLToPath(import.meta.url));
/** Gốc repo overstack: OVERSTACK_ROOT, hoặc thư mục cha của mcp/ (layout repo). */
export const OVERSTACK_ROOT = resolve(process.env.OVERSTACK_ROOT ?? join(HERE, "..", ".."));
export const CATALOG_PATH = join(OVERSTACK_ROOT, "mcp", "catalog.json");

export function loadCatalog(path = CATALOG_PATH): Catalog {
  if (!existsSync(path)) throw new Error(`catalog not found at ${path} — run: python3 mcp/scripts/gen-catalog.py`);
  const cat = JSON.parse(readFileSync(path, "utf8")) as Catalog;
  if (cat.schemaVersion !== 1) throw new Error(`catalog schemaVersion ${cat.schemaVersion} unsupported (want 1)`);
  return cat;
}

/** Nội dung SKILL.md của một skill (đọc lúc gọi, không cache: skill đổi trên đĩa thì prompt đổi theo). */
/** Thư mục skill lúc chạy: OVERSTACK_SKILLS_ROOT (Docker /opt/skills/skills) > catalog.skillsRoot (máy sinh catalog) > <root>/skills. */
export function skillsRootDir(cat: Catalog | undefined, root = OVERSTACK_ROOT): string {
  const env = process.env.OVERSTACK_SKILLS_ROOT;
  if (env) return env;
  if (cat?.skillsRoot && existsSync(cat.skillsRoot)) return cat.skillsRoot;
  return join(root, "skills");
}

export function skillBody(skill: CatalogSkill, root = OVERSTACK_ROOT, cat?: Catalog): string {
  // skill.path tương đối skills root (từ 141026: repo Rheinmir/skills); bản cũ `skills/x/SKILL.md` tương đối repo setup
  const p = skill.path.startsWith("skills/") ? join(root, skill.path) : join(skillsRootDir(cat, root), skill.path);
  return readFileSync(p, "utf8");
}

/** template_version của harness (repo setup hoặc bản global) — /healthz công bố để dev so bản. */
export function harnessVersion(root = OVERSTACK_ROOT): string | null {
  for (const p of [join(root, "harness", "version.json"), join(process.env.HOME ?? "", ".claude", "harness", "version.json")]) {
    try { return String(JSON.parse(readFileSync(p, "utf8")).template_version ?? null); } catch { /* thử đường kế */ }
  }
  return null;
}

export function findSkill(cat: Catalog, name: string): CatalogSkill | undefined {
  const n = name.replace(/^\//, "").toLowerCase();
  return cat.skills.find((s) => s.name.toLowerCase() === n || s.dir.toLowerCase() === n);
}
export function findRule(cat: Catalog, ref: string): CatalogRule | undefined {
  const r = ref.toUpperCase();
  return cat.rules.find((x) => x.id.toUpperCase() === r || (x.name ?? "").toLowerCase() === ref.toLowerCase() || (x.validator ?? "") === ref);
}
export function findTool(cat: Catalog, name: string): CatalogTool | undefined {
  const n = name.toLowerCase().replace(/\.(py|sh|mjs)$/, "");
  return cat.tools.find((t) => t.name.toLowerCase() === n) ?? cat.tools.find((t) => t.file.toLowerCase() === name.toLowerCase());
}

// ── skill_find: BM25 giống fdk/tools/build-skill-search.py (k1 1.5, b 0.75) trên name + description + phần đầu body ──
const STOP = new Set("a an the and or of to in on for with is are be this that it as at by from into về của và cho với là có một các khi để từ trong".split(" "));
export function tokenize(text: string): string[] {
  return text.toLowerCase().normalize("NFC").split(/[^\p{L}\p{N}_-]+/u).filter((t) => t.length > 1 && !STOP.has(t));
}
export interface SkillHit { name: string; score: number; group: string; description: string; modelInvocable: boolean }
export function searchSkills(cat: Catalog, query: string, k = 5, root = OVERSTACK_ROOT): SkillHit[] {
  const docs = cat.skills.map((s) => {
    let body = "";
    try { body = skillBody(s, root, cat).slice(0, 4000); } catch { body = ""; }
    return { s, toks: tokenize(`${s.name} ${s.name.replace(/-/g, " ")} ${s.description} ${body}`) };
  });
  const N = docs.length, avgdl = docs.reduce((a, d) => a + d.toks.length, 0) / Math.max(1, N);
  const df = new Map<string, number>();
  for (const d of docs) for (const t of new Set(d.toks)) df.set(t, (df.get(t) ?? 0) + 1);
  const q = tokenize(query);
  const k1 = 1.5, b = 0.75;
  const scored = docs.map((d) => {
    const tf = new Map<string, number>();
    for (const t of d.toks) tf.set(t, (tf.get(t) ?? 0) + 1);
    let score = 0;
    for (const t of q) {
      const f = tf.get(t) ?? 0;
      if (!f) continue;
      const idf = Math.log(1 + (N - (df.get(t) ?? 0) + 0.5) / ((df.get(t) ?? 0) + 0.5));
      score += idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * d.toks.length / avgdl));
    }
    return { name: d.s.name, score: Math.round(score * 1000) / 1000, group: d.s.group, description: d.s.description, modelInvocable: d.s.modelInvocable };
  });
  return scored.filter((x) => x.score > 0).sort((a, b2) => b2.score - a.score).slice(0, k);
}
