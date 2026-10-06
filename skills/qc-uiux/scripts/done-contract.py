#!/usr/bin/env python3
"""done-contract — khoá tiêu chí DONE của một báo cáo qc-uiux và giữ chiều tăng giữa các vòng sửa. Tất định, stdlib.

Hai lỗi nó chặn:
  1. NỚI TIÊU CHÍ: DONE viết ra TRƯỚC khi sửa rồi bị sửa lại cho dễ đạt → `check` so sha256, lệch là rc 1.
  2. VÒNG SAU PHÁ VÒNG TRƯỚC: tiêu chí đã đạt ở vòng N thành cổng hồi quy của mọi vòng sau → `verify` chạy lại lệnh
     kiểm của mọi tiêu chí đã đạt, đỏ lại là rc 1 (ratchet — chỉ tăng, không lùi).

Khối DONE trong báo cáo (markdown), mỗi tiêu chí một dòng, lệnh kiểm tất định (nếu có) trong backtick sau "kiểm:":
    <!-- done:begin -->
    - D1: Không tràn ngang ở 375px — kiểm: `node skills/visual-qa/assets/route-shots.mjs --base http://127.0.0.1:3000 --route / --viewports 375x812 --assert`
    - D2: Màn đầu trả lời được "bán gì, cho ai" trong 5 giây (soi ảnh 1440 + 375)
    <!-- done:end -->
Tiêu chí không có lệnh = kiểm bằng mắt (ảnh chụp) — `verify` liệt kê lại để agent soi lại mỗi vòng, không tự cho qua.

Usage:
  done-contract.py lock   <report.md>            ghi <!-- done:sha256=… --> ngay sau khối (chỉ khi chưa khoá)
  done-contract.py check  <report.md>            rc 1 nếu khối DONE đã đổi sau khi khoá / chưa khoá
  done-contract.py pass   <report.md> D1 [D3…]   ghi tiêu chí đã đạt vào <report>.ratchet.jsonl (chạy lệnh kiểm trước; đỏ thì từ chối)
  done-contract.py verify <report.md>            chạy lại lệnh kiểm của MỌI tiêu chí đã đạt; rc 1 nếu cái nào đỏ lại
  done-contract.py status <report.md>            đạt x/y, còn lại gì
"""
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

BLOCK = re.compile(r"<!-- done:begin -->\n(.*?)<!-- done:end -->", re.S)
LOCK = re.compile(r"<!-- done:sha256=([0-9a-f]{64}) -->")
ITEM = re.compile(r"^\s*-\s*(D\d+):\s*(.*?)\s*(?:—\s*kiểm:\s*`([^`]+)`)?\s*$")


def block(text):
    m = BLOCK.search(text)
    if not m:
        raise SystemExit("✗ không thấy khối <!-- done:begin --> … <!-- done:end --> trong báo cáo")
    return m


def items(text):
    return {m.group(1): (m.group(2), m.group(3)) for ln in block(text).group(1).splitlines() if (m := ITEM.match(ln))}


def digest(text):
    return hashlib.sha256(block(text).group(1).strip().encode()).hexdigest()


def run(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600).returncode
    except subprocess.TimeoutExpired:
        return 124


def ledger(rep):
    return rep.with_name(rep.name + ".ratchet.jsonl")


def passed(rep):
    f = ledger(rep)
    return {json.loads(l)["id"] for l in f.read_text().splitlines() if l.strip()} if f.is_file() else set()


def main(argv):
    if len(argv) < 2 or argv[0] not in ("lock", "check", "pass", "verify", "status"):
        print(__doc__); return 2
    cmd, rep = argv[0], Path(argv[1])
    text = rep.read_text(encoding="utf-8")
    lk = LOCK.search(text)
    if cmd == "lock":
        if lk:
            print("· đã khoá — không khoá lại (khoá lại = nới tiêu chí)"); return 0
        if not items(text):
            print("✗ khối DONE không có tiêu chí nào dạng `- D1: …`"); return 1
        m = block(text)
        rep.write_text(text[:m.end()] + f"\n<!-- done:sha256={digest(text)} -->" + text[m.end():], encoding="utf-8")
        print(f"✓ khoá {len(items(text))} tiêu chí DONE"); return 0
    if not lk:
        print("✗ DONE chưa khoá — chạy `lock` trước khi sửa"); return 1
    if lk.group(1) != digest(text):
        print("✗ khối DONE đã bị sửa sau khi khoá (nới tiêu chí) — khôi phục bản đã khoá"); return 1
    if cmd == "check":
        print("✓ DONE khớp bản đã khoá"); return 0
    it, done = items(text), passed(rep)
    if cmd == "pass":
        bad = []
        for i in argv[2:]:
            if i not in it:
                print(f"✗ {i} không có trong DONE"); bad.append(i); continue
            if it[i][1] and run(it[i][1]) != 0:
                print(f"✗ {i} chưa đạt — lệnh kiểm đỏ: {it[i][1]}"); bad.append(i); continue
            if i not in done:
                with ledger(rep).open("a", encoding="utf-8") as f:
                    f.write(json.dumps({"id": i, "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "cmd": it[i][1]}, ensure_ascii=False) + "\n")
            print(f"✓ {i} đạt{' (kiểm bằng mắt — agent tự chịu trách nhiệm)' if not it[i][1] else ''}")
        return 1 if bad else 0
    if cmd == "verify":
        reg = [i for i in sorted(done) if i in it and it[i][1] and run(it[i][1]) != 0]
        eyes = [i for i in sorted(done) if i in it and not it[i][1]]
        for i in reg:
            print(f"✗ HỒI QUY {i}: từng đạt, giờ đỏ — {it[i][0]}")
        if eyes:
            print(f"· soi lại bằng mắt (đã đạt, không có lệnh kiểm): {', '.join(eyes)}")
        print(f"ratchet: {len(done) - len(reg)}/{len(done)} tiêu chí đã đạt vẫn giữ")
        return 1 if reg else 0
    left = [i for i in it if i not in done]
    print(f"DONE {len(done & set(it))}/{len(it)} đạt" + (f" · còn: {', '.join(left)}" if left else " · ĐỦ"))
    return 0 if not left else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
