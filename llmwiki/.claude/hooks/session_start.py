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

from hooklib import audit, project_dir, read_payload


def find_health_check(root: Path):
    """harness/scripts cạnh repo, hoặc bản copy cạnh hooks (deploy standalone)."""
    here = Path(__file__).resolve().parent
    for cand in (root / "harness" / "scripts" / "health-check.py",
                 here / "health-check.py",
                 here.parent.parent.parent / "harness" / "scripts" / "health-check.py"):
        if cand.is_file():
            return cand
    return None


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
