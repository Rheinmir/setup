#!/usr/bin/env python3
"""okf-scan — quét MỌI nguồn OKF (wiki + memory store) theo tag/type, trả về mục liên quan,
và ĐỂ LẠI BIÊN LAI để biết việc quét có thật sự chạy — rồi đối chiếu transcript xem agent
có MỞ những mục đó không.

Vì sao cần: recall/orient chỉ *in gợi ý* vào context. Không có gì chứng minh (a) việc quét đã
chạy, (b) agent có đọc thứ được trả về hay chỉ lướt qua. "Agent bảo là đã đọc wiki" không phải
bằng chứng. Ở đây cả hai vế đều tất định, 0 token:

  query "<từ khoá>" [--prompt "<prompt>"] [--tags a,b] [--type t] [--files a,b] [--k N] [--session S] [--json]
        `--prompt`: rút từ khoá TẤT ĐỊNH từ prompt (định danh → từ vựng chỉ mục → bảng cầu Việt→Anh,
        xem prompt_terms) và ghép vào "<từ khoá>" (có thể bỏ trống); file nhắc trong prompt vào --files.
        Quét frontmatter OKF (`type`, `tags`, `title`, `id`) của mọi file .md trong các cây wiki
        + mọi record trong harness/metrics/memory.jsonl (đã mang `type`), xếp hạng theo tag khớp
        → cạnh file→trang (`--files`: file đang dirty / được nhắc; trang trích dẫn file đó nổi
        lên dù chữ không trùng) → BM25 trên title/path/tags (lexrank.py). In top-k. GHI biên lai
        {ts, session, query, files, scanned, returned}. 0 token, tất định.

  verify --session S --transcript P [--json]
        Đọc transcript của phiên, xem mục nào trong `returned` thật sự xuất hiện ở đầu vào
        tool (Read/Grep/…): cập nhật biên lai `opened` + `coverage`. Đây là chỗ duy nhất
        phân biệt "đã trả về" với "đã đọc".

  receipts [--session S] [--json]      xem biên lai
  --check --session S                  exit 2 nếu phiên KHÔNG có biên lai quét nào (gate)
  --self-test

Biên lai: harness/metrics/context-receipts.jsonl (gitignore như các sổ khác).
Fail-open: mọi lỗi hạ tầng → im lặng, exit 0. Đây là công cụ đo, không được phá phiên.
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
try:
    import overstack_paths
    from overstack_paths import harness_dir
except Exception:
    overstack_paths = None
    harness_dir = None
try:
    import lexrank                      # BM25 + cạnh file→trang (0 token). Thiếu → Jaccard cũ.
except Exception:
    lexrank = None

def receipts_path(root):
    if harness_dir:
        return harness_dir(str(root)) / "metrics" / "context-receipts.jsonl"
    return root / "harness" / "metrics" / "context-receipts.jsonl"


def _metrics_dir(root) -> Path:
    return (harness_dir(root) if harness_dir else Path(root) / "harness") / "metrics"


MEMORY = "harness/metrics/memory.jsonl"
WIKI_CANDS = ("fdk/wiki", ".llmwiki/wiki", "llmwiki/wiki", "wiki")
FM = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)
_WORD = re.compile(r"[a-z0-9à-ỹ]+", re.I)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _toks(s: str) -> set:
    return {w.lower() for w in _WORD.findall(s or "") if len(w) > 2}


def _frontmatter(text: str) -> dict:
    """Đọc frontmatter OKF không cần pyyaml — chỉ cần scalar + list phẳng (đủ cho type/tags/title)."""
    m = FM.match(text or "")
    if not m:
        return {}
    out = {}
    for ln in m.group(1).splitlines():
        if ":" not in ln or ln.lstrip().startswith("#") or ln.startswith(" "):
            continue
        k, v = ln.split(":", 1)
        k, v = k.strip(), v.strip().strip("'\"")
        if not k or not v:
            continue
        if v.startswith("[") and v.endswith("]"):
            out[k] = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
        else:
            out[k] = v
    return out


def wiki_dirs(root: Path) -> list:
    return [root / c for c in WIKI_CANDS if (root / c).is_dir()]


def _skip_dirs() -> list:
    """Cây con KHÔNG quét, dạng 'sources/provenance' ; env OKF_SCAN_SKIP (phẩy) ghi đè, rỗng = không bỏ gì."""
    env = os.environ.get("OKF_SCAN_SKIP")
    if env is None:
        return ["sources/provenance"]
    return [x.strip() for x in env.split(",") if x.strip()]


def collect(root: Path) -> list:
    """Mọi mục OKF: file .md có frontmatter trong các cây wiki + record trong memory store."""
    items = []
    for wd in wiki_dirs(root):
        for p in wd.rglob("*.md"):
            # Tuỳ chọn bỏ qua cây con: mặc định sources/provenance/ (sổ scratch-log tự ghi mỗi
            # ngày cho hệ khác đọc — memory-map, overstack; mỗi trang chỉ trích 2 file harness →
            # cạnh yếu, 15/43 mục openship 2026-10-13). Đổi bằng OKF_SCAN_SKIP="a/,b/" ; rỗng = quét hết.
            if any(sk and f"/{sk.strip('/')}/" in p.as_posix() for sk in _skip_dirs()):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
                fm = _frontmatter(text[:2000])
            except Exception:
                continue
            if not fm.get("type"):
                continue                     # OKF v0.1: không có `type` thì không phải mục OKF
            tags = fm.get("tags") or []
            # cạnh file→trang: đường dẫn trang trích dẫn (backtick) — sinh từ chữ đã viết, 0 token
            files = lexrank.cited_files(text) if lexrank else []
            items.append({"source": "wiki", "path": str(p.relative_to(root)),
                          "type": fm["type"], "title": fm.get("title") or p.stem,
                          "tags": tags if isinstance(tags, list) else [str(tags)], "id": fm.get("id") or p.stem,
                          "files": files})
    try:
        for ln in (_metrics_dir(root) / "memory.jsonl").read_text(encoding="utf-8").splitlines():
            if not ln.strip():
                continue
            m = json.loads(ln)
            if not m.get("type"):
                continue
            items.append({"source": "memory",
                          "path": f"{(_metrics_dir(root) / 'memory.jsonl').relative_to(root).as_posix()}#{m.get('id')}",
                          "type": m["type"], "title": (m.get("did") or m.get("text") or "")[:90],
                          "tags": ["memory", m["type"]] + ([m["session"]] if m.get("session") else []),
                          "id": m.get("id"), "files": list(m.get("files") or [])})
    except Exception:
        pass
    return items


def rank(items: list, query: str, tags=None, type_filter=None, k: int = 5, files=None) -> list:
    """Ba tầng, tầng trên thắng tầng dưới (hệ số 10 / 3 / 1):
      tag khớp  — tag là thứ người/máy khai CHỦ ĐÍCH, chính xác hơn đoán từ chữ;
      cạnh file — trang trích dẫn file đang dirty/được nhắc (`files`) liên quan dù chữ không trùng
                  (bench wiki openship, 275 commit thật: chỉ chữ R@1 0.46 → có cạnh 0.98);
      BM25      — chữ trên title/path/tags, thay Jaccard (LongMemEval R@5 0.63 → 0.95).
    Mọi tầng tất định, 0 token. Thiếu lexrank.py → Jaccard cũ (fail-open)."""
    want_tags = {t.strip().lower() for t in (tags or []) if t.strip()}
    qfiles = [f.strip() for f in (files or []) if f and f.strip()]
    cands = []
    for it in items:
        if type_filter and it["type"] != type_filter:
            continue
        it_tags = {str(t).lower() for t in it.get("tags") or []}
        tag_hit = len(want_tags & it_tags)
        if want_tags and not tag_hit:
            continue
        cands.append((it, it_tags, tag_hit))
    hays = [" ".join([it.get("title") or "", it.get("path") or "", " ".join(sorted(tg))]) for it, tg, _ in cands]
    if lexrank:
        lex = lexrank.bm25_scores(query, hays)
    else:                                                   # fallback: Jaccard như bản cũ
        q = _toks(query); lex = []
        for h in hays:
            hay = _toks(h)
            lex.append(len(q & hay) / len(q | hay) if (q and hay) else 0.0)
    out = []
    for (it, _tg, tag_hit), lx in zip(cands, lex):
        edge = lexrank.edge_score(qfiles, it.get("files") or []) if (lexrank and qfiles) else 0.0
        score = tag_hit * 10 + edge * 3 + lx
        if score > 0:
            out.append((score, it))
    out.sort(key=lambda x: (-x[0], x[1]["path"]))
    # Gộp bản TRÙNG (cùng nguồn + title + files): episode auto-ghi mỗi lượt Stop lặp y hệt nhau
    # và chiếm hết k slot, wiki không ngoi lên được (thấy trên openship 2026-10-13: 4/4 slot là
    # "Merge pull request #930"). Giữ bản điểm cao nhất, đồng điểm thì giữ bản ĐỨNG SAU (id mới).
    best = {}
    for sc, it in out:
        # Khoá gộp = (nguồn, tiêu đề). KHÔNG đưa files vào khoá: cùng một did với 3 danh sách
        # file hơi khác nhau vẫn là một lời nhắc; để cả ba thì 3/4 slot recall là bản sao
        # (đo 2026-10-13 sau compact: m254/m329/m92 cùng "Merge pull request #930").
        key = (it.get("source"), re.sub(r"\s+", " ", (it.get("title") or "").strip().lower()))
        cur = best.get(key)
        if cur is None or sc > cur[0] or (sc == cur[0] and str(it.get("id")) > str(cur[1].get("id"))):
            best[key] = (sc, it)
    out = sorted(best.values(), key=lambda x: (-x[0], x[1]["path"]))
    return [dict(it, score=round(sc, 4)) for sc, it in out[:k]]


def _receipts_file(root: Path) -> Path:
    p = receipts_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    rel = p.relative_to(root).as_posix()
    try:                                     # sổ local, không vào git — cùng quy ước các sổ khác
        gi = root / ".gitignore"
        cur = gi.read_text(encoding="utf-8", errors="ignore") if gi.exists() else ""
        if rel not in cur:
            with open(gi, "a", encoding="utf-8") as f:
                f.write(f"\n# okf-scan context receipts\n{rel}\n")
    except Exception:
        pass
    return p


def write_receipt(root: Path, rec: dict) -> None:
    try:
        with open(_receipts_file(root), "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass


def read_receipts(root: Path, session=None) -> list:
    out = []
    try:
        for ln in receipts_path(root).read_text(encoding="utf-8").splitlines():
            if not ln.strip():
                continue
            r = json.loads(ln)
            if session and r.get("session") != session:
                continue
            out.append(r)
    except Exception:
        pass
    return out


# ── Rút từ khoá từ PROMPT (tất định, 0 token) ──────────────────────────────────────────
# Prompt thật ở openship: 18/18 phiên tiếng Việt, title/tag wiki tiếng Anh → BM25 thuần không
# gặp nhau ("tên miền" ≠ "domain"). Ba tầng, tầng nào cũng không cần model:
#   1. định danh trong prompt (đường dẫn, tên file, snake_case, CamelCase, chữ trong backtick)
#      → vào chữ truy vấn, và file-ish thì vào kênh cạnh `files`;
#   2. token prompt ∩ từ vựng chỉ mục (title+path+tags của mọi mục) — từ mượn lọt qua đây;
#   3. bảng cầu Việt→Anh: mặc định bên dưới (từ vựng dev chung) + bảng riêng dự án
#      `<wiki>/.query-bridge.json` ({"cụm tiếng việt": "en terms"}), bảng dự án ghi đè.
# Không rút được gì → trả nguyên prompt (BM25 tự bỏ qua từ không có trong chỉ mục).
DEFAULT_BRIDGE = {
    "tên miền": "domain", "miền": "domain", "định tuyến": "routing", "điều hướng": "routing", "chứng chỉ": "ssl certificate",
    "https": "ssl", "triển khai": "deploy deployment", "đẩy lên": "push deploy", "sao lưu": "backup", "khôi phục": "backup restore",
    "thư điện tử": "mail", "email": "mail", "hộp thư": "mail", "dịch vụ": "service", "môi trường": "environment",
    "biến môi trường": "environment", "cơ sở dữ liệu": "database", "csdl": "database", "migration": "database migration",
    "bảng điều khiển": "dashboard", "giao diện quản trị": "dashboard", "đăng nhập": "auth access", "xác thực": "auth",
    "phân quyền": "auth access permission", "quyền truy cập": "access", "dòng lệnh": "cli", "máy tính để bàn": "desktop",
    "thư viện khách": "sdk client", "kiến trúc": "architecture", "cấu trúc dự án": "project structure", "thư mục": "project structure",
    "nền tảng": "platform", "lõi": "engine kernel", "làm quen": "onboarding tour", "hướng dẫn mới": "onboarding",
    "tự host": "self hosted", "tự lưu trữ": "self hosted", "việc đang làm": "active work", "đang làm dở": "active work",
    "webhook": "api webhook", "giao diện": "dashboard", "người dùng": "auth access", "tài khoản": "auth access",
    "tuyến": "routing", "cổng": "routing", "proxy": "routing", "địa chỉ": "domain routing", "trang tĩnh": "routing",
    "đám mây": "cloud adapter", "máy chủ": "adapter host", "container": "adapter", "docker": "adapter", "k8s": "adapter",
    "bản dựng": "deployment pipeline", "build": "deployment pipeline", "phát hành": "deployment", "rollback": "deployment pipeline",
    "quay lui": "deployment pipeline", "hàng đợi": "pipeline", "nhật ký": "dashboard", "ticket": "dashboard", "vấn đề": "dashboard",
    "bảng": "dashboard", "ứng dụng": "app", "máy chạy": "environment service", "bản chạy": "environment service",
    "trạng thái": "service", "phiên đăng nhập": "auth access", "phiên làm việc": "auth access", "ssh": "access", "khoá api": "auth access", "mật khẩu": "auth",
    "lưu trữ": "backup database", "bản sao": "backup", "schema": "database", "truy vấn": "database",
    "đồng bộ": "sdk cli", "máy khách": "sdk cli desktop", "gói": "sdk", "thư viện": "sdk",
}
_IDENT_RE = re.compile(r"`([^`\n]{2,80})`|((?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.(?:tsx?|jsx?|mjs|py|md|json|ya?ml|go|rs|sql|css|html|sh))"
                       r"|\b([a-z]+_[a-z0-9_]+)\b|\b([a-z]+(?:[A-Z][a-z0-9]+)+)\b|\b([A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+)\b")


def load_bridge(root: Path) -> dict:
    b = dict(DEFAULT_BRIDGE)
    try:
        from overstack_paths import wiki_dir  # type: ignore
        w = wiki_dir(str(root))
    except Exception:
        w = None
    for cand in ([Path(w)] if w else []) + [root / ".llmwiki" / "wiki", root / "llmwiki" / "wiki"]:
        f = Path(cand) / ".query-bridge.json"
        if f.is_file():
            try:
                b.update({str(k).lower(): str(v) for k, v in json.load(open(f, encoding="utf-8")).items()})
            except Exception:
                pass
            break
    return b


def prompt_terms(prompt: str, items: list, bridge: dict) -> dict:
    """prompt → {"q": chữ truy vấn, "files": file-ish nhắc trong prompt, "how": tầng nào góp gì}."""
    text = prompt or ""
    idents, files = [], []
    for m in _IDENT_RE.finditer(text):
        g = next((x for x in m.groups() if x), "")
        if not g:
            continue
        if re.search(r"\.[a-z]{1,5}$", g) and ("/" in g or "." in g):
            files.append(g.strip("`"))
        idents.append(g)
    df = {}
    if lexrank:
        for it in items:
            # từ vựng = title + tags + TÊN FILE trang (không lấy cả đường dẫn: "llmwiki", "wiki", "concepts", "md"
            # là chữ rác chung — phiên thật 14/10: prompt có chữ "wiki" → 4 trang đồng điểm 1.0 bị bơm)
            stem = Path(str(it.get("path") or "")).stem.replace("-", " ").replace("_", " ")
            for t in set(lexrank.norm(" ".join([it.get("title") or "", stem, " ".join(map(str, it.get("tags") or []))]))):
                df[t] = df.get(t, 0) + 1
        ptoks = lexrank.norm(text)
    else:
        ptoks = []
    # Từ mượn (ASCII) có trong chỉ mục; bỏ token Việt (lọt từ trang nháp Việt) và bỏ token có ở quá nửa chỉ mục
    # ("wiki", "llmwiki", "md", "concept", "harness" nằm trong MỌI đường dẫn → phiên thật 13/10 in 3 trang rác điểm 0.11).
    half = max(1, len(items) // 2)
    # Âm tiết Việt không dấu lọt qua isascii ("theo", "cho", "xem"…) và trùng với chữ trong title trang nháp Việt
    # → phiên thật 14/10: "sao lưu theo lịch" kéo theo issue-tracker 0.53. Không phải từ mượn thì bỏ.
    VI_ASCII = {"theo", "cho", "xem", "nay", "con", "ban", "lam", "toi", "nha", "anh", "hay", "may", "khi", "neu", "nen",
                "van", "dang", "dung", "tren", "trong", "sau", "truoc", "vao", "cua", "noi", "phan", "hon", "nhu", "dong",
                "lien", "them", "nhe", "roi", "cai", "cac", "nhung", "voi", "thi", "bao", "chay", "lai", "sua", "tao", "doc"}
    hits = [t for t in dict.fromkeys(ptoks) if t in df and len(t) > 2 and t.isascii() and df[t] <= half and t not in VI_ASCII]
    low = text.lower()
    bridged = []
    for vi, en in bridge.items():
        if vi in low:
            bridged.extend(en.split())
    parts = idents + hits + bridged
    # Không rút được gì → q RỖNG, KHÔNG rơi về prompt thô: chữ Việt không có trong chỉ mục, còn từ chung
    # ("wiki") khớp mọi trang → BM25 chuẩn hoá đẩy một trang bất kỳ lên 1.0 (test_prompt_recall case 5).
    q = " ".join(dict.fromkeys(parts))
    return {"q": q, "files": list(dict.fromkeys(files)),
            "how": {"idents": idents, "vocab": hits, "bridge": list(dict.fromkeys(bridged))}}


def query(root: Path, q: str, tags=None, type_filter=None, k=5, session=None, files=None, prompt=None) -> dict:
    items = collect(root)
    derived = None
    if prompt:                                   # --prompt: rút từ khoá tất định, prompt gốc vẫn vào biên lai
        derived = prompt_terms(prompt, items, load_bridge(root))
        q = (q + " " + derived["q"]).strip() if q else derived["q"]
        files = list(dict.fromkeys(list(files or []) + derived["files"]))
    # --prompt mà không rút được từ khoá lẫn file → không xếp hạng (biên lai vẫn ghi để hook biết đã quét)
    hits = rank(items, q, tags, type_filter, k, files=files) if (q or files or tags) else []
    rec = {"ts": _now(), "session": session or "", "query": q,
           "tags": tags or [], "files": list(files or []), "scanned": len(items),
           "returned": [h["path"] for h in hits], "hits": hits}
    if derived is not None:
        rec["prompt"] = (prompt or "")[:300]
        rec["prompt_terms"] = derived["how"]
    write_receipt(root, rec)
    return rec


def _tool_inputs(transcript: str) -> str:
    """Nối mọi tham số chuỗi của tool_use trong transcript JSONL (assistant → content[].tool_use.input)."""
    vals = []

    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str):
            vals.append(x)
    try:
        with open(transcript, encoding="utf-8", errors="ignore") as fh:
            for ln in fh:
                if '"tool_use"' not in ln:
                    continue
                try:
                    r = json.loads(ln)
                except Exception:
                    continue
                if r.get("type") != "assistant":
                    continue
                for c in (r.get("message") or {}).get("content") or []:
                    if isinstance(c, dict) and c.get("type") == "tool_use":
                        walk(c.get("input"))
    except Exception:
        pass
    return "\n".join(vals)


def verify(root: Path, session: str, transcript: str) -> dict:
    """Mục đã TRẢ VỀ nào thật sự xuất hiện trong đầu vào tool của phiên (agent đã mở/đọc)?

    Nguồn duy nhất trung thực là transcript của provider: nó ghi tool_use với tham số thật.
    So khớp bằng basename + đường dẫn tương đối để không phụ thuộc agent gõ tuyệt đối hay không.
    """
    returned = []
    for r in read_receipts(root, session):
        returned += r.get("returned") or []
    returned = sorted(set(returned))
    # CHỈ đếm tham số tool_use (Read.file_path, Bash.command, Grep.path...). Bản cũ soi cả
    # transcript thô nên khớp luôn chữ trong CHÍNH output hook SessionStart (nơi liệt kê các
    # đường dẫn này) → coverage 1.0 ở 329/329 biên lai openship (đo 2026-10-13), trong khi
    # đếm theo tool_use thật thì 7/72. Biên lai sai còn tệ hơn không có biên lai.
    blob = _tool_inputs(transcript)
    opened = [p for p in returned if p and (p.split("#")[0] in blob)]
    cov = round(len(opened) / len(returned), 3) if returned else 0.0
    rec = {"ts": _now(), "session": session, "kind": "verify", "returned": returned,
           "opened": opened, "coverage": cov}
    write_receipt(root, rec)
    return rec


def self_test() -> int:
    ok = True

    def chk(c, m):
        nonlocal ok
        print(("  \033[1;32m✓\033[0m " if c else "  \033[1;31m✗\033[0m ") + m)
        ok = ok and bool(c)

    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        wd = root / ".llmwiki" / "wiki" / "concepts"
        wd.mkdir(parents=True)
        (wd / "harness-rules.md").write_text(
            "---\ntype: concept\ntitle: \"luật harness R1-R19\"\ntags: [harness, rules, gate]\nid: harness-rules\n---\n\n# x\n## Origin\n- a\n",
            encoding="utf-8")
        (wd / "design-taste.md").write_text(
            "---\ntype: concept\ntitle: \"gu thiết kế UI\"\ntags: [design, ui]\nid: design-taste\n---\n\n# y\n## Origin\n- b\n",
            encoding="utf-8")
        (wd / "no-frontmatter.md").write_text("# không phải OKF\n", encoding="utf-8")
        pv = root / ".llmwiki" / "wiki" / "sources" / "provenance"
        pv.mkdir(parents=True)
        (pv / "131026-session-provenance.md").write_text(
            "---\ntype: source\ntitle: \"harness gate provenance\"\ntags: [harness]\nid: pv\n---\n\n# p\n## Origin\n- d\n", encoding="utf-8")
        (wd / "backups.md").write_text(
            "---\ntype: concept\ntitle: \"Backups\"\ntags: [openship]\nid: backups\n---\n\n# Backups\n"
            "Route `apps/api/src/modules/backups/backup.routes.ts:32`.\n## Origin\n- c\n", encoding="utf-8")
        (root / "harness" / "metrics").mkdir(parents=True)
        (_metrics_dir(root) / "memory.jsonl").write_text(json.dumps(
            {"id": "ep1", "kind": "episode", "type": "episode", "did": "vá hook harness",
             "session": "sessA", "ts": "2026-09-07T00:00:00"}) + "\n" + json.dumps(
            {"id": "ep2", "kind": "episode", "type": "episode", "did": "vá hook harness",
             "session": "sessB", "ts": "2026-09-08T00:00:00"}) + "\n", encoding="utf-8")

        items = collect(root)
        chk(len(items) == 5, f"collect: 3 wiki OKF + 2 memory, bỏ file thiếu frontmatter ({len(items)})")
        chk(any(it.get("files") == ["apps/api/src/modules/backups/backup.routes.ts"] for it in items),
            "collect: lấy được cạnh file→trang từ đường dẫn trong backtick")

        r = query(root, "luật harness", session="sessX")
        chk(r["scanned"] == 5 and r["returned"] and "harness-rules" in r["returned"][0],
            f"query xếp đúng mục liên quan nhất ({r['returned'][:1]})")

        r_edge = query(root, "sửa lỗi lưu trữ", session="sessX",
                       files=["apps/api/src/modules/backups/retention.ts"])
        chk(r_edge["returned"] and "backups" in r_edge["returned"][0] and r_edge["files"],
            f"cạnh file→trang: file dirty cùng module kéo trang lên dù chữ không trùng ({r_edge['returned'][:1]})")

        r_idf = query(root, "harness gate", session="sessX")
        chk(r_idf["returned"] and "harness-rules" in r_idf["returned"][0],
            "BM25/IDF: từ hiếm (gate) quyết định, từ phổ thông (harness) không kéo mục khác lên")

        r2 = query(root, "bất kỳ", tags=["design"], session="sessX")
        chk(len(r2["returned"]) == 1 and "design-taste" in r2["returned"][0],
            "lọc theo tag: chỉ trả mục mang tag đó")

        r3 = query(root, "vá hook", type_filter="episode", session="sessX")
        chk(len(r3["returned"]) == 1 and r3["returned"][0].endswith("#ep2"),
            "lọc theo type + gộp trùng: 2 episode y hệt → trả 1, giữ bản mới (ep2)")

        rs = read_receipts(root, "sessX")
        chk(len(rs) == 5 and all(x.get("scanned") == 5 for x in rs),
            f"biên lai ghi đủ mỗi lượt quét ({len(rs)})")
        chk(read_receipts(root, "khac") == [], "lọc biên lai theo phiên")

        tr = root / "t.jsonl"
        tr.write_text('{"type":"attachment","attachment":{"type":"hook_success","content":"nên đọc: '
                      '.llmwiki/wiki/concepts/design-taste.md backups.md"}}\n'
                      '{"type":"user","message":{"content":"đọc design-taste.md đi"}}\n'
                      '{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read",'
                      '"input":{"file_path":"/x/.llmwiki/wiki/concepts/harness-rules.md"}}]}}\n', encoding="utf-8")
        v = verify(root, "sessX", str(tr))
        chk(len(v["opened"]) == 1 and v["opened"][0].endswith("harness-rules.md") and 0 < v["coverage"] < 1,
            f"verify: chỉ đếm tool_use thật, KHÔNG đếm chữ trong hook/prompt ({v['opened']}, coverage {v['coverage']})")

        v2 = verify(root, "sessX", str(root / "khong-co.jsonl"))
        chk(v2["opened"] == [] and v2["coverage"] == 0.0, "transcript thiếu → coverage 0, không nổ")

        chk(check(root, "sessX") == 0 and check(root, "sessRong") == 2,
            "check: phiên có biên lai → 0, phiên chưa quét gì → 2")
        chk(receipts_path(root).relative_to(root).as_posix() in (root / ".gitignore").read_text(encoding="utf-8"),
            "sổ biên lai tự vào .gitignore")

    print("okf-scan self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 2


def check(root: Path, session: str) -> int:
    return 0 if read_receipts(root, session) else 2


def _opt(args, flag, default=None):
    if flag in args:
        i = args.index(flag)
        return args[i + 1] if i + 1 < len(args) else default
    return default


def main() -> None:
    args = sys.argv[1:]
    if "--self-test" in args:
        sys.exit(self_test())
    root = Path(_opt(args, "--root") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()
    sess = _opt(args, "--session", "")
    try:
        if args and args[0] == "query":
            tags = [t for t in (_opt(args, "--tags") or "").split(",") if t.strip()]
            files = [f for f in (_opt(args, "--files") or "").split(",") if f.strip()]
            qtext = args[1] if len(args) > 1 and not args[1].startswith("--") else ""
            rec = query(root, qtext, tags, _opt(args, "--type"), int(_opt(args, "--k") or 5), sess,
                        files=files, prompt=_opt(args, "--prompt") or None)
            if "--json" in args:
                print(json.dumps(rec, ensure_ascii=False, indent=1)); return
            if not rec["hits"]:
                print(f"okf-scan: quét {rec['scanned']} mục OKF — không có mục nào khớp"); return
            print(f"okf-scan: quét {rec['scanned']} mục OKF → {len(rec['hits'])} liên quan"
                  + (f" (tag: {', '.join(tags)})" if tags else ""))
            for h in rec["hits"]:
                print(f"  · {h['path']}  [{h['type']}] {h['title'][:60]}"
                      + (f"  tags: {', '.join(map(str, h['tags'][:4]))}" if h.get("tags") else ""))
            return
        if args and args[0] == "verify":
            rec = verify(root, sess, _opt(args, "--transcript", "") or "")
            if "--json" in args:
                print(json.dumps(rec, ensure_ascii=False, indent=1)); return
            print(f"okf-scan verify {sess[:8]}: trả về {len(rec['returned'])} mục · "
                  f"agent MỞ {len(rec['opened'])} · coverage {rec['coverage']:.0%}")
            for p in rec["opened"]:
                print(f"  ✓ đã mở: {p}")
            for p in [x for x in rec["returned"] if x not in rec["opened"]]:
                print(f"  · chưa mở: {p}")
            return
        if args and args[0] == "receipts":
            rs = read_receipts(root, sess or None)
            if "--json" in args:
                print(json.dumps(rs, ensure_ascii=False, indent=1)); return
            if not rs:
                print("okf-scan: chưa có biên lai nào"); return
            for r in rs:
                if r.get("kind") == "verify":
                    print(f"  {r['ts'][:16]}  {r.get('session', '')[:8]}  VERIFY  "
                          f"mở {len(r.get('opened') or [])}/{len(r.get('returned') or [])} "
                          f"({r.get('coverage', 0):.0%})")
                else:
                    print(f"  {r['ts'][:16]}  {r.get('session', '')[:8]}  quét {r.get('scanned', 0)} "
                          f"→ {len(r.get('returned') or [])}  «{(r.get('query') or '')[:40]}»")
            return
        if "--check" in args:
            rc = check(root, sess)
            print(f"okf-scan: phiên {sess[:8] or '?'} "
                  + ("CÓ biên lai quét context" if rc == 0 else "CHƯA quét context lần nào"))
            sys.exit(rc)
    except SystemExit:
        raise
    except Exception as e:
        print(f"okf-scan: lỗi hạ tầng, bỏ qua (fail-open): {e}", file=sys.stderr); sys.exit(0)
    print(__doc__)


if __name__ == "__main__":
    main()
