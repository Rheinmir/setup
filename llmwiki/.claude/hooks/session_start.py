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


def main() -> None:
    payload = read_payload()
    audit(payload, "SessionStart")

    root = Path(project_dir(payload))
    if not (root / ".template-manifest.json").is_file():
        sys.exit(0)  # không phải project dùng template → bỏ qua

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
