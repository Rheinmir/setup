#!/usr/bin/env python3
"""tc-xlsx — bóc file test case .xlsx (nhiều sheet, cột chuẩn "Test Case ID / Description / Test Steps /
Expected Result / Priority / Test Type / Status") thành JSON + phân loại tự-động-hoá-được, rồi sinh
PLAN.md theo LÔ để orca-graph chạy. Tất định, 0 token.

  tc-xlsx.py extract <file.xlsx> -o tcs.json            # mọi sheet có header "Test Case ID"
  tc-xlsx.py classify tcs.json                          # in bảng: sheet · số TC · ui|calc|perf|security|gap
  tc-xlsx.py plan tcs.json --app "<tên app>" --batch 8 -o DDMMYY-<tên>-PLAN.md [--only ui]
Phân loại (heuristic, ghi nhãn `auto` cho từng TC — model được sửa nhưng phải nói rõ):
  ui        : sheet/description có màn hình, menu, nút, nhấp, hộp thoại, hiển thị → chạy Playwright/Chrome được
  calc      : sheet công thức / tính lương / số liệu → cần dữ liệu đầu vào, không phải UI
  perf      : Test Type có Performance/Load
  security  : sheet Security hoặc SSO/đăng nhập/mật khẩu → không tự động hoá an toàn
  gap       : Test Type Gap-Verification hoặc Steps rỗng "—" → chờ nghiệp vụ
"""
import argparse, json, re, sys, time
from pathlib import Path

UI_WORDS = re.compile(r"màn hình|menu|nút|bấm|nhấp|click|hộp thoại|dialog|hiển thị|double-click|esc|enter|cột|bảng danh sách|trang", re.I)
CALC_WORDS = re.compile(r"công thức|tính lương|lương thực|bảo hiểm|thuế|phụ cấp|ngày công|tncn|hồi tố", re.I)
SEC_WORDS = re.compile(r"sso|đăng nhập|mật khẩu|token|phiên|xss|sql|csrf|quyền truy cập", re.I)


def extract(path: Path) -> list:
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out = []
    for ws in wb.worksheets:
        hdr = None
        for row in ws.iter_rows(values_only=True):
            if row and row[0] == "Test Case ID":
                hdr = [str(h).strip() if h else "" for h in row]; continue
            if not hdr or not row or not isinstance(row[0], str) or not row[0].startswith("TC-"):
                continue
            d = {hdr[i]: (str(row[i]).strip() if i < len(row) and row[i] is not None else "") for i in range(len(hdr)) if hdr[i]}
            out.append({"sheet": ws.title, "id": row[0].strip(), "desc": d.get("Test Case Description", ""),
                        "data": d.get("Test Data", ""), "prep": d.get("Test Data Preparation", ""), "steps": d.get("Test Steps", ""),
                        "expected": d.get("Expected Result", ""), "priority": d.get("Priority", ""), "severity": d.get("Severity", ""),
                        "type": d.get("Test Type", ""), "status": d.get("Status") or d.get("Status SIT", ""), "result": d.get("Result", "")})
    return out


def classify_one(t: dict) -> str:
    sheet = t["sheet"].lower(); text = f"{t['desc']} {t['steps']}"
    if "gap" in t["type"].lower() or t["steps"].strip() in ("", "—", "-"):
        return "gap"
    if "performance" in t["type"].lower() or "load" in t["type"].lower() or "performance" in sheet:
        return "perf"
    if "security" in sheet or SEC_WORDS.search(t["desc"]):
        return "security"
    if "công thức tính" in sheet or ("ui" not in sheet and CALC_WORDS.search(t["desc"]) and not UI_WORDS.search(t["steps"])):
        return "calc"
    if UI_WORDS.search(text) or "ui" in sheet or "cấu hình" in sheet:
        return "ui"
    return "calc"


def classify(tcs: list) -> list:
    for t in tcs:
        t["auto"] = classify_one(t)
    return tcs


def prio(p: str) -> str:
    return {"P0": "High", "P1": "High", "P2": "Medium"}.get(p.strip().upper(), "Low")


def plan(tcs: list, app: str, batch: int, out: Path, only: str) -> None:
    sel = [t for t in tcs if t["auto"] == only]
    if not sel:
        raise SystemExit(f"không có TC loại {only}")
    groups = {}
    for t in sel:
        groups.setdefault(t["sheet"], []).append(t)
    lots = []
    for sheet, items in groups.items():
        for i in range(0, len(items), batch):
            lots.append((sheet, items[i:i + batch]))
    stem = out.stem.replace("-PLAN", "")
    L = [f'''---
type: draft
title: "{app} — chạy {len(sel)} test case {only} theo {len(lots)} lô trên phiên đăng nhập sẵn, xuất report tester-kit — PLAN thi hành"
status: proposed
tags: [plan, sit, playwright, tester-kit, orca-graph]
timestamp: {time.strftime('%Y-%m-%d')}
---

# {app} — {len(sel)} TC {only} · {len(lots)} lô

**Goal:** chạy từng lô TC trên trình duyệt đã đăng nhập (claude-in-chrome hoặc Playwright connectOverCDP), ghi `results/<lô>.json` (PASS/FAIL/BLOCK + ảnh + actual), rồi xuất mỗi lô một report `.xlsx` tester-kit.

## Origin
Sinh bởi `tc-xlsx.py plan` từ file test case do user cung cấp ({len(tcs)} TC, {len(set(t['sheet'] for t in tcs))} sheet); chỉ lấy loại `{only}`. Phân loại là heuristic — TC bị xếp sai thì sửa nhãn `auto` trong tcs.json rồi sinh lại.

## Global constraints
- Không nhập mật khẩu/không vượt SSO; không có phiên đăng nhập → node `blocked` (HITL).
- Không thao tác phá huỷ dữ liệu thật: dừng trước Lưu/Xoá/Cập nhật → ghi `BLOCK — cần môi trường SIT riêng`, trừ khi user cho phép rõ.
- Mỗi TC → `{{"id","status":"PASS|FAIL|BLOCK","actual","screenshot","evidence":[…]}}`; verify của lô = đủ số TC và status hợp lệ.
- Report: `tao_report_test` (tester-kit) — priority P0/P1→High, P2→Medium, P3→Low; description = steps + expected + ACTUAL + status.

## File structure
- `scratchpad/{stem}/app.json` · `results/<lô>.json` · `shots/` · `report-<lô>.xlsx` · `summary.md`

### Task 1: Khảo sát app — URL, menu, phiên đăng nhập

**Kind:** research
**Mode:** hitl
**Files:**
- Tạo: `scratchpad/{stem}/app.json`
**Interfaces:**
- Consumes: URL do user cung cấp; tab trình duyệt đã đăng nhập.
- Produces: `app.json = {{url, logged_in, menus}}`.

**Depends:** —

- [ ] **Step 1:** mở URL trong tab mới, xác nhận không phải trang login; ghi selector các menu.

```json
{{"url": "<URL app>", "logged_in": true, "menus": {{}}}}
```

**Verify:** `python3 -c "import json;d=json.load(open('scratchpad/{stem}/app.json'));assert d['logged_in'] and d['url'].startswith('http')"`
''']
    n = 1
    lot_ids = []
    for sheet, items in lots:
        n += 1; lot = f"lo{n-1}"; lot_ids.append((n, lot))
        ids = ", ".join(t["id"] for t in items)
        L.append(f'''
### Task {n}: Lô {n-1} — {sheet} — {items[0]["id"]}…{items[-1]["id"]}

**Kind:** test
**Files:**
- Tạo: `scratchpad/{stem}/results/{lot}.json`
**Interfaces:**
- Consumes: `app.json` (Task 1).
- Produces: `results/{lot}.json` {len(items)} mục: {ids}.

**Depends:** Task 1

- [ ] **Step 1:** với mỗi TC: làm theo Test Steps, chụp ảnh `shots/<id>.png`, so Expected Result → status; dừng trước thao tác phá huỷ.

```json
{{"id": "{items[0]["id"]}", "status": "PASS|FAIL|BLOCK", "actual": "…", "screenshot": "shots/{items[0]["id"]}.png", "evidence": []}}
```

**Verify:** `python3 -c "import json;r=json.load(open('scratchpad/{stem}/results/{lot}.json'));assert len(r)=={len(items)} and all(x['status'] in ('PASS','FAIL','BLOCK') for x in r)"`
''')
    deps = ", ".join(f"Task {k}" for k, _ in lot_ids)
    files = " ".join(f"scratchpad/{stem}/report-{lot}.xlsx" for _, lot in lot_ids)
    L.append(f'''
### Task {n+1}: Xuất {len(lots)} report tester-kit + tổng hợp

**Kind:** docs
**Files:**
- Tạo: {", ".join(f"`scratchpad/{stem}/report-{lot}.xlsx`" for _, lot in lot_ids)}, `scratchpad/{stem}/summary.md`
**Interfaces:**
- Consumes: mọi `results/*.json`.
- Produces: report xlsx mỗi lô + `summary.md` (PASS/FAIL/BLOCK theo lô, TC cần người).

**Depends:** {deps}

- [ ] **Step 1:** `tc-xlsx.py report results/<lô>.json --url <URL>` in payload → gọi `tao_report_test` → chép xlsx về; viết summary.

```json
{{"url": "<URL app>", "cases": [{{"priority": "High", "name": "TC-…", "shortDesc": "…", "description": "Steps…\\nExpected…\\nActual…\\nStatus: PASS", "complexity": "Medium"}}]}}
```

**Verify:** `ls {files} scratchpad/{stem}/summary.md`
''')
    out.write_text("".join(L), encoding="utf-8")
    print(f"→ {out}  ({len(sel)} TC {only}, {len(lots)} lô + khảo sát + report)")


def report_payload(results: Path, tcs: Path, url: str) -> dict:
    by = {t["id"]: t for t in json.loads(tcs.read_text(encoding="utf-8"))}
    cases = []
    for r in json.loads(results.read_text(encoding="utf-8")):
        t = by.get(r["id"], {})
        cases.append({"priority": prio(t.get("priority", "")), "name": r["id"], "shortDesc": t.get("desc", "")[:200],
                      "description": f"STEPS:\n{t.get('steps','')}\n\nEXPECTED:\n{t.get('expected','')}\n\nACTUAL:\n{r.get('actual','')}\n\nSTATUS: {r['status']}"
                                     + (f"\nSCREENSHOT: {r['screenshot']}" if r.get("screenshot") else ""),
                      "complexity": "High" if t.get("severity", "") in ("Critical", "High") else "Medium"})
    return {"url": url, "cases": cases}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("extract"); p.add_argument("xlsx"); p.add_argument("-o", "--out", default="tcs.json")
    p = sp.add_parser("classify"); p.add_argument("tcs")
    p = sp.add_parser("plan"); p.add_argument("tcs"); p.add_argument("--app", required=True); p.add_argument("--batch", type=int, default=8); p.add_argument("-o", "--out", required=True); p.add_argument("--only", default="ui")
    p = sp.add_parser("report"); p.add_argument("results"); p.add_argument("--tcs", required=True); p.add_argument("--url", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "extract":
        tcs = classify(extract(Path(a.xlsx))); Path(a.out).write_text(json.dumps(tcs, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"→ {a.out}: {len(tcs)} TC từ {len(set(t['sheet'] for t in tcs))} sheet")
    elif a.cmd == "classify":
        tcs = classify(json.loads(Path(a.tcs).read_text(encoding="utf-8")))
        sheets = {}
        for t in tcs:
            sheets.setdefault(t["sheet"], {}).setdefault(t["auto"], 0); sheets[t["sheet"]][t["auto"]] += 1
        for s, c in sheets.items():
            print(f"  {s:<36} {sum(c.values()):>3}  {c}")
        tot = {}
        for t in tcs:
            tot[t["auto"]] = tot.get(t["auto"], 0) + 1
        print(f"TỔNG {len(tcs)}: {tot}  → tự động hoá UI được: {tot.get('ui', 0)}")
    elif a.cmd == "plan":
        plan(classify(json.loads(Path(a.tcs).read_text(encoding="utf-8"))), a.app, a.batch, Path(a.out), a.only)
    elif a.cmd == "report":
        print(json.dumps(report_payload(Path(a.results), Path(a.tcs), a.url), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
