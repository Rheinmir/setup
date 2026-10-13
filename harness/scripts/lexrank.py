#!/usr/bin/env python3
"""lexrank — xếp hạng TẤT ĐỊNH, 0 token, 0 dependency cho đường đọc của harness.

Dùng chung cho okf-scan.py (quét wiki + memory) và mem-rank.py (store memory). Hai kênh:

  BM25   — thay Jaccard. Jaccard chỉ đếm từ trùng nên mù IDF (từ hiếm = từ phổ thông) và
           phạt văn bản dài. BM25 có bão hoà tần suất + chuẩn hoá độ dài + IDF.
           Đối chứng LongMemEval 500 câu (cùng metric MemPalace): Jaccard R@5 0.628 →
           BM25 0.954 (embedding minilm của MemPalace: 0.966). Bench 2026-10-13.
  EDGE   — cạnh entity tất định `file → trang`: trang nào trích dẫn file đang dirty / được
           nhắc thì nổi lên, không cần chữ trùng. Trên bench wiki openship (275 commit thật):
           chỉ chữ R@1 0.46; có cạnh file R@1 0.98. Cạnh sinh từ chữ đã viết (`## Origin`,
           đường dẫn trong backtick, trường `files` của episode) — 0 token lúc đọc.

Không stem tiếng Việt (giữ nguyên chữ có dấu); stem-lite chỉ áp cho từ ASCII.
"""
from __future__ import annotations

import math
import re
from collections import Counter

_WORD = re.compile(r"[a-z0-9à-ỹ]+", re.I)
# stopword gọn (Anh + Việt) — chỉ bỏ từ nối; từ chuyên môn giữ hết
STOP = set("""a an the and or but if then than so of to in on at by for from with without into as is are was were be been
being am do does did have has had i me my you your he she it its we our they their this that these those there here what
which who when where why how can could would should will may might must not no also just very too about all any some such
only same over under up down out off once while during please thanks ok yes like get got want need know think make let
và hoặc là của cho với từ về trong trên dưới khi đã đang sẽ được bị các những này đó một có không rất cũng để mà thì nên
tôi bạn chúng ta nó họ""".split())
_ASCII = re.compile(r"^[a-z0-9]+$")


def _stem(w: str) -> str:
    if not _ASCII.match(w):
        return w
    for suf in ("ingly", "edly", "ing", "ies", "ied", "ers", "er", "ed", "es", "s", "ly"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            w = w[:-len(suf)]
            if suf in ("ies", "ied"):
                w += "y"
            break
    return w


def norm(s: str) -> list:
    """Chuỗi → list token đã hạ chữ, bỏ stopword, stem-lite. Giữ thứ tự + trùng (cho TF)."""
    out = []
    for w in _WORD.findall(s or ""):
        w = w.lower()
        if w in STOP or (len(w) < 2 and not w.isdigit()):
            continue
        out.append(_stem(w))
    return out


class BM25:
    """BM25 (Robertson/Sparck Jones) trên list doc đã token hoá. k1=1.2, b=0.75 chuẩn."""

    def __init__(self, docs: list, k1: float = 1.2, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tf = [Counter(d) for d in docs]
        self.dl = [len(d) for d in docs]
        self.avgdl = (sum(self.dl) / len(docs)) if docs else 1.0
        df: Counter = Counter()
        for d in self.tf:
            df.update(d.keys())
        n = len(docs)
        self.idf = {w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()}

    def score(self, q: list, i: int) -> float:
        tf, dl = self.tf[i], self.dl[i]
        s = 0.0
        for w in set(q):
            f = tf.get(w)
            if not f:
                continue
            s += self.idf.get(w, 0.0) * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * dl / (self.avgdl or 1)))
        return s

    def scores(self, q: list) -> list:
        return [self.score(q, i) for i in range(len(self.tf))]


def bm25_scores(query: str, texts: list) -> list:
    """Tiện ích một dòng: điểm BM25 của query với từng text (cùng chỉ số). Chuẩn hoá về [0,1]."""
    if not texts:
        return []
    sc = BM25([norm(t) for t in texts]).scores(norm(query))
    top = max(sc) if sc else 0.0
    return [s / top if top > 0 else 0.0 for s in sc]


# ── cạnh file → trang ────────────────────────────────────────────────────────────────────
_PATH = re.compile(r"`((?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+\.[A-Za-z0-9]{1,6})(?::\d+)?`")


def cited_files(text: str) -> list:
    """Đường dẫn file trích dẫn trong văn bản (trong backtick, ≥1 thư mục, có đuôi). Tất định."""
    seen, out = set(), []
    for p in _PATH.findall(text or ""):
        p = p.lstrip("./")
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _dirs(f: str, min_depth: int = 3) -> list:
    parts = f.split("/")
    return ["/".join(parts[:d]) for d in range(len(parts) - 1, min_depth - 1, -1)]   # sâu → nông


def edge_score(query_files: list, item_files: list) -> float:
    """Điểm cạnh: mỗi file query khớp ĐÚNG file trang trích dẫn = 2.0; cùng thư mục module
    (sâu ≥3 cấp) = 1.0 nhân theo độ sâu. Chia theo số file query để không thiên vị commit to."""
    if not query_files or not item_files:
        return 0.0
    items = set(item_files)
    item_dirs = {d for f in item_files for d in _dirs(f)}
    item_base = {f.rsplit("/", 1)[-1] for f in item_files}
    total = 0.0
    for qf in query_files:
        qf = qf.lstrip("./")
        if qf in items:
            total += 2.0
            continue
        if "/" not in qf and qf in item_base:      # chỉ tên file (prompt người gõ) khớp basename trang trích dẫn
            total += 1.5
            continue
        for d in _dirs(qf):
            if d in item_dirs:
                total += min(1.0, len(d.split("/")) / 6)
                break
    return total / max(1, len(query_files)) ** 0.5


def rrf(rank_lists: list, k: int = 60, weights=None) -> list:
    """Reciprocal Rank Fusion — gộp nhiều bảng xếp hạng (list id) thành một, không cần chuẩn hoá điểm."""
    sc: dict = {}
    for li, ranks in enumerate(rank_lists):
        w = (weights or [1.0] * len(rank_lists))[li]
        for r, key in enumerate(ranks):
            sc[key] = sc.get(key, 0.0) + w / (k + r + 1)
    return [key for key, _ in sorted(sc.items(), key=lambda x: (-x[1], str(x[0])))]


def self_test() -> int:
    ok = True
    # IDF: "gate" hiếm phải thắng "harness" phổ thông
    docs = ["luật harness R1-R19 gate", "harness hook stop", "harness hook start", "gu thiết kế UI"]
    sc = bm25_scores("harness gate", docs)
    ok &= sc.index(max(sc)) == 0
    # chuẩn hoá độ dài: doc ngắn chứa đủ từ thắng doc dài lặp từ
    sc2 = bm25_scores("deploy docker", ["deploy app with docker compose", "docker " * 30 + "deploy"])
    ok &= sc2[0] >= sc2[1]
    # không liên quan → 0 (NOOP)
    ok &= max(bm25_scores("zebra", docs)) == 0.0
    # tiếng Việt giữ dấu, không stem
    ok &= norm("Thiết kế giao diện") == ["thiết", "kế", "giao", "diện"]
    # cạnh file
    files = cited_files("xem `apps/api/src/modules/backups/backup.routes.ts:32` và `packages/db/schema.ts`")
    ok &= files == ["apps/api/src/modules/backups/backup.routes.ts", "packages/db/schema.ts"]
    ok &= edge_score(["apps/api/src/modules/backups/backup.routes.ts"], files) == 2.0
    ok &= 0 < edge_score(["apps/api/src/modules/backups/other.ts"], files) < 2.0
    ok &= edge_score(["x/y/z.ts"], files) == 0.0
    # rrf: id đứng đầu cả hai bảng phải đứng đầu
    ok &= rrf([["a", "b", "c"], ["a", "c", "b"]])[0] == "a"
    print("lexrank self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(self_test())
