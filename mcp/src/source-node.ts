/** Source đọc đĩa (Node/Docker): repo setup hoặc bản global, skill ở OVERSTACK_SKILLS_ROOT > catalog.skillsRoot > <root>/skills. */
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { harnessVersion, OVERSTACK_ROOT, skillsRootDir } from "./catalog.ts";
import type { Catalog, CatalogSkill } from "./catalog.ts";
import { HEAD_CHARS } from "./source.ts";
import type { SkillHead, Source } from "./source.ts";

export class NodeSource implements Source {
  constructor(private readonly root: string = OVERSTACK_ROOT, private readonly cat?: Catalog) {}
  skillPath(skill: CatalogSkill): string {
    return skill.path.startsWith("skills/") ? join(this.root, skill.path) : join(skillsRootDir(this.cat, this.root), skill.path);
  }
  async read(rel: string): Promise<string | null> {
    const p = join(this.root, rel);
    return existsSync(p) ? readFileSync(p, "utf8") : null;
  }
  /** Đọc lúc gọi, không cache: skill đổi trên đĩa thì prompt đổi theo. */
  async skillBody(skill: CatalogSkill): Promise<string> {
    return readFileSync(this.skillPath(skill), "utf8");
  }
  async skillHeads(): Promise<SkillHead[]> {
    return (this.cat?.skills ?? []).map((s) => {
      let head = "";
      try { head = readFileSync(this.skillPath(s), "utf8").slice(0, HEAD_CHARS); } catch { head = ""; }
      return { name: s.name, head };
    });
  }
  async harnessVersion(): Promise<string | null> { return harnessVersion(this.root); }
}
