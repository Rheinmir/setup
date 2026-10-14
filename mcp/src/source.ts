/**
 * Nguồn ĐỌC file của server (skill body, policy, CAPABILITIES, validator) tách khỏi `node:fs` để cùng một lõi chạy được
 * hai nơi: Node/Docker (NodeSource trong source-node.ts) và Cloudflare Workers (AssetsSource — static assets, không có đĩa).
 * Không import gì của Node ở file này: nó đi vào bundle Worker.
 */
import type { CatalogSkill } from "./catalog.ts";

export interface SkillHead { name: string; head: string }

export interface Source {
  /** Một file tương đối gốc repo setup (fdk/CAPABILITIES.md, harness/policy.yaml, harness/validators/x.py); null nếu không có. */
  read(rel: string): Promise<string | null>;
  skillBody(skill: CatalogSkill): Promise<string>;
  /** Phần đầu SKILL.md của mọi skill cho BM25 (skill_find). Worker đọc một file chỉ mục tính sẵn lúc build (giới hạn 50 subrequest/request). */
  skillHeads(): Promise<SkillHead[]>;
  harnessVersion(): Promise<string | null>;
}

export const HEAD_CHARS = 4000;

/** Đường của SKILL.md trong cây assets: skill.path tương đối skills root (từ 141026) hoặc dạng cũ `skills/x/SKILL.md`. */
export function skillRel(skill: CatalogSkill): string {
  return skill.path.startsWith("skills/") ? skill.path : `skills/${skill.path}`;
}

/** Binding ASSETS của Workers (hoặc bất kỳ thứ gì có fetch(URL)). */
export interface AssetFetcher { fetch(input: URL | string | Request): Promise<Response> }

export class AssetsSource implements Source {
  private heads?: Promise<SkillHead[]>;
  constructor(private readonly assets: AssetFetcher, private readonly origin: string) {}
  async read(rel: string): Promise<string | null> {
    const r = await this.assets.fetch(new URL("/" + rel.replace(/^\/+/, ""), this.origin));
    return r.ok ? r.text() : null;
  }
  async skillBody(skill: CatalogSkill): Promise<string> {
    const t = await this.read(skillRel(skill));
    if (t == null) throw new Error(`skill ${skill.name} missing in assets (${skillRel(skill)}) — rebuild: npm run worker:assets`);
    return t;
  }
  skillHeads(): Promise<SkillHead[]> {
    this.heads ??= this.read("skills-index.json").then((t) => (t ? (JSON.parse(t) as SkillHead[]) : []));
    return this.heads;
  }
  async harnessVersion(): Promise<string | null> {
    try { return String(JSON.parse((await this.read("harness/version.json")) ?? "{}").template_version ?? null); } catch { return null; }
  }
}

/** So token thời gian cố định, không cần node:crypto (Workers không có Buffer nếu thiếu nodejs_compat). */
export function sameToken(a: string | undefined, b: string): boolean {
  if (!a || a.length !== b.length) return false;
  const x = new TextEncoder().encode(a), y = new TextEncoder().encode(b);
  if (x.length !== y.length) return false;
  let d = 0;
  for (let i = 0; i < x.length; i++) d |= x[i]! ^ y[i]!;
  return d === 0;
}
