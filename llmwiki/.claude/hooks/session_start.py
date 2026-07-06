#!/usr/bin/env python3
"""L1/SessionStart: chạy health-check pattern-sync, BÁO CÁO (không chặn).

Đầu phiên: so version.json local ↔ remote ↔ disk. Nếu lệch (behind/drift/missing)
in 1 đoạn ngắn vào context để agent biết cần /sync-template. Fail-open tuyệt đối:
thiếu script / mạng chậm / lỗi gì cũng exit 0, không bao giờ làm gãy phiên.
"""
import json
import subprocess
import sys
from pathlib import Path

from hooklib import HARNESS_HOME, audit, project_dir, read_payload


def find_health_check(root: Path):
    """harness/scripts cạnh repo, hoặc bản copy cạnh hooks (deploy standalone)."""
    here = Path(__file__).resolve().parent
    for cand in (root / "harness" / "scripts" / "health-check.py",
                 here / "health-check.py",
                 here.parent.parent.parent / "harness" / "scripts" / "health-check.py"):
        if cand.is_file():
            return cand
    return None


def harness_integrity(root: Path) -> None:
    """U11 (GH#63 Phase 5): self-integrity — so llmwiki/.harness-stamp (hợp đồng install,
    travel theo git) vs ~/.claude/harness/version.json (global đang cài trên máy).
    LỆCH MAJOR → cảnh báo TO; stamp là HỢP ĐỒNG, không tự ép/tự sửa gì.
    Chạy TRƯỚC early-exit template-manifest (downstream v4 không có manifest).
    Fail-open tuyệt đối: thiếu file / JSON hỏng → im lặng, không bao giờ gãy phiên."""
    try:
        stamp_p = root / "llmwiki" / ".harness-stamp"
        if not stamp_p.is_file():
            return  # repo chưa bootstrap v4 → không có hợp đồng để so
        gv_p = HARNESS_HOME / "version.json"
        if not gv_p.is_file():
            print("⚠️ [harness-integrity] repo có llmwiki/.harness-stamp nhưng GLOBAL "
                  "~/.claude/harness CHƯA cài trên máy này — engine/validator global không chạy. "
                  "Cài: bash harness/scripts/install-harness.sh --global (hoặc re-curl bootstrap).")
            return
        want = str(json.loads(stamp_p.read_text()).get("guarded_by", "0"))
        have = str(json.loads(gv_p.read_text()).get("template_version", "0"))
        if want.split(".")[0] != have.split(".")[0]:
            print(f"🚨 [harness-integrity] LỆCH MAJOR: repo khai được gác bản v{want} "
                  f"(llmwiki/.harness-stamp) nhưng global đang cài v{have}. Stamp là hợp đồng — "
                  f"KHÔNG tự ép. Đồng bộ: re-curl bootstrap (cập nhật stamp) hoặc "
                  f"install-harness.sh --global (cập nhật global).")
        elif want != have:
            print(f"⟳ [harness-integrity] stamp v{want} ≠ global v{have} (cùng MAJOR — vẫn chạy "
                  f"bình thường; re-curl bootstrap khi tiện để khớp).")
    except Exception:
        pass


def wiki_drift(root: Path) -> None:
    """Nhắc code→wiki drift đầu phiên (distill openwiki 2026-07-06): wiki có neo
    .last-sync.json (do harness/scripts/wiki-sync.py --mark-synced chốt) mà code đã
    đổi kể từ neo → in 1 dòng nhắc /lint. Phục vụ dự án hiện tại (hợp ADR-004);
    tất định, 0 token, fail-open tuyệt đối."""
    try:
        for wd in (root / "llmwiki" / "wiki", root / "wiki"):
            anchor = wd / ".last-sync.json"
            if not anchor.is_file():
                continue
            head = json.loads(anchor.read_text(encoding="utf-8")).get("gitHead", "")
            if not head:
                return
            n = subprocess.run(["git", "rev-list", "--count", f"{head}..HEAD"],
                               cwd=root, capture_output=True, text=True, timeout=4)
            cnt = int(n.stdout.strip() or 0) if n.returncode == 0 else 0
            if cnt:
                print(f"⟳ [wiki-sync] code đã đổi {cnt} commit kể từ lần sync wiki "
                      f"(neo {head[:10]}) — chạy /lint để rà; chi tiết: "
                      f"wiki-sync.py --check.")
            return
    except Exception:
        pass


def orient(root: Path) -> None:
    """SessionStart orientation: in NGẮN để agent BIẾT project có code-index + wiki + capabilities,
    và NHẮC query chúng để định vị nhanh (đừng grep/đọc mù). Project-relevant — KHÔNG phải FDK
    framework-dev (ADR-004 chỉ cấm auto-bơm FDK). Chỉ in khi thật sự có; fail-open tuyệt đối."""
    try:
        bits = []
        has_cg = (root / ".graph-agent" / "index.db").is_file()
        if not has_cg:
            try:
                has_cg = any((d / ".graph-agent" / "index.db").is_file()
                             for d in root.iterdir() if d.is_dir())
            except Exception:
                pass
        if has_cg:
            bits.append("• code-index (code-graph, auto-reindex khi code đổi) — query `mcp__code-graph__*` "
                        "(search_symbols / get_symbol_context / get_callers) để ĐỊNH VỊ code nhanh, đừng grep mù.")
        wiki = root / "fdk" / "wiki" if (root / "fdk" / "wiki").is_dir() else root / "llmwiki" / "wiki"
        if wiki.is_dir():
            bits.append(f"• wiki `{wiki.relative_to(root)}` — query concept/entity/sources/adr/decisions cho context.")
        for cap in (root / "fdk" / "CAPABILITIES.md", root / "CAPABILITIES.md"):
            if cap.is_file():
                bits.append(f"• `{cap.relative_to(root)}` — bản đồ skill/tool đang có (đọc khi chưa chắc có đồ nghề gì).")
                break
        if bits:
            print("📍 [orientation] Project này có — QUERY trước khi đọc/grep rộng:\n  " + "\n  ".join(bits))
    except Exception:
        pass


def main() -> None:
    payload = read_payload()
    audit(payload, "SessionStart")

    root = Path(project_dir(payload))
    harness_integrity(root)  # U11: so stamp↔global TRƯỚC early-exit (downstream v4 không có manifest)
    wiki_drift(root)         # code→wiki drift — cũng TRƯỚC early-exit (downstream v4 là đích chính)
    if not (root / ".template-manifest.json").is_file():
        sys.exit(0)  # không phải project dùng template → bỏ qua

    orient(root)  # đầu phiên: cho agent BIẾT project có gì + nhắc query trước (chống 'lơ ngơ')

    # NOTE: KHÔNG auto-bơm context framework-dev (FDK) ở đây. Phần lớn phiên là dùng
    # framework để dev DỰ ÁN KHÁC, không phải dev chính framework → bơm nội-bộ-framework
    # vào mọi phiên là nhiễu. Front-door FDK là skill gọi chủ động `/fdk` (xem ADR-004).
    script = find_health_check(root)
    if script is None or not (root / "harness" / "version.json").is_file():
        sys.exit(0)  # chưa có version.json → chưa khởi tạo, im lặng

    try:
        proc = subprocess.run(
            [sys.executable, str(script), "--root", str(root), "--json",
             "--remote-timeout", "4", "--branch", "orca"],
            capture_output=True, text=True, timeout=8,
        )
        rep = json.loads(proc.stdout)
    except Exception:
        sys.exit(0)  # fail-open

    if rep.get("status") == "ok":
        sys.exit(0)

    lines = ["⟳ [pattern-health] cấu hình template lệch — cân nhắc đồng bộ:"]
    if rep.get("behind") or rep.get("version_behind"):
        n = len(rep.get("behind", []))
        rv = rep.get("remote_version")
        lines.append(f"  • {n} pattern cũ hơn remote"
                     + (f" (remote v{rv} > local v{rep.get('local_version')})" if rep.get("version_behind") else "")
                     + " → chạy /health-check rồi /sync-template (downstream).")
    if rep.get("missing"):
        lines.append(f"  • thiếu {len(rep['missing'])} file pattern: "
                     + ", ".join(rep["missing"][:5]) + (" …" if len(rep["missing"]) > 5 else ""))
    if rep.get("drift"):
        lines.append(f"  • {len(rep['drift'])} pattern đã sửa local: "
                     + ", ".join(d.split('/')[-1] for d in rep["drift"][:5])
                     + (" …" if len(rep["drift"]) > 5 else "") + " (upstream hoặc revert).")
    if not rep.get("remote_reachable"):
        lines.append("  • (remote offline — chỉ so local; chạy /health-check khi có mạng để đối chiếu version remote.)")
    print("\n".join(lines))
    sys.exit(0)


if __name__ == "__main__":
    main()
