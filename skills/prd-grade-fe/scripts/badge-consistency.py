#!/usr/bin/env python3
"""badge-consistency — trong MỘT file, các badge trạng thái phải cùng pattern (GH#164).

Badge = hàm/component tên có Badge|Status|Pill (render*Badge, StatusPill…) hoặc <span> pill-like
(rounded-* + px- + text-xs|text-[Npx]). Chữ ký = (marker icon|dot|none, rounded-*, có hằng token
ALL_CAPS_WITH_UNDERSCORE như STATUS_GLASS). Có ≥2 badge chung một chữ ký (đa số duy nhất) mà badge
khác lệch → in `file:line: …`, rc 1. Badge đơn lẻ / hoà phiếu → không flag. So khớp nội bộ file.

  badge-consistency.py <file|dir>...   rc 0 sạch · rc 1 có badge lệch
  badge-consistency.py --self-test
"""
import os, re, sys

EXTS = (".tsx", ".jsx", ".vue", ".html")
DECL = re.compile(r"^([ \t]*)(?:export\s+)?(?:default\s+)?(?:function|const|let)\s+(\w+)", re.M)
BADGE_NAME = re.compile(r"Badge|Status|Pill")
CLASS_STR = re.compile(r"""["'`]([^"'`\n]*)["'`]""")
ICON = re.compile(r"<(?:svg\b|i\b|[A-Z]\w*[^>]*/>)")
DOT = re.compile(r"""["'`][^"'`\n]*(?=[^"'`\n]*rounded-full)[^"'`\n]*\b(?:h|w|size)-(?:1|1\.5|2|2\.5)\b[^"'`\n]*["'`]""")
TOKEN = re.compile(r"\b[A-Z][A-Z0-9]*_[A-Z0-9_]+\b")
PILL = re.compile(r"\brounded-(?:full|md|lg|sm|xl)\b")
SPAN = re.compile(r"<span\b[^>]*\bclass(?:Name)?\s*=[^>]*>")


def signature(block):
    shape = next((PILL.search(c).group(0) for c in CLASS_STR.findall(block) if " px-" in " " + c and PILL.search(c)), None)
    if not shape:
        return None
    marker = "icon" if ICON.search(block) else "dot" if DOT.search(block) else "none"
    return (marker, shape, bool(TOKEN.search(block)))


def badges(text):
    """[(line, name, signature)]. ponytail: khối hàm kết thúc ở khai báo kế cùng/ít thụt lề (cap 60 dòng), không parse JSX thật."""
    lines = text.splitlines(keepends=True)
    offs = [0]
    for l in lines:
        offs.append(offs[-1] + len(l))
    lineof = lambda pos: next(i for i in range(len(offs)) if offs[i + 1] > pos) + 1
    decls = [(m.start(), len(m.group(1)), m.group(2)) for m in DECL.finditer(text)]
    out, covered = [], []
    for i, (pos, ind, name) in enumerate(decls):
        if not BADGE_NAME.search(name):
            continue
        end = next((p for p, ind2, _ in decls[i + 1:] if ind2 <= ind), len(text))
        ln = lineof(pos)
        end = min(end, offs[min(ln - 1 + 60, len(lines))])
        sig = signature(text[pos:end])
        covered.append((pos, end))
        if sig:
            out.append((ln, name, sig))
    for m in SPAN.finditer(text):
        tag = m.group(0)
        if any(a <= m.start() < b for a, b in covered) or not (PILL.search(tag) and " px-" in tag.replace('"', " ")
                                                               and re.search(r"\btext-(?:xs|\[\d+px\])", tag)):
            continue
        depth, j = 0, m.start()
        for t in re.finditer(r"<span\b|</span>", text[m.start():]):
            depth += 1 if t.group(0) == "<span" else -1
            if depth == 0:
                j = m.start() + t.end()
                break
        sig = signature(text[m.start():j or len(text)])
        if sig:
            out.append((lineof(m.start()), "<span>", sig))
    return sorted(out)


def describe(sig):
    return f"{sig[0]}, {sig[1]}, {'có' if sig[2] else 'không'} hằng token"


def check(path, text):
    found = badges(text)
    counts = {}
    for _, _, s in found:
        counts[s] = counts.get(s, 0) + 1
    if not counts:
        return []
    top = max(counts.values())
    majors = [s for s, c in counts.items() if c == top]
    if top < 2 or len(majors) != 1:
        return []
    major, msgs = majors[0], []
    for ln, name, s in found:
        if s != major:
            diff = [f"{k}: {a} ≠ {b}" for k, a, b in zip(("marker", "rounded", "token"), describe(s).split(", "), describe(major).split(", ")) if a != b]
            msgs.append(f"{path}:{ln}: badge lệch pattern so với {top} badge anh em ({name}: {'; '.join(diff)} — anh em: {describe(major)})")
    return msgs


def files(args):
    for a in args:
        if os.path.isdir(a):
            for root, _, fs in os.walk(a):
                if "node_modules" not in root:
                    yield from (os.path.join(root, f) for f in fs if f.endswith(EXTS))
        elif a.endswith(EXTS):
            yield a


LICENSE = '''import { CheckCircle2, XCircle, Clock } from "lucide-react";
const STATUS_GLASS = { ok: "bg-emerald-500/10 text-emerald-700", bad: "bg-red-500/10 text-red-700" };

const renderLicenseStatusBadge = (s) => {
  const Icon = s === "active" ? CheckCircle2 : s === "expired" ? XCircle : Clock;
  return (
    <span className="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium bg-green-100">
      <Icon className="h-3.5 w-3.5" />
      {s}
    </span>
  );
};

const renderPaymentBadge = (s) => (
  <span className={cn("inline-flex items-center gap-1.5 rounded-md px-2.5 py-0.5 text-[11px]", STATUS_GLASS[s])}>
    <span className="h-1.5 w-1.5 rounded-full bg-current" />
    {s}
  </span>
);

const renderApprovalBadge = (s) => (
  <span className={cn("inline-flex items-center gap-1.5 rounded-md px-2.5 py-0.5 text-[11px]", STATUS_GLASS[s])}>
    <span className="h-1.5 w-1.5 rounded-full bg-current" />
    {s}
  </span>
);

export default function LicenseDetail() {
  return <div>{renderLicenseStatusBadge(a)}{renderPaymentBadge(b)}{renderApprovalBadge(c)}</div>;
}
'''


def self_test():
    bad = check("LicenseDetail.tsx", LICENSE)
    assert len(bad) == 1 and bad[0].startswith("LicenseDetail.tsx:4:") and "renderLicenseStatusBadge" in bad[0], bad
    assert "icon ≠ dot" in bad[0] and "rounded-full ≠ rounded-md" in bad[0], bad
    fixed = LICENSE.replace(LICENSE[LICENSE.index("const renderLicenseStatusBadge"):LICENSE.index("const renderPaymentBadge")],
                            LICENSE[LICENSE.index("const renderPaymentBadge"):LICENSE.index("const renderApprovalBadge")]
                            .replace("renderPaymentBadge", "renderLicenseStatusBadge"))
    assert len(badges(fixed)) == 3 and check("clean.tsx", fixed) == [], check("clean.tsx", fixed)
    single = LICENSE[:LICENSE.index("const renderPaymentBadge")]
    assert len(badges(single)) == 1 and check("one.tsx", single) == []
    html = ('<span class="rounded-md px-2 text-xs"><span class="h-2 w-2 rounded-full"></span>A</span>\n' * 2
            + '<span class="rounded-full px-2 text-xs"><svg></svg>B</span>\n')
    assert len(check("x.html", html)) == 1 and ":3:" in check("x.html", html)[0]
    print("badge-consistency --self-test: 4/4 ok (lệch→flag đúng dòng · sạch · 1 badge · span html)")


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        self_test()
        sys.exit(0)
    msgs = []
    for f in files(sys.argv[1:]):
        with open(f, encoding="utf-8", errors="replace") as fh:
            msgs += check(f, fh.read())
    if msgs:
        print("\n".join(msgs))
    sys.exit(1 if msgs else 0)
