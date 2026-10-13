#!/usr/bin/env python3
"""Phiên claude -p THẬT (haiku) cho nhiều prompt Việt trên repo có wiki thật: hook recall-prompt có bắn không,
gợi ý những trang nào, agent mở trang nào, có trúng trang đúng không, có rác không. Trần fdk-uat không có bước này.
Chạy: python3 live_prompt_cases.py <repo> [--jobs N]. Dọn biên lai/episode của các phiên thử sau khi chạy."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
REPO = Path(sys.argv[1]).resolve()
JOBS = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 4
PROJ = Path.home() / ".claude" / "projects" / ("-" + str(REPO).strip("/").replace("/", "-"))
OKF = Path.home() / ".claude" / "harness" / "harness" / "scripts" / "okf-scan.py"
CASES = [
    ("tên miền không cấp được chứng chỉ, xem lại luồng cấp SSL",            "domains-routing-ssl"),
    ("sao lưu theo lịch bị lỗi, khôi phục bản sao lưu không chạy",            "backups"),
    ("hộp thư tự host gửi email ra ngoài bị chặn",                            "self-hosted-mail"),
    ("migration cơ sở dữ liệu kẹt khoá khi chạy song song",                   "database"),
    ("bản dựng rollback không quay lại được bản trước trong pipeline triển khai", "deployment-pipeline"),
    ("bảng điều khiển hiện trạng thái dịch vụ sai",                           "dashboard"),
    ("dòng lệnh và sdk máy khách không đồng bộ phiên bản",                    "cli-desktop-sdk"),
    ("đăng nhập qua mcp không có quyền truy cập",                              "access-auth-mcp"),
    ("biến môi trường của dịch vụ không được nạp khi chạy",                   "services-environment"),
    ("sửa endpoints.ts cho đúng đường dẫn gọi api",                            "dashboard"),   # dashboard.md trích apps/dashboard/src/lib/api/endpoints.ts
    ("hôm nay làm gì tiếp nhỉ",                                               None),   # chung chung → không bơm rác
    ("xem lại wiki và harness cho tôi với nhé",                               None),   # chữ chung khớp mọi đường dẫn
]
ASK = ("Tôi sắp làm việc này: {p}. Trước khi làm, hãy đọc trang wiki mà harness gợi ý cho bạn (nếu có) bằng Read, "
       "rồi tóm tắt 2 dòng. Nếu không được gợi ý trang nào, trả lời đúng chữ 'không có gợi ý'.")

def run(case):
    p, gold = case
    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}
    cmd = ["claude", "-p", "--model", "haiku", "--output-format", "json", "--max-turns", "6", "--allowedTools", "Read",
           "--disallowedTools", "Bash,Edit,Write,Agent,WebSearch,WebFetch,Task,Skill,Grep,Glob"]
    r = subprocess.run(cmd, input=ASK.format(p=p), capture_output=True, text=True, cwd=str(REPO), env=env, timeout=300)
    raw = r.stdout.strip()
    try:
        j = json.loads(raw[raw.find("{"):])
    except Exception:
        return {"prompt": p, "gold": gold, "err": (r.stderr or raw)[-200:]}
    sid = j.get("session_id", ""); tp = PROJ / f"{sid}.jsonl"
    ss, pr, reads = [], [], []
    try:
        for r2 in json.loads(subprocess.run([sys.executable, str(OKF), "receipts", "--session", sid, "--root", str(REPO), "--json"],
                                            capture_output=True, text=True).stdout or "[]"):
            (pr if r2.get("prompt") else ss).extend(h["path"].split("/wiki/")[-1].rsplit(".md", 1)[0].split("/")[-1] for h in r2.get("hits") or [] if "/wiki/" in h["path"])
    except Exception:
        pass
    blocks = {"ss": False, "pr": False}
    try:
        for ln in open(tp, encoding="utf-8"):
            rec = json.loads(ln); s = json.dumps(rec, ensure_ascii=False)
            if rec.get("type") != "assistant":
                blocks["ss"] |= "[recall]" in s; blocks["pr"] |= "recall-prompt" in s
            else:
                for c in rec.get("message", {}).get("content") or []:
                    if isinstance(c, dict) and c.get("type") == "tool_use":
                        fp = c.get("input", {}).get("file_path", "")
                        if "/wiki/" in fp: reads.append(fp.split("/wiki/")[-1].rsplit(".md", 1)[0].split("/")[-1])
    except Exception:
        pass
    return {"prompt": p, "gold": gold, "sid": sid, "cost": j.get("total_cost_usd", 0), "ss": ss, "pr": pr,
            "pr_block": blocks["pr"], "reads": reads, "answer": (j.get("result") or "")[:120].replace("\n", " ")}

with ThreadPoolExecutor(JOBS) as ex:
    res = list(ex.map(run, CASES))
ok_sugg = ok_read = junk = 0; n_gold = sum(1 for c in CASES if c[1])
print(f"{'prompt':52s} {'gold':20s} {'gợi ý (SS|prompt)':34s} {'agent mở':24s} kết quả")
for r in res:
    if r.get("err"): print(r["prompt"][:50], "LỖI", r["err"]); continue
    sugg = set(r["ss"]) | set(r["pr"]); g = r["gold"]
    if g:
        hs, hr = g in sugg, g in r["reads"]; ok_sugg += hs; ok_read += hr
        extra = [x for x in r["pr"] if x != g]; junk += len(extra)
        verdict = ("✓ gợi+mở" if hs and hr else "~ gợi, không mở" if hs else "✗ không gợi") + (f" · rác prompt {extra}" if extra else "")
    else:
        verdict = "✓ im lặng" if not r["pr"] else f"✗ bơm rác {r['pr']}"
    print(f"{r['prompt'][:52]:52s} {str(g):20s} {('|'.join(r['ss'])[:14] + ' | ' + ','.join(r['pr']))[:34]:34s} {','.join(r['reads'])[:24]:24s} {verdict}")
print(f"\ncase có gold {n_gold}: gợi ý trúng {ok_sugg}/{n_gold} · agent mở trúng {ok_read}/{n_gold} · trang rác do prompt bơm {junk} · cost ${sum(r.get('cost', 0) for r in res):.3f}")
json.dump(res, open(Path(__file__).parent / "data" / "live_prompt_cases_2026-10-14.json", "w"), ensure_ascii=False, indent=1)
print("SIDS=" + ",".join(r.get("sid", "") for r in res if r.get("sid")))
