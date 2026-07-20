#!/usr/bin/env python3
"""orca-reconcile — đối soát task orchestration của Orca: việc nào chưa kết thúc, vì sao.

Vì sao tồn tại (đo 2026-07-20, T-260720-01):
  Trên 59 task orchestration: 13 (22%) từng được dispatch, **46 (78%) có `dispatch: null`
  — chưa bao giờ được giao**. Toàn bộ 14 task treo (ready/blocked) đều thuộc nhóm này,
  rải từ 2026-05-22 tới 2026-07-17. Không cổng nào đối soát, không ai dọn.

  `dispatch-verify.py` đã đóng một vòng KHÁC (lời-hứa proposal ↔ artifact trên đĩa).
  Vòng này — runtime task state — trước nay không ai đóng.

PHÂN NHÓM là điểm chính, không phải đếm:
  · chưa-từng-dispatch  → câu hỏi "VÌ SAO người điều phối không giao?"
                          (gốc: không biết lúc nào worker xong → xem orca-dispatch.py)
  · đã-giao-rồi-treo    → câu hỏi "worker chết ở đâu?"
  · failed-chưa-triage  → cần người phán
  Hai nhóm đầu đòi hai hành động hoàn toàn khác nhau; gộp lại là mất thông tin.

KỶ LUẬT: tool này CHỈ BÁO CÁO. Không gọi task-update, không reset, không xoá.
  Đóng một task là hành động có chủ ý của người — một worker chạy lâu bị đoán nhầm
  là đã chết thì việc đang chạy bị giết oan.

Fail-open: thiếu `orca` / runtime tắt / JSON lạ → coi là BÌNH THƯỜNG (exit 0, im).
  Người không dùng orchestration không bao giờ bị cổng sức khoẻ làm phiền.

CLI:
    orca-reconcile.py [--stale-days 7] [--json]
    orca-reconcile.py --self-test
"""
from __future__ import annotations

import argparse
import datetime
import json
import shutil
import subprocess
import sys

DEFAULT_STALE_DAYS = 7
OPEN_STATUSES = ("ready", "blocked", "failed")


def classify(task: dict, has_dispatch: bool) -> str:
    if task.get("status") == "failed":
        return "failed-chua-triage"
    return "da-giao-roi-treo" if has_dispatch else "chua-tung-dispatch"


def age_days(created_at: str, now=None) -> int:
    """Tuổi theo ngày. Chuỗi lạ → 0 (fail-open: không bịa tuổi)."""
    if not created_at:
        return 0
    now = now or datetime.datetime.now()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return max(0, (now - datetime.datetime.strptime(created_at[:19], fmt)).days)
        except ValueError:
            continue
    return 0


def _orca_json(*args, timeout=25):
    try:
        out = subprocess.run(["orca", *args], capture_output=True, text=True, timeout=timeout)
        return json.loads(out.stdout)
    except Exception:  # noqa: BLE001 — fail-open có chủ đích
        return None


def collect(stale_days=DEFAULT_STALE_DAYS):
    """Trả (available, report). available=False nghĩa là không có Orca — KHÔNG phải lỗi."""
    if shutil.which("orca") is None:
        return False, {"reason": "orca không có trên PATH"}
    d = _orca_json("orchestration", "task-list", "--json")
    if not d or not d.get("ok"):
        return False, {"reason": "runtime Orca không phản hồi"}
    tasks = (d.get("result") or {}).get("tasks") or []
    groups: dict[str, list] = {}
    for t in tasks:
        if t.get("status") not in OPEN_STATUSES:
            continue
        ds = _orca_json("orchestration", "dispatch-show", "--task", t.get("id", ""), "--json")
        has = bool(((ds or {}).get("result") or {}).get("dispatch"))
        groups.setdefault(classify(t, has), []).append({
            "id": t.get("id"), "status": t.get("status"),
            "age_days": age_days(t.get("created_at", "")),
            "spec": (t.get("spec") or "")[:90],
        })
    stale = [x for g in groups.values() for x in g if x["age_days"] >= stale_days]
    return True, {
        "total_tasks": len(tasks),
        "open_total": sum(len(v) for v in groups.values()),
        "groups": {k: len(v) for k, v in groups.items()},
        "stale_count": len(stale),
        "max_age_days": max([x["age_days"] for x in stale], default=0),
        "stale_days_threshold": stale_days,
        "detail": groups,
    }


def self_test() -> int:
    """Tất định, KHÔNG cần runtime — chạy được ở CI."""
    fails = []

    def ck(name, cond):
        print(f"  {'[OK ]' if cond else '[FAIL]'} {name}")
        if not cond:
            fails.append(name)

    ck("không dispatch → nhóm chua-tung-dispatch",
       classify({"status": "ready"}, False) == "chua-tung-dispatch")
    ck("có dispatch → nhóm da-giao-roi-treo",
       classify({"status": "ready"}, True) == "da-giao-roi-treo")
    ck("failed → nhóm riêng dù đã dispatch",
       classify({"status": "failed"}, True) == "failed-chua-triage")
    now = datetime.datetime(2026, 7, 20)
    ck("tuổi tính đúng theo ngày", age_days("2026-07-13 00:00:00", now) == 7)
    ck("tuổi làm tròn XUỐNG, không thổi phồng", age_days("2026-07-13 10:00:00", now) == 6)
    ck("ts lạ → 0, không bịa tuổi", age_days("rác", now) == 0)
    ck("ts rỗng → 0", age_days("", now) == 0)
    # Needle ghép lúc chạy: nếu viết thẳng literal thì CHÍNH dòng check này chứa chuỗi
    # cần tìm và test tự-fail vĩnh viễn (bug đã dính lần đầu, giữ lại làm ghi nhớ).
    src = open(__file__, encoding="utf-8").read()
    verbs = [ln for ln in src.splitlines()
             if "_orca_json(" in ln and "def " not in ln]
    ck("mọi lời gọi orca đều là verb CHỈ-ĐỌC (không đổi state)",
       all(any(v in ln for v in ("task-" + "list", "dispatch-" + "show")) for ln in verbs))
    avail, rep = collect()
    ck("thiếu orca/runtime → available=False, KHÔNG raise",
       isinstance(rep, dict) and isinstance(avail, bool))

    print(f"\nSELF-TEST: {'ALL PASS' if not fails else str(len(fails)) + ' FAIL'}")
    return 1 if fails else 0


def main() -> None:
    ap = argparse.ArgumentParser(description="đối soát task orchestration Orca (chỉ báo cáo)")
    ap.add_argument("--stale-days", type=int, default=DEFAULT_STALE_DAYS)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        sys.exit(self_test())

    avail, rep = collect(a.stale_days)
    if a.json:
        print(json.dumps({"available": avail, **rep}, ensure_ascii=False, indent=1))
        sys.exit(0)
    if not avail:
        print(f"· orchestration: bỏ qua — {rep.get('reason')}")
        sys.exit(0)
    if not rep["open_total"]:
        print(f"✓ orchestration: 0 task treo / {rep['total_tasks']} task.")
        sys.exit(0)
    print(f"⚠ orchestration: {rep['open_total']} task chưa kết thúc / {rep['total_tasks']} "
          f"(cũ nhất {rep['max_age_days']} ngày)")
    for g, n in sorted(rep["groups"].items(), key=lambda kv: -kv[1]):
        print(f"   · {g}: {n}")
        for x in sorted(rep["detail"][g], key=lambda x: -x["age_days"])[:5]:
            print(f"       {x['id']}  {x['age_days']}d  {x['spec'][:60]}")
    print("   → đây là BÁO CÁO; đóng task là hành động có chủ ý (orca orchestration task-update)")
    sys.exit(0)


if __name__ == "__main__":
    main()
