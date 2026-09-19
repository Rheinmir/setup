#!/usr/bin/env python3
"""Helpers chung cho L1 adapter (Claude Code). Vendor khác viết adapter tương đương
— xem harness/recipe.md, phần "Cook bản vendor mới".
"""
import datetime
import json
import os
import pathlib
import subprocess
import sys


def read_payload() -> dict:
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def project_dir(payload: dict) -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()


HARNESS_HOME = pathlib.Path(
    os.environ.get("OVERSTACK_HARNESS_HOME") or (pathlib.Path.home() / ".claude" / "harness")
)


def resolve_tool(root: str, rel: str):
    """GLOBAL-SHARED (council-036): tìm engine/tool theo thứ tự REPO-LOCAL → GLOBAL.
      1. root/rel                          (repo framework hoặc repo có copy riêng)
      2. ~/.claude/harness/rel             (global-shared — cài 1 lần, mọi project dùng chung)
    `rel` giữ nguyên cấu trúc con, vd 'fdk/tools/build-wiki-graph.py', 'harness/scripts/mem-rank.py'.
    Trả path str hoặc None (fail-open: không tìm thấy → caller bỏ qua, không chặn phiên)."""
    p = pathlib.Path(root) / rel
    if p.is_file():
        return str(p)
    g = HARNESS_HOME / rel
    if g.is_file():
        return str(g)
    return None


def find_validators(start: str):
    """Thứ tự: env LLMWIKI_VALIDATORS → bản copy cạnh hooks → harness/validators ở repo cha
    → GLOBAL ~/.claude/harness/harness/validators (global-shared)."""
    env = os.environ.get("LLMWIKI_VALIDATORS")
    if env and os.path.isdir(env):
        return pathlib.Path(env)
    here = pathlib.Path(__file__).resolve().parent
    if (here / "validators").is_dir():
        return here / "validators"
    p = pathlib.Path(start).resolve()
    for parent in [p, *p.parents]:
        cand = parent / "harness" / "validators"
        if cand.is_dir():
            return cand
    gv = HARNESS_HOME / "harness" / "validators"        # global-shared fallback
    if gv.is_dir():
        return gv
    return None


def run_validator(name: str, event: dict, validators_dir: pathlib.Path):
    """Chạy validator theo contract stdin-JSON. Trả (returncode, stderr)."""
    proc = subprocess.run(
        [sys.executable, str(validators_dir / name)],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        timeout=30,
    )
    return proc.returncode, proc.stderr.strip()


def scope_config(root: str) -> dict:
    """GH#49: scope index KHAI TƯỜNG MINH qua .overstack.yaml tại root dự án.

    Parser tối giản (hook chạy bằng python hệ thống, không thêm dep pyyaml) — 2 khoá scalar:
        wiki_dir: llmwiki/wiki     # wiki chính (relocate được — hook + graph cùng đọc)
        code_root: src             # vùng code để index (thu hẹp/relocate, tách mẹ/con)
    Thiếu file/khoá → mặc định cũ → KHÔNG hồi quy. Config hỏng → mặc định, không chặn phiên.
    Một nguồn: stop.py (regen wiki-graph) và find_wiki_dir() (mọi hook) đọc cùng hàm này —
    trước đây chỉ regen đọc config nên "relocate wiki" chỉ đúng với graph, sai với R3/orient.
    """
    cfg = {"wiki_dir": None, "code_root": None}
    f = pathlib.Path(root) / ".overstack.yaml"
    if not f.is_file():
        return cfg
    try:
        for ln in f.read_text(encoding="utf-8").splitlines():
            ln = ln.split("#", 1)[0].rstrip()
            if ":" not in ln:
                continue
            k, v = ln.split(":", 1)
            k, v = k.strip(), v.strip().strip("'\"")
            if k in cfg and v:
                cfg[k] = v
    except Exception:
        pass
    return cfg


def find_wiki_dir(root: str):
    # GH#49: wiki_dir khai trong .overstack.yaml thắng mọi ứng viên ngầm định (relocate được).
    declared = scope_config(root)["wiki_dir"]
    if declared:
        d = pathlib.Path(root) / declared
        if d.is_dir():
            return d
    # fdk/wiki first: in the framework repo the framework's OWN wiki lives in the kit (fdk/wiki);
    # downstream projects have no fdk/ → fall through to their per-project wiki. Downstream dùng
    # layout dot (.llmwiki/wiki — installer mặc định) — thiếu ứng viên này thì MỌI hook global
    # (docs-gate, session-continue, session_end…) thoát sớm "không phải project llmwiki" (đo 2026-09-07).
    for cand in (pathlib.Path(root) / "fdk" / "wiki", pathlib.Path(root) / "wiki",
                 pathlib.Path(root) / ".llmwiki" / "wiki", pathlib.Path(root) / "llmwiki" / "wiki"):
        if cand.is_dir():
            return cand
    return None


# Cùng THỨ TỰ với harness/scripts/overstack_paths.py (chuẩn mới trước, cũ sau). Hook không chắc
# import được file đó (global: ~/.claude/harness/harness/scripts) nên chép thứ tự sang đây;
# harness/validators/bare_path_lint.py --self-test assert hai nơi khớp nhau.
OVERSTACK_DIRS = (".llmwiki", "llmwiki")
HARNESS_DIRS = (".harness", "harness")

def _first_dir(root, names):
    for n in names:
        c = pathlib.Path(root) / n
        if c.is_dir():
            return c
    return None

def overstack_dir(root: str):
    return _first_dir(root, OVERSTACK_DIRS)

def harness_dir(root: str) -> pathlib.Path:
    d = _first_dir(root, HARNESS_DIRS)
    if d:
        return d
    fw = (pathlib.Path(root) / "fdk" / "wiki").is_dir()
    return pathlib.Path(root) / ("harness" if fw else ".harness")

def stamp_path(root: str):
    d = overstack_dir(root)
    if d and (d / ".harness-stamp").is_file():
        return d / ".harness-stamp"
    return None


def code_log(root, *args) -> None:
    """Gọi harness/scripts/code-logger.py qua subprocess (fail-open) — log framework BẰNG CODE.

    Để hook (PostToolUse/Stop) ghi log nghiệp vụ tự động, không phụ thuộc agent nhớ append log.md.
    """
    try:
        here = pathlib.Path(__file__).resolve().parent
        # cạnh hooks (deployed downstream — logger xuống cùng project) HOẶC repo framework
        for cl in (here / "code-logger.py",
                   pathlib.Path(root) / "harness" / "scripts" / "code-logger.py"):
            if cl.is_file():
                subprocess.run([sys.executable, str(cl), "--root", str(root), *args],
                               capture_output=True, timeout=5)
                return
    except Exception:
        pass


def audit(payload: dict, event: str) -> None:
    """R4 log-append, bằng máy: mọi event append vào .claude/audit/YYYY-MM-DD.jsonl."""
    try:
        root = pathlib.Path(project_dir(payload))
        d = root / ".claude" / "audit"
        d.mkdir(parents=True, exist_ok=True)
        # audit log chứa command snippets — bảo đảm không bao giờ bị commit
        gi = root / ".claude" / ".gitignore"
        if not gi.exists() or "audit/" not in gi.read_text(encoding="utf-8", errors="ignore"):
            with open(gi, "a", encoding="utf-8") as f:
                f.write("audit/\n")
        ti = payload.get("tool_input") or {}
        rec = {
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
            "event": event,
            "session_id": payload.get("session_id"),
            "tool_name": payload.get("tool_name"),
            "file_path": ti.get("file_path"),
            "command": (ti.get("command") or "")[:200] or None,
        }
        rec = {k: v for k, v in rec.items() if v is not None}
        path = d / (datetime.date.today().isoformat() + ".jsonl")
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass  # audit không bao giờ được phép làm gãy phiên làm việc


def orca_graph_running(root: str):
    """Node nào của orca-graph đang `locked`/`dispatched` + đường dẫn TUYỆT ĐỐI bảng kanban —
    dùng chung cho session_start.py (đầu phiên) và user_prompt_submit.py (mỗi lượt, feedback 170926:
    user muốn link luôn hiện ở cuối response khi graph còn đang chạy, không chỉ đầu phiên).
    Trả `([], None)` khi không có gì đang chạy hoặc thiếu overstack — fail-open, không raise."""
    try:
        ov = overstack_dir(root)
        if not ov:
            return [], None
        graph_dir = pathlib.Path(ov) / "graph"
        if not graph_dir.is_dir():
            return [], None
        running = []
        for p in sorted(graph_dir.glob("*.graph.json")):
            try:
                g = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            for n in g.get("nodes", []):
                if n.get("state") in ("locked", "dispatched"):
                    running.append(f"{g.get('id', p.stem)}/{n['id']}")
        if not running:
            return [], None
        kanban = pathlib.Path(ov) / "html" / "control-room-kanban.html"
        cockpit = pathlib.Path(ov) / "html" / "control-room.html"
        link = kanban if kanban.is_file() else (cockpit if cockpit.is_file() else None)
        return running, (link.resolve() if link else None)
    except Exception:
        return [], None


# R21 touched-paths (feedback 190926 "path đâu mà coi?"): cuối mỗi lượt hook Stop in cho USER
# đường dẫn tuyệt đối các file phiên này tạo/sửa — người xem mở được ngay, không phải hỏi lại.
TOUCHED_CAP = int(os.environ.get("OVERSTACK_TOUCHED_CAP", "40") or "40")
_TOUCHED_NOISE = ("harness/metrics/", ".claude/audit/", "/.locks/", ".events.jsonl")  # bare-path: ok — mẫu substring lọc nhiễu, khớp cả harness/ lẫn .harness/ downstream


def session_touched_files(root: str, transcript_path: str):
    """Path tuyệt đối file phiên này tạo/sửa, mới nhất trước.
    Nguồn 1 (chắc): file_path của tool Write/Edit/NotebookEdit trong transcript.
    Nguồn 2 (bắt cả sửa qua Bash): file trong `git status` có mtime >= mốc bắt đầu phiên.
    Fail-open: lỗi gì cũng trả list rỗng."""
    start, seen = None, set()
    try:
        for line in open(transcript_path, encoding="utf-8", errors="ignore"):
            try:
                r = json.loads(line)
            except Exception:
                continue
            ts = r.get("timestamp")
            if ts and start is None:
                start = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
            msg = r.get("message") if isinstance(r.get("message"), dict) else {}
            for c in msg.get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_use" and \
                        c.get("name") in ("Write", "Edit", "NotebookEdit"):
                    fp = (c.get("input") or {}).get("file_path") or (c.get("input") or {}).get("notebook_path")
                    if fp:
                        seen.add(os.path.abspath(fp))
    except Exception:
        pass
    if start is not None:
        try:
            out = subprocess.run(["git", "-C", root, "status", "--porcelain", "-uall", "-z"],
                                 capture_output=True, text=True, timeout=10).stdout
            top = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel"],
                                 capture_output=True, text=True, timeout=5).stdout.strip() or root
            for ent in out.split("\0"):
                if len(ent) > 3 and ent[:2] != " D" and ent[0] != "D":
                    p = os.path.join(top, ent[3:])
                    if os.path.isfile(p) and os.path.getmtime(p) >= start:
                        seen.add(os.path.abspath(p))
        except Exception:
            pass
    files = [p for p in seen if os.path.isfile(p) and not any(n in p for n in _TOUCHED_NOISE)]
    return sorted(files, key=os.path.getmtime, reverse=True)


def touched_message(files, cap: int = TOUCHED_CAP) -> str:
    """Khối text cho user: tối đa `cap` link file:// (mới nhất trước), dư thì ghi '+N file nữa'."""
    if not files:
        return ""
    lines = [f"📂 [R21] {len(files)} file phiên này tạo/sửa (mới nhất trước):"]
    lines += [f"  file://{p}" for p in files[:cap]]
    if len(files) > cap:
        lines.append(f"  … +{len(files) - cap} file nữa (trần {cap} — OVERSTACK_TOUCHED_CAP)")
    return "\n".join(lines)
