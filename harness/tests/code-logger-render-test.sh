#!/usr/bin/env bash
# code-logger-render-test — render_md phải giữ ĐÚNG MỘT khối auto trong wiki/log.md, kể cả khi file đã bị xé
# và khi nhiều tiến trình Stop render cùng lúc.
#
# Bối cảnh (đo 02/10/2026): llmwiki/wiki/log.md phình 50 → 5.798 dòng, 118 khối. Ở repo framework stop.py
# chạy 2 lần mỗi lượt (hook dự án + global); hai lần render đọc–sửa–ghi KHÔNG khoá chồng nhau để lại
# "bản ngắn + đuôi bản dài" = END mồ côi (tái hiện 30/1500 lượt). Bản cũ cắt theo END ĐẦU TIÊN nên từ đó
# mỗi lần render thêm một khối. CL=<code-logger.py khác> để chạy với bản cũ (bite test).
# Usage: bash harness/tests/code-logger-render-test.sh [repo-root]   (exit 0 = pass)
set -u
SRC="$(cd "${1:-.}" && pwd)"
CL="${CL:-$SRC/harness/scripts/code-logger.py}"
python3 - "$CL" <<'PY'
import importlib.util, json, multiprocessing as mp, os, sys, tempfile
spec = importlib.util.spec_from_file_location("cl", sys.argv[1]); cl = importlib.util.module_from_spec(spec); spec.loader.exec_module(cl)
S, E = cl.AUTO_START, cl.AUTO_END
fail = 0
def ok(m): print(f"  \033[1;32m✓\033[0m {m}")
def bad(m):
    global fail; fail += 1; print(f"  \033[1;31m✗\033[0m {m}")
def mkroot(n=60):
    r = tempfile.mkdtemp(); os.makedirs(r + "/llmwiki/wiki"); os.makedirs(r + "/harness/metrics")
    open(r + "/harness/metrics/events.jsonl", "w").write("\n".join(json.dumps({"ts": f"2026-09-19T14:{i%60:02d}:00", "event": "file.write", "path": f"llmwiki/wiki/sources/draft/{i}-x.md"}) for i in range(n)) + "\n")
    return r, r + "/llmwiki/wiki/log.md"

print("── (a) file đã bị xé (END mồ côi đứng trước START) phải tự lành, giữ chữ người viết ──")
r, log = mkroot()
open(log, "w").write("# Log\n\n")
cl.render_md(r); good = open(log).read()
open(log, "w").write(good + "cc4f999ad |\n| 2026-09-19 13:59:01 | `x` | y |\n\n" + E + "\n\n## 2026-09-20 — ingest — ghi chép của người\n- dòng người viết\n")
outs = []
for _ in range(3):
    cl.render_md(r); outs.append(open(log).read())
t = outs[-1]
(ok if (t.count(S), t.count(E)) == (1, 1) else bad)(f"sau 3 lần render còn đúng 1 khối (start={t.count(S)} end={t.count(E)})")
(ok if outs[1] == outs[2] else bad)("render lặp lại không làm file đổi (idempotent)")
(ok if "## 2026-09-20 — ingest — ghi chép của người" in t and t.index("# Log") < t.index("## 2026-09-20") else bad)("chữ người viết còn nguyên, đúng thứ tự")

print("── (b) nhiều tiến trình Stop render cùng lúc không được xé file ──")
def worker(a):
    root, keep, go = a; go.wait(); cl.render_md(root, keep)
mp.set_start_method("fork", force=True)
r, log = mkroot(80); human = "# Log\n\n" + "- ghi chép dài cho file lớn\n" * 4000
torn, N = 0, 400
for _ in range(N):
    open(log, "w").write(human); cl.render_md(r, 40)
    go = mp.Event(); ps = [mp.Process(target=worker, args=((r, k, go),)) for k in (40, 12, 25)]
    [p.start() for p in ps]; go.set(); [p.join() for p in ps]
    t = open(log).read()
    torn += not ((t.count(S), t.count(E)) == (1, 1) and t.startswith("# Log"))
(ok if torn == 0 else bad)(f"race 3 tiến trình × {N} lượt: {torn} lượt file bị xé")

print("── (c) START không có END (file cụt) không được nuốt chữ phía dưới ──")
r, log = mkroot()
open(log, "w").write("# Log\n\n" + S + "\n| mảnh |\n\n## giữ dòng này\n")
cl.render_md(r); t = open(log).read()
(ok if "## giữ dòng này" in t and (t.count(S), t.count(E)) == (1, 1) else bad)("chữ sau START cụt được giữ, còn đúng 1 khối")

print(f"\n═══ code-logger-render: {'PASS' if fail == 0 else str(fail) + ' VI PHẠM'}")
sys.exit(1 if fail else 0)
PY
