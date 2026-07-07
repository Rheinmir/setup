#!/usr/bin/env python3
"""frame-lint — deterministic validator for Ralph FRAMES (GH#15, step 2 / Slice).

A FRAME is one unit of the Ralph production line: `{muc_tieu, scope_code,
acceptance_test}` sliced from a BR clause. Before a frame is allowed into the
loop (step 3), it must pass these 5 rules — the guard against the SLICER's
tail risk (council 028/031): a mis-cut frame is a CORRELATED error (every frame
wrong the same way), so we catch mis-shaped frames deterministically, cheaply,
BEFORE the loop spends money on them.

The 5 rules (all deterministic, exit-code contract):
  1. Schema — required fields present + `schema_version` a known int.
  2. Scope  — scope_code ∩ scope_test == ∅ · globs match real files ·
              scope_code MUST NOT touch the brakes (harness/ .github/ .git/ hooks).
  3. Test-first — acceptance_test runs and is currently RED (exit != 0). A test
              that is already GREEN before the frame is built is a FAKE test.
              (skip with --skip-verify for offline structural checks.)
  4. Freshness — parent_br_hash matches sha256 of the parent BR file (detects an
              ORPHAN frame after the BR changed underneath it).
  5. DAG    — depends_on across the frame set has no cycle.
  7. Content — the frame must be READABLE BY A HUMAN LATER: muc_tieu is a real
              business sentence (not "F10 nghiệp vụ"), and the body has the 4
              template sections (Nghiệp vụ · Input/Output · Tiêu chí nghiệm thu ·
              Ngoài phạm vi), each non-trivially filled.
              Template: skills/br/assets/frame-template.md.

Rules 1-4 are per-frame; rule 5 needs the whole set (run `check` on a directory).

Usage:
  frame-lint.py check <frame.md | frames-dir> [--root DIR] [--skip-verify]
  frame-lint.py selftest        # BAD + GOOD fixtures for every rule (temp dirs)

Exit: 0 = all frames pass · 1 = at least one rule failed · 2 = usage error.
"""
import argparse
import fnmatch
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import yaml  # noqa
except ImportError:
    yaml = None

KNOWN_SCHEMA_VERSIONS = {0}
REQUIRED_FIELDS = [
    "schema_version", "frame_id", "created_by", "parent_br", "clause_ids",
    "parent_br_hash", "muc_tieu", "scope_code", "scope_test", "acceptance_test",
]
# R7 content — a frame is documentation for the human who comes back later.
REQUIRED_BODY_SECTIONS = ["## Nghiệp vụ", "## Input", "## Tiêu chí nghiệm thu", "## Ngoài phạm vi"]
MIN_MUC_TIEU_LEN = 20
MIN_SECTION_LEN = 30
# generic slop: "F10 nghiệp vụ", "frame-f10", bare ids…
_GENERIC_MUC_TIEU = re.compile(r"^(frame[-_ ]?\w+|[fs]?\d+(\.\d+)?)([ :–-]*(nghiệp vụ|nghiep vu|feature|logic))?$", re.I)
# scope_code MUST NOT be able to edit the brakes of the system itself.
FORBIDDEN_SCOPE_SEGMENTS = {"harness", ".github", ".git"}
FORBIDDEN_SCOPE_SUBSTR = ("hook",)


# ── Frontmatter parsing (yaml if present, else a minimal subset parser) ──────
def parse_frontmatter(text):
    """Return the dict from the leading `---`…`---` YAML block. Uses PyYAML when
    available; otherwise a minimal parser covering the flat frame schema shape:
    `key: scalar`, `key: [a, b]`, block lists (`  - item`), one nested map
    (`guards:` then `  k: v`)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("frame file must start with a `---` YAML frontmatter block")
    body = []
    for ln in lines[1:]:
        if ln.strip() == "---":
            break
        body.append(ln)
    else:
        raise ValueError("unterminated frontmatter (missing closing `---`)")
    block = "\n".join(body)
    if yaml is not None:
        data = yaml.safe_load(block) or {}
        if not isinstance(data, dict):
            raise ValueError("frontmatter did not parse to a mapping")
        return data
    return _mini_yaml(body)


def _coerce(v):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [_unquote(x.strip()) for x in inner.split(",") if x.strip()] if inner else []
    if v in ("true", "false"):
        return v == "true"
    if v.lstrip("-").isdigit():
        return int(v)
    return _unquote(v)


def _unquote(s):
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def _mini_yaml(body):
    data, cur_key, cur_list, cur_map = {}, None, None, None
    for raw in body:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        s = raw.strip()
        if indent == 0:
            cur_list = cur_map = None
            if s.endswith(":"):
                cur_key = s[:-1].strip()
                data[cur_key] = None  # decided by following indented lines
            else:
                k, _, v = s.partition(":")
                data[k.strip()] = _coerce(v)
                cur_key = k.strip()
        else:
            if s.startswith("- "):
                if not isinstance(data.get(cur_key), list):
                    data[cur_key] = []
                data[cur_key].append(_unquote(s[2:].strip()))
            else:
                k, _, v = s.partition(":")
                if not isinstance(data.get(cur_key), dict):
                    data[cur_key] = {}
                data[cur_key][k.strip()] = _coerce(v)
    return data


# ── Helpers ─────────────────────────────────────────────────────────────────
def _glob_segments_bad(glob):
    parts = Path(glob).parts
    if parts and parts[0] in FORBIDDEN_SCOPE_SEGMENTS:
        return True
    return any(sub in glob for sub in FORBIDDEN_SCOPE_SUBSTR)


def _matches(globs, root):
    """Match globs against real files, gitignore-style: `src/**` means everything
    under src/. pathlib's `**` only matches directories, so match relative posix
    paths with fnmatch (its `*` spans `/`, so `**` behaves like a recursive glob)."""
    files = [p for p in root.rglob("*") if p.is_file()]
    rels = {p: p.relative_to(root).as_posix() for p in files}
    out = set()
    for g in globs or []:
        for p, rel in rels.items():
            if fnmatch.fnmatch(rel, g):
                out.add(p.resolve())
    return out


def _sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ── The 5 rules — each returns list[str] of failures (empty = pass) ──────────
def rule_schema(fm):
    fails = []
    for f in REQUIRED_FIELDS:
        if f not in fm or fm.get(f) in (None, "", []):
            fails.append(f"R1 schema: missing/empty required field `{f}`")
    sv = fm.get("schema_version")
    if sv not in KNOWN_SCHEMA_VERSIONS:
        fails.append(f"R1 schema: schema_version {sv!r} not in {sorted(KNOWN_SCHEMA_VERSIONS)}")
    if fm.get("created_by") not in ("human", "slicer"):
        fails.append("R1 schema: created_by must be 'human' or 'slicer'")
    return fails


def rule_scope(fm, root):
    fails = []
    code = fm.get("scope_code") or []
    test = fm.get("scope_test") or []
    if not isinstance(code, list) or not isinstance(test, list):
        return ["R2 scope: scope_code and scope_test must be lists of globs"]
    if set(code) & set(test):
        fails.append(f"R2 scope: scope_code and scope_test share glob(s): {sorted(set(code) & set(test))}")
    for g in code:
        if _glob_segments_bad(g):
            fails.append(f"R2 scope: scope_code glob `{g}` touches the brakes (harness/.github/.git/hooks) — forbidden")
    code_files = _matches(code, root)
    test_files = _matches(test, root)
    if not code_files:
        fails.append(f"R2 scope: scope_code {code} matched NO real file under {root}")
    overlap = code_files & test_files
    if overlap:
        rel = sorted(str(p.relative_to(root)) for p in overlap)
        fails.append(f"R2 scope: file(s) matched by BOTH scope_code and scope_test: {rel}")
    return fails


def _child_env():
    # Same determinism guard as loop-runner: disable .pyc so a fast rewrite can't be judged
    # against a stale bytecode cache (harass-test finding 2026-07-06).
    import os
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.setdefault("PYTHONHASHSEED", "0")
    return env


def rule_test_first(fm, root):
    setup = fm.get("setup_cmd")
    if setup:
        subprocess.run(setup, shell=True, cwd=str(root), capture_output=True, text=True, env=_child_env())
    cmd = fm.get("acceptance_test")
    if not cmd:
        return ["R3 test-first: no acceptance_test to run"]
    proc = subprocess.run(cmd, shell=True, cwd=str(root), capture_output=True, text=True, env=_child_env())
    if proc.returncode == 127:
        return [f"R3 test-first: acceptance_test not runnable (exit 127) — `{cmd}`"]
    if proc.returncode == 0:
        return [f"R3 test-first: acceptance_test is ALREADY GREEN (exit 0) before the frame is built — fake/empty test?"]
    return []


def rule_freshness(fm, root):
    br = fm.get("parent_br")
    if not br:
        return ["R4 freshness: no parent_br to hash"]
    brp = (root / br) if not Path(br).is_absolute() else Path(br)
    if not brp.exists():
        return [f"R4 freshness: parent_br file not found: {br}"]
    actual = _sha256_file(brp)
    want = fm.get("parent_br_hash")
    if actual != want:
        return [f"R4 freshness: parent_br_hash mismatch — frame is ORPHAN (BR changed). want {want!r}, got {actual!r}"]
    return []


def rule_exclusive_scope(frame_scopes, root):
    """R6: frames own EXCLUSIVE code territory — the whole point of 'bug ở đâu → đúng
    MỘT frame phụ trách'. Two frames whose scope_code match the same real file = FAIL."""
    fails = []
    matched = [(fid, _matches(globs, root)) for fid, globs in frame_scopes]
    for i in range(len(matched)):
        for j in range(i + 1, len(matched)):
            overlap = matched[i][1] & matched[j][1]
            if overlap:
                rel = sorted(str(p.relative_to(root)) for p in list(overlap)[:5])
                fails.append(f"R6 exclusive-scope: frame `{matched[i][0]}` and `{matched[j][0]}` "
                             f"both own file(s): {rel} — scope phải độc lập, tách lại lát cắt")
    return fails


def rule_content(fm, text):
    """R7: frame phải đọc-hiểu-được bởi người về sau — muc_tieu là câu nghiệp vụ
    thật + body đủ 4 section template, mỗi section có nội dung thật."""
    fails = []
    fid = str(fm.get("frame_id") or "")
    tokens = re.split(r"[-_]", fid.removeprefix("frame").lstrip("-_"))
    if not any(sum(c.isalpha() for c in t) >= 3 for t in tokens):
        fails.append(f"R7 content: frame_id {fid!r} chỉ là mã số — phải có slug nói lên nghiệp vụ "
                     f"(vd frame-010-ean13-checksum; template: skills/br/assets/frame-template.md)")
    mt = str(fm.get("muc_tieu") or "").strip()
    if len(mt) < MIN_MUC_TIEU_LEN or _GENERIC_MUC_TIEU.match(mt):
        fails.append(f"R7 content: muc_tieu {mt!r} chung chung/quá ngắn — phải là MỘT câu nghiệp vụ "
                     f"người-đọc-hiểu (≥{MIN_MUC_TIEU_LEN} ký tự; template: skills/br/assets/frame-template.md)")
    parts = text.split("---", 2)  # ["", frontmatter, body] — file bắt đầu bằng ---
    body = parts[2] if len(parts) >= 3 else ""
    for sec in REQUIRED_BODY_SECTIONS:
        idx = body.find(sec)
        if idx < 0:
            fails.append(f"R7 content: thiếu section `{sec}` trong thân frame (template: skills/br/assets/frame-template.md)")
            continue
        nxt = body.find("\n## ", idx + len(sec))
        chunk = body[idx + len(sec): nxt if nxt >= 0 else len(body)].strip()
        if len(chunk) < MIN_SECTION_LEN:
            fails.append(f"R7 content: section `{sec}` rỗng/sơ sài (<{MIN_SECTION_LEN} ký tự) — viết cho người về sau đọc")
    return fails


def rule_dag(frames):
    """frames: list of (frame_id, depends_on-list). Return failures if any cycle."""
    graph = {fid: list(deps or []) for fid, deps in frames}
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}
    cyc = []

    def visit(n, stack):
        color[n] = GRAY
        for m in graph.get(n, []):
            if m not in graph:
                continue  # dangling dep handled elsewhere; DAG check ignores externals
            if color[m] == GRAY:
                cyc.append(" -> ".join(stack + [m]))
            elif color[m] == WHITE:
                visit(m, stack + [m])
        color[n] = BLACK

    for n in graph:
        if color[n] == WHITE:
            visit(n, [n])
    return [f"R5 dag: dependency cycle detected: {c}" for c in cyc]


# ── Orchestration ───────────────────────────────────────────────────────────
def lint_frame(path, root, skip_verify=False):
    """Lint one frame file (rules 1-4). Returns (frame_id, depends_on, failures)."""
    text = Path(path).read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    fails = []
    fails += rule_schema(fm)
    fails += rule_content(fm, text)
    # only run scope/freshness/test rules if schema gave us the fields
    if not any(f.startswith("R1 schema: missing") for f in fails):
        fails += rule_scope(fm, root)
        fails += rule_freshness(fm, root)
        if not skip_verify:
            fails += rule_test_first(fm, root)
    return fm.get("frame_id"), (fm.get("depends_on") or []), fails, fm


def check(target, root, skip_verify=False):
    root = Path(root).resolve()
    target = Path(target)
    files = sorted(target.glob("*.md")) if target.is_dir() else [target]
    files = [f for f in files if f.name != "index.md"]
    if not files:
        print(f"[frame-lint] no frame files under {target}", file=sys.stderr)
        return 2
    all_ok = True
    frames_for_dag = []
    frame_scopes = []
    for f in files:
        try:
            fid, deps, fails, fm = lint_frame(f, root, skip_verify)
        except (ValueError, OSError) as e:
            print(f"  [FAIL] {f.name}: cannot parse — {e}")
            all_ok = False
            continue
        frames_for_dag.append((fid, deps))
        frame_scopes.append((fid, fm.get("scope_code") or []))
        if fails:
            all_ok = False
            print(f"  [FAIL] {f.name} ({fid}):")
            for x in fails:
                print(f"          - {x}")
        else:
            print(f"  [ok]   {f.name} ({fid})")
    dag_fails = rule_dag(frames_for_dag) + rule_exclusive_scope(frame_scopes, root)
    if dag_fails:
        all_ok = False
        for x in dag_fails:
            print(f"  [FAIL] {x}")
    print("-" * 60)
    print(f"  frame-lint: {'ALL PASS' if all_ok else 'FAILURES PRESENT'}  ({len(files)} frame(s))")
    return 0 if all_ok else 1


# ── Self-test: BAD + GOOD fixtures for each rule ─────────────────────────────
_GOOD_FRAME = """---
schema_version: 0
frame_id: {fid}-luu-so-cai
created_by: human
parent_br: BR.md
clause_ids: [S4.1]
parent_br_hash: {brhash}
muc_tieu: "Người dùng nhập X thì hệ thống tính và lưu kết quả Y vào sổ"
scope_code: ["src/**"]
scope_test: ["tests/**"]
depends_on: [{deps}]
acceptance_test: "{atest}"
guards:
  max_iter: 3
  budget_seconds: 900
  no_progress_k: 2
  escalate_after_iter: 2
---
# frame {fid}

## Nghiệp vụ
Người dùng nhập X trên màn hình nhập liệu; hệ thống tính Y và ghi vào sổ để đối chiếu cuối ngày.

## Input / Output
- Input: giá trị X (số nguyên dương, nhập tay)
- Output: Y = f(X), ghi kèm timestamp vào sổ

## Tiêu chí nghiệm thu
- X hợp lệ thì Y được tính đúng và lưu thành công
- X âm hoặc rỗng thì báo lỗi, không ghi sổ

## Ngoài phạm vi
Không làm phần báo cáo tổng hợp cuối tháng (frame khác phụ trách).
"""


def _write_frame(d, name, **kw):
    (d / name).write_text(_GOOD_FRAME.format(**kw), encoding="utf-8")


def selftest():
    py = sys.executable
    red = f"{py} -c 'import sys;sys.exit(1)'"   # a RED test (feature not built)
    green = f"{py} -c 'import sys;sys.exit(0)'"  # a GREEN test (should fail rule 3)
    ok = True
    results = []

    def record(label, want_fail_substr, exit_expected_fail, dir_target, root, skip=False):
        nonlocal ok
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = check(dir_target, root, skip_verify=skip)
        out = buf.getvalue()
        failed = rc != 0
        hit = (want_fail_substr in out) if want_fail_substr else True
        passed = (failed == exit_expected_fail) and hit
        ok = ok and passed
        results.append((label, "PASS" if passed else "FAIL", rc, want_fail_substr))

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "src").mkdir()
        (root / "tests").mkdir()
        (root / "src" / "x.py").write_text("x = 1\n")
        (root / "tests" / "t.py").write_text("def test(): pass\n")
        (root / "BR.md").write_text("clause S4.1\n")
        brhash = _sha256_file(root / "BR.md")

        # GOOD — all 5 rules pass
        gd = root / "good"; gd.mkdir()
        _write_frame(gd, "frame-001.md", fid="f1", brhash=brhash, deps="", atest=red)
        record("GOOD (5/5 pass)", "ALL PASS", False, gd, root)

        # BAD R1 — missing acceptance_test (drop a required field)
        b1 = root / "bad1"; b1.mkdir()
        (b1 / "frame.md").write_text(_GOOD_FRAME.format(fid="f", brhash=brhash, deps="", atest=red)
                                     .replace('acceptance_test: "%s"' % red, 'acceptance_test: ""'))
        record("BAD R1 schema", "R1 schema", True, b1, root, skip=True)

        # BAD R2 — scope_code touches the brakes (harness/)
        b2 = root / "bad2"; b2.mkdir()
        (root / "harness").mkdir(exist_ok=True)
        (root / "harness" / "h.py").write_text("h = 1\n")
        f2 = _GOOD_FRAME.format(fid="f2", brhash=brhash, deps="", atest=red).replace(
            'scope_code: ["src/**"]', 'scope_code: ["harness/**"]')
        (b2 / "frame.md").write_text(f2)
        record("BAD R2 brakes", "touches the brakes", True, b2, root, skip=True)

        # BAD R3 — acceptance_test already GREEN
        b3 = root / "bad3"; b3.mkdir()
        _write_frame(b3, "frame.md", fid="f3", brhash=brhash, deps="", atest=green)
        record("BAD R3 green-test", "ALREADY GREEN", True, b3, root)

        # BAD R4 — wrong parent_br_hash (orphan)
        b4 = root / "bad4"; b4.mkdir()
        _write_frame(b4, "frame.md", fid="f4", brhash="deadbeef", deps="", atest=red)
        record("BAD R4 orphan", "ORPHAN", True, b4, root, skip=True)

        # BAD R5 — dependency cycle f5a <-> f5b
        b5 = root / "bad5"; b5.mkdir()
        _write_frame(b5, "a.md", fid="f5a", brhash=brhash, deps="f5b-luu-so-cai", atest=red)
        _write_frame(b5, "b.md", fid="f5b", brhash=brhash, deps="f5a-luu-so-cai", atest=red)
        record("BAD R5 cycle", "cycle", True, b5, root, skip=True)

        # BAD R7 — muc_tieu generic + body 1 dòng (frame vô nghĩa với người đọc)
        b7 = root / "bad7"; b7.mkdir()
        f7 = _GOOD_FRAME.format(fid="f7", brhash=brhash, deps="", atest=red)
        f7 = f7.replace('muc_tieu: "Người dùng nhập X thì hệ thống tính và lưu kết quả Y vào sổ"',
                        'muc_tieu: "F10 nghiệp vụ"')
        f7 = f7.split("\n## Nghiệp vụ")[0] + "\n"  # cắt sạch body sections
        (b7 / "frame.md").write_text(f7)
        record("BAD R7 content", "R7 content", True, b7, root, skip=True)

        # BAD R6 — two frames own the SAME file (scope not exclusive)
        b6 = root / "bad6"; b6.mkdir()
        _write_frame(b6, "a.md", fid="f6a", brhash=brhash, deps="", atest=red)
        _write_frame(b6, "b.md", fid="f6b", brhash=brhash, deps="", atest=red)  # same src/** scope
        record("BAD R6 overlap", "exclusive-scope", True, b6, root, skip=True)

        # GOOD R6 — disjoint scopes pass
        g6 = root / "good6"; g6.mkdir()
        (root / "src2").mkdir(); (root / "src2" / "y.py").write_text("y = 1\n")
        _write_frame(g6, "a.md", fid="g6a", brhash=brhash, deps="", atest=red)
        f_b = _GOOD_FRAME.format(fid="g6b", brhash=brhash, deps="", atest=red).replace(
            'scope_code: ["src/**"]', 'scope_code: ["src2/**"]')
        (g6 / "b.md").write_text(f_b)
        record("GOOD R6 disjoint", "ALL PASS", False, g6, root, skip=True)

    print("frame-lint self-test — BAD/GOOD fixtures per rule\n" + "-" * 60)
    for label, tag, rc, sub in results:
        print(f"  [{tag}] {label:<20} rc={rc}")
    print("-" * 60)
    print(f"  RESULT: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    return 0 if ok else 1


def build_parser():
    p = argparse.ArgumentParser(prog="frame-lint.py", description="Deterministic validator for Ralph frames.")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="lint one frame file or every frame in a directory")
    c.add_argument("target", help="frame .md file OR directory of frames")
    c.add_argument("--root", default=".", help="project root that scope globs resolve against")
    c.add_argument("--skip-verify", action="store_true", help="skip rule 3 (do not run acceptance_test)")
    c.set_defaults(func=lambda a: check(a.target, a.root, a.skip_verify))
    s = sub.add_parser("selftest", help="BAD/GOOD fixtures for every rule (temp dirs)")
    s.set_defaults(func=lambda a: selftest())
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
