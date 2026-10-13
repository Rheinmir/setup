#!/usr/bin/env python3
"""Sinh prompt TIẾNG VIỆT cho bench wiki: mỗi commit subject (English) → 2 câu dev Việt nhờ trợ lý làm việc đó.
  plain : không nhắc tên file/định danh mã (chỉ nghiệp vụ)  → đo kênh chữ thuần
  ident : được nhắc 1 tên file hoặc định danh có trong commit → đo tầng "định danh trong prompt"
Gold giữ nguyên (trang trích dẫn file commit chạm). Haiku, 1 lượt, ~275 call. Kết quả: data/wiki_queries_vi.json"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).parent
REPO = Path(sys.argv[1])
cases = json.load(open(HERE / "bench_wiki_queries.json"))
log = subprocess.run(["git", "log", "--no-merges", "--name-only", "--format=@@%h|%s", "-n600", "--", "apps", "packages"],
                     cwd=REPO, capture_output=True, text=True).stdout
files_by_subject, cur = {}, None
for ln in log.splitlines():
    if ln.startswith("@@"):
        cur = ln[2:].split("|", 1)[1]; files_by_subject.setdefault(cur, [])
    elif ln.strip() and cur is not None: files_by_subject[cur].append(ln.strip())

def ask(c):
    files = files_by_subject.get(c["q"], [])[:6]
    prompt = ("Bạn là lập trình viên Việt Nam đang nhờ trợ lý AI lập trình làm một việc trong repo. "
              "Commit subject (tiếng Anh) mô tả việc đó:\n  " + c["q"] + "\nFile commit chạm:\n  " + "\n  ".join(files) +
              "\n\nViết 2 câu nhờ việc bằng tiếng Việt tự nhiên, ngắn như người gõ vào chat (10–25 từ), KHÔNG dịch word-by-word:\n"
              "- plain: chỉ mô tả nghiệp vụ, TUYỆT ĐỐI không nhắc tên file, tên hàm, tên biến, từ tiếng Anh kỹ thuật nào ngoài từ mượn rất phổ biến (deploy, api, db cũng KHÔNG dùng).\n"
              "- ident: giống plain nhưng có nhắc đúng 1 tên file (basename) hoặc 1 định danh mã lấy từ danh sách file trên.\n"
              "Trả về DUY NHẤT JSON: {\"plain\": \"...\", \"ident\": \"...\"}")
    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}
    cmd = ["claude", "-p", "--model", "haiku", "--output-format", "json", "--max-turns", "1", "--no-session-persistence",
           "--disallowedTools", "Read,Bash,Grep,Glob,Edit,Write,Agent,WebSearch,WebFetch,Task,Skill,ToolSearch"]
    try:
        p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, env=env, timeout=120)
        j = json.loads(p.stdout); txt = (j.get("result") or "").strip()
        s, e = txt.find("{"), txt.rfind("}")
        v = json.loads(txt[s:e + 1])
        return dict(c, files=files, vi_plain=v.get("plain", ""), vi_ident=v.get("ident", ""), cost=j.get("total_cost_usd", 0))
    except Exception as ex:
        return dict(c, files=files, vi_plain="", vi_ident="", err=str(ex)[-200:])

with ThreadPoolExecutor(6) as ex:
    out = list(ex.map(ask, cases))
json.dump(out, open(HERE / "data" / "wiki_queries_vi.json", "w"), ensure_ascii=False, indent=1)
ok = sum(1 for o in out if o["vi_plain"] and o["vi_ident"])
print(f"done {ok}/{len(out)} · cost ${sum(o.get('cost', 0) for o in out):.2f}")
