#!/usr/bin/env python3
"""skill-health — soi hình dạng mọi skill bằng CODE, không nhờ model nhớ (0 token).

Đo 5 mục theo concept skill-craft (wiki/concepts/skill-craft.md). Một dữ kiện
("skill này 340 dòng, 0 completion criterion, 61% câu cấm") đổi được hành vi;
một lời khuyên ("hãy viết gọn") thì không.

BÁO CÁO, KHÔNG CHẶN — đây là chất lượng, không phải an toàn. Exit luôn 0 trừ khi
--ci và có skill vượt ngưỡng CỨNG (chỉ để CI cảnh báo, mặc định vẫn không chặn).

Đo:
  1. context load — tổng token description của skill CÒN model-invoked
  2. completion criterion — bước '### Task'/'N.' không có điều kiện kiểm được ở cuối
  3. negation — tỉ lệ câu cấm (KHÔNG/đừng/cấm/never/don't) trên tổng câu
  4. sprawl — SKILL.md > ngưỡng dòng mà không có progressive disclosure (không link file .md khác)
  5. duplication — description gần trùng nhau giữa các skill (chớm — chỉ cảnh báo cặp giống >0.8)

Dùng:
  python3 harness/scripts/skill-health.py                 # bảng xếp hạng, exit 0
  python3 harness/scripts/skill-health.py --json          # máy đọc
  python3 harness/scripts/skill-health.py --skills-dir X  # mặc định ./skills
"""
import argparse
import glob
import json
import os
import re
import sys
from difflib import SequenceMatcher

# ngưỡng — chọn theo phân bố hiện tại, chỉnh được (SPEC 150726 Assumptions)
DESC_CHARS_WARN = 400        # description dài hơn → cân nhắc rút
LINES_WARN = 200             # SKILL.md dài hơn mà không disclosure → sprawl
NEGATION_WARN = 0.45         # >45% câu là câu cấm → nặng negation (guardrail-skill vốn cao, ngưỡng phải thật cao mới là tín hiệu)
TOTAL_TOKEN_WARN = 6000      # tổng context load model-invoked vượt → cảnh báo

NEG_RE = re.compile(r"\b(KHÔNG|ĐỪNG|đừng|không|cấm|CẤM|never|don't|do not|must not|chớ)\b", re.IGNORECASE)
# câu hoàn thành thường có completion criterion nếu chứa các dấu hiệu "đến khi/xong/pass/exit/→"
DONE_HINT_RE = re.compile(r"(hoàn tất|đã xong|hết|PASS|exit 0|exit 2|→|đến khi|cho tới khi|until|verify|kiểm|assert)", re.IGNORECASE)
# CHỈ bước thi hành thật cần completion criterion: checklist '- [ ]' và '### Task/Step'.
# Danh sách prose đánh số (nguyên tắc thiết kế, tham chiếu) KHÔNG phải bước hành động —
# đếm chúng là biến lint thành máy kêu sói (đúng lỗi no-op mà skill-craft cảnh báo).
# Bước thi hành nhiều dòng cần "chạy X → mong đợi Y". Một checkbox '- [ ]' một dòng
# TỰ NÓ là điều kiện kiểm được (chính cái ô tick) → không tính là thiếu criterion.
STEP_RE = re.compile(r"^\s*### (?:Task|Bước|Step)", re.MULTILINE)
EXEC_STEP_RE = re.compile(r"^\s*### (?:Task|Bước|Step)[^\n]*\n(.*?)(?=^\s*### (?:Task|Bước|Step)|\Z)",
                          re.M | re.S)
DISCLOSURE_RE = re.compile(r"\]\([^)]+\.md\)|`[^`]+\.md`")  # link/nhắc tới file .md khác → có disclosure


def frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    return m.group(1) if m else ""


def field(fm, key):
    m = re.search(rf"^{key}:\s*(.*)$", fm, re.M)
    return m.group(1).strip() if m else ""


def description(text):
    m = re.search(r"^description:\s*(.*?)(?=^\w[\w-]*:|^---)", text, re.M | re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def analyze(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    fm = frontmatter(t)
    body = t[t.find("---", 3) + 3:] if t.startswith("---") else t
    disabled = re.search(r"disable-model-invocation:\s*true", fm) is not None
    desc = description(t)
    lines = t.count("\n") + 1
    sentences = [s for s in re.split(r"[.\n](?:\s|$)", body) if len(s.strip()) > 12]
    neg = sum(1 for s in sentences if NEG_RE.search(s))
    neg_ratio = neg / len(sentences) if sentences else 0.0
    has_disclosure = DISCLOSURE_RE.search(body) is not None
    # completion criterion: đếm bước không có dấu hiệu "done"
    steps = STEP_RE.findall(body)
    weak = sum(1 for m in EXEC_STEP_RE.finditer(body) if not DONE_HINT_RE.search(m.group(1)))
    flags = []
    if not disabled and len(desc) > DESC_CHARS_WARN:
        flags.append(f"desc {len(desc)}c")
    if lines > LINES_WARN and not has_disclosure:
        flags.append(f"sprawl {lines}d")
    if neg_ratio > NEGATION_WARN:
        flags.append(f"negation {neg_ratio:.0%}")
    if steps and weak:
        flags.append(f"weak-criterion {weak}/{len(steps)}")
    return {
        "name": os.path.basename(os.path.dirname(path)),
        "disabled": disabled,
        "desc_chars": len(desc),
        "desc_tokens": len(desc) // 4,
        "lines": lines,
        "neg_ratio": round(neg_ratio, 2),
        "weak_criteria": weak,
        "steps": len(steps),
        "flags": flags,
        "_desc": desc,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skills-dir", default="skills")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--ci", action="store_true")
    a = ap.parse_args()

    rows = [analyze(p) for p in sorted(glob.glob(os.path.join(a.skills_dir, "*", "SKILL.md")))]
    if not rows:
        print(f"skill-health: không thấy skill nào trong {a.skills_dir}/", file=sys.stderr)
        sys.exit(0)

    live = [r for r in rows if not r["disabled"]]
    total_tok = sum(r["desc_tokens"] for r in live)

    # duplication (chớm): cặp description giống > 0.8
    dups = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            if rows[i]["_desc"] and rows[j]["_desc"]:
                s = SequenceMatcher(None, rows[i]["_desc"][:200], rows[j]["_desc"][:200]).ratio()
                if s > 0.8:
                    dups.append((rows[i]["name"], rows[j]["name"], round(s, 2)))

    for r in rows:
        r.pop("_desc", None)

    if a.json:
        print(json.dumps({"total_model_invoked_tokens": total_tok, "n_disabled": len(rows) - len(live),
                          "skills": rows, "dup_pairs": dups}, ensure_ascii=False, indent=2))
        sys.exit(0)

    flagged = sorted([r for r in rows if r["flags"]], key=lambda r: len(r["flags"]), reverse=True)
    print(f"skill-health · {len(rows)} skill ({len(live)} model-invoked, {len(rows)-len(live)} tắt)")
    print(f"  context load model-invoked: ~{total_tok:,} token/lượt"
          + ("  ⚠ vượt ngưỡng" if total_tok > TOTAL_TOKEN_WARN else ""))
    if flagged:
        print(f"  {len(flagged)} skill có cờ (báo cáo, KHÔNG chặn):")
        for r in flagged:
            print(f"    {r['name']:<26} {' · '.join(r['flags'])}")
    else:
        print("  không skill nào vượt ngưỡng hình dạng.")
    if dups:
        print(f"  {len(dups)} cặp description chớm-trùng (>0.8): "
              + ", ".join(f"{x}↔{y}" for x, y, _ in dups[:5]))
    sys.exit(0)


if __name__ == "__main__":
    main()
