#!/usr/bin/env python3
"""repo_role — công cụ của overstack đang đứng ở LOẠI repo nào? Nhãn là KHAI BÁO; suy theo hình dạng thư mục chỉ là phương án lùi.

    framework   repo phát triển chính overstack (Rheinmir/setup)          → /ship: medic + ci-local + stamp; installer TỪ CHỐI ghi vào đây
    module      repo vệ tinh do ta sở hữu, framework kéo về (orca-graph…) → /ship: test+eval+install-test của nó, tag, rồi re-pin ở framework
    downstream  dự án của user có cài overstack (.llmwiki/)               → /ship: test của dự án + validate; không ci-local/stamp/UAT
    foreign     repo của người khác, không có overstack                   → /ship: chỉ PR/MR; KHÔNG ghi cấu hình overstack nào vào repo

Vì sao cần (đo 20/09/2026): installer chạy nhầm trong repo framework ghi đè harness.yml + settings.json; /ship chỉ có luồng framework
nên ship repo engine phải tự nhớ quy trình khác hẳn. Cả hai đều là "đoán theo hình dạng thư mục" — bug lặp lại (xem build-control-room.detect_root).

    repo_role.py [root] [--json]          in role (một từ) hoặc JSON {role, source, evidence}
    repo_role.py [root] --set ROLE        ghi nhãn: .overstack.yaml (repo_role:) — riêng `foreign` ghi vào sổ MÁY, không đụng repo người khác

Thứ tự: 1) `.overstack.yaml: repo_role` → declared · 2) sổ máy ~/.claude/harness/repo-roles.json theo remote URL → machine ·
3) suy luận kèm BẰNG CHỨNG → inferred (caller phải hỏi user một lần rồi --set).
"""
import json, os, re, subprocess, sys
from pathlib import Path

ROLES = ("framework", "module", "downstream", "foreign")
MACHINE = Path(os.environ.get("OVERSTACK_HARNESS_HOME") or Path.home() / ".claude" / "harness") / "repo-roles.json"
_KEY = re.compile(r"^repo_role:\s*([A-Za-z_-]+)\s*(?:#.*)?$", re.M)


def _remote(root: Path) -> str:
    try:
        r = subprocess.run(["git", "-C", str(root), "remote", "get-url", "origin"], capture_output=True, text=True, timeout=3)
        u = r.stdout.strip()
        return re.sub(r"\.git$", "", re.sub(r"^(git@|https?://)([^:/]+)[:/]", r"\2/", u)).lower() if r.returncode == 0 else ""
    except Exception:
        return ""


def resolve(root=".") -> dict:
    root = Path(root).resolve()
    y = root / ".overstack.yaml"
    text = y.read_text(encoding="utf-8", errors="ignore") if y.is_file() else ""
    m = _KEY.search(text)
    if m:
        role = m.group(1).lower()
        if role not in ROLES:
            raise SystemExit(f"{y}: repo_role `{role}` không hợp lệ — một trong {', '.join(ROLES)}")
        return {"role": role, "source": "declared", "evidence": [f"{y.name}: repo_role: {role}"]}
    rem = _remote(root)
    try:
        book = json.loads(MACHINE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        book = {}
    if rem and book.get(rem) in ROLES:
        return {"role": book[rem], "source": "machine", "evidence": [f"{MACHINE}: {rem}"]}
    ev = []
    if (root / "fdk" / "wiki").is_dir():
        return {"role": "framework", "source": "inferred", "evidence": ["có fdk/wiki/ (wiki riêng của framework)"]}
    if re.search(r"^upstream_pin:", text, re.M):
        return {"role": "module", "source": "inferred", "evidence": [".overstack.yaml có upstream_pin:"]}
    for s in (".llmwiki/.harness-stamp", "llmwiki/.harness-stamp"):   # bare-path: ok — dò CẢ hai layout
        if (root / s).is_file():
            return {"role": "downstream", "source": "inferred", "evidence": [f"có {s}, không có fdk/wiki/"]}
    ev.append("không có fdk/wiki/, không có .harness-stamp, không có nhãn")
    return {"role": "foreign", "source": "inferred", "evidence": ev}


def set_role(root, role: str) -> str:
    if role not in ROLES:
        raise SystemExit(f"role `{role}` không hợp lệ — một trong {', '.join(ROLES)}")
    root = Path(root).resolve()
    if role == "foreign":                       # KHÔNG ghi gì vào repo của người khác
        rem = _remote(root)
        if not rem:
            raise SystemExit("repo không có remote origin — không có khoá để ghi sổ máy; dùng `ship --as foreign` cho lần này")
        try:
            book = json.loads(MACHINE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            book = {}
        book[rem] = role
        MACHINE.parent.mkdir(parents=True, exist_ok=True)
        MACHINE.write_text(json.dumps(book, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return str(MACHINE)
    y = root / ".overstack.yaml"
    text = y.read_text(encoding="utf-8") if y.is_file() else ""
    line = f"repo_role: {role}"
    text = _KEY.sub(line, text, count=1) if _KEY.search(text) else (text.rstrip("\n") + "\n" if text.strip() else "") + line + "\n"
    y.write_text(text, encoding="utf-8")
    return str(y)


def main(argv=None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    if "-h" in a or "--help" in a:
        print(__doc__); return 0
    role = None
    if "--set" in a:
        i = a.index("--set"); role = a[i + 1] if i + 1 < len(a) else ""; del a[i:i + 2]
    as_json = "--json" in a
    rest = [x for x in a if not x.startswith("--")]
    root = rest[0] if rest else "."
    if role is not None:
        print(f"repo_role={role} → {set_role(root, role)}"); return 0
    r = resolve(root)
    print(json.dumps(r, ensure_ascii=False) if as_json else r["role"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
