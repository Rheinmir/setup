#!/usr/bin/env python3
"""L1/Stop: trước khi Claude kết thúc lượt — nếu phiên có sửa wiki thì index.md phải khớp (R3).
Exit 2 = chặn dừng, Claude phải sửa index trước. Có guard chống lặp vô hạn."""
import os
import re
import subprocess
import sys

from hooklib import audit, code_log, find_validators, find_wiki_dir, project_dir, read_payload, run_validator


# file code (đa ngôn ngữ) trong git-status → trigger regen phần code-graph của wiki-graph.
# `$` + re.M vì mỗi dòng porcelain kết ở đường dẫn; khớp SUPPORTED_EXTS của code_imports.
_CODE_RE = re.compile(r"\.(py|js|jsx|ts|tsx|mjs|cjs|go|rs|java|rb|php|c|h|cpp|cc|sh)$", re.M)


def regen_docs(root: str) -> None:
    """Auto-fresh derived docs NGAY khi nguồn của chúng đổi, fail-open, gác bằng git-status nên
    không đụng = không tốn. Hai nhóm ĐỘC LẬP, phạm vi KHÁC nhau:
    (A) overstack.html + CAPABILITIES + skill-search — CHỈ repo framework (có build-overstack-docs.py),
        khi skill/rule/generator đổi.
    (B) wiki-graph.html (whiteboard quan hệ + code-graph cho NGƯỜI xem) — chạy khi có engine
        build-wiki-graph.py, ở CẢ downstream (GH#41 phương án B): repo framework luôn bật; downstream
        bật qua opt-in OVERSTACK_WIKIGRAPH=1 (Taleb: engine chạy trên máy người khác → không auto-on).
        MỘT codepath duy nhất — cùng engine, khác môi trường, không đẻ hook riêng (Munger)."""
    td = os.path.join(root, "fdk", "tools")
    is_framework = os.path.isfile(os.path.join(td, "build-overstack-docs.py"))
    wg = os.path.join(td, "build-wiki-graph.py")
    # (B) chạy khi CÓ engine và (repo framework HOẶC downstream bật opt-in). Không engine → không B.
    wikigraph_on = os.path.isfile(wg) and (is_framework or os.environ.get("OVERSTACK_WIKIGRAPH") == "1")
    if not is_framework and not wikigraph_on:
        return  # không phải framework và cũng không bật wiki-graph downstream → bỏ hẳn (rẻ)
    try:
        st = subprocess.run(["git", "status", "--porcelain"], cwd=root,
                            capture_output=True, text=True, timeout=8).stdout
        # (A) chỉ repo framework: skill/rule/generator đổi → overstack + CAPABILITIES + skill-search
        if is_framework and re.search(r"(skills/.*SKILL\.md|llmwiki/skills/|policy\.yaml|"
                     r"build-overstack-docs\.py|build-capabilities\.py|sync-skills\.py)", st):
            # mirror parity TRƯỚC: sửa canonical skills/<name>/SKILL.md → sinh lại llmwiki/skills/ y hệt
            # NGAY cuối lượt, để 2 cây không stale tạm thời (trước đây phải cp tay → gate mới bắt).
            ss = os.path.join(root, "harness", "scripts", "sync-skills.py")
            if os.path.isfile(ss):
                subprocess.run([sys.executable, ss], capture_output=True, timeout=40)
            for t in ("build-capabilities.py", "build-overstack-docs.py", "build-skill-search.py"):
                subprocess.run([sys.executable, os.path.join(td, t)], capture_output=True, timeout=40)
        # (B) wiki-graph.html: nội dung wiki, engine, HOẶC file code đổi → dựng lại.
        # --code-root=root: seed toàn repo làm node code + import-graph → graph phản ánh cả code dự án
        # → gate bắt cả thay đổi code (_CODE_RE). cwd=root vì generator resolve output + --code-root
        # theo cwd. --also fdk/wiki chỉ khi tồn tại (downstream không có fdk/wiki). Whole-repo ~2s/lần.
        if wikigraph_on and (re.search(r"(wiki/|build-wiki-graph\.py)", st) or _CODE_RE.search(st)):
            also = ["--also", "fdk/wiki"] if os.path.isdir(os.path.join(root, "fdk", "wiki")) else []
            subprocess.run([sys.executable, wg, "llmwiki/wiki", *also, "--code-root", root],
                           cwd=root, capture_output=True, timeout=90)
    except Exception:
        pass


_ANSI = re.compile(r"\033\[[0-9;]*m")
FW_SURFACES = ("fdk/", "harness/", "skills/", "llmwiki/")


def _strip(s: str) -> str:
    return _ANSI.sub("", s).rstrip()


def framework_medic_mirror(root: str) -> int:
    """T2 gương-soi cuối phiên: phiên có ĐỤNG bề mặt framework (fdk/ harness/ skills/
    llmwiki/) → tự chạy `medic --ci` NGAY trước khi kết thúc lượt, để dark-rail/docs-lệch/
    code-vỡ lộ SỚM (không đợi tới commit-gate — bài học R7-f v1.0.5).

    Phạm vi (chống theater): CHỈ repo framework (có fdk/tools/medic.py) — phiên dev PROJECT
    thường không có medic.py nên bỏ qua hoàn toàn; và chỉ khi git-status thật sự chạm surface.
    Khoẻ (warn cũng tính khoẻ) → 1 dòng khẽ báo đã soi. FAIL thật (medic --ci exit≠0, chỉ khi
    có fail) → trả 2 để CHẶN dừng, in chỗ hở cho agent sửa (guard stop_hook_active chống lặp).
    Fail-open tuyệt đối: thiếu medic/git lỗi/timeout → 0, không bao giờ làm gãy phiên."""
    medic = os.path.join(root, "fdk", "tools", "medic.py")
    if not os.path.isfile(medic):
        return 0  # không phải repo framework → không soi
    try:
        st = subprocess.run(["git", "status", "--porcelain"], cwd=root,
                            capture_output=True, text=True, timeout=8).stdout
    except Exception:
        return 0
    if not any(ln[3:].startswith(FW_SURFACES) for ln in st.splitlines() if len(ln) > 3):
        return 0  # phiên không chạm framework → im lặng (chống theater)
    try:
        p = subprocess.run([sys.executable, medic, "--ci"], cwd=root,
                           capture_output=True, text=True, timeout=120)
    except Exception:
        return 0  # medic lỗi/timeout không được chặn người dùng
    if p.returncode == 0:
        head = next((_strip(ln) for ln in p.stdout.splitlines() if "▉" in ln), "medic KHOẺ")
        print(f"🩺 [medic gương-soi] phiên đụng framework → đã tự soi: {head}", file=sys.stderr)
        return 0
    fails = [_strip(ln) for ln in p.stdout.splitlines() if "✗" in ln or "▉ FAIL" in ln]
    print("🩺 [medic gương-soi] phiên ĐỤNG framework mà medic --ci CÓ FAIL — sửa trước khi kết thúc:\n"
          + "\n".join(fails[:10])
          + "\n  → xem đầy đủ: `python3 fdk/tools/medic.py`", file=sys.stderr)
    return 2


def wiki_changed(root: str) -> bool:
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root, capture_output=True, text=True, timeout=10,
        ).stdout
        return "wiki/" in out
    except Exception:
        return False


def main() -> None:
    payload = read_payload()
    audit(payload, "Stop")

    if payload.get("stop_hook_active"):
        sys.exit(0)  # đã block một lần rồi → không lặp vô hạn

    root = project_dir(payload)
    code_log(root, "--render-md")  # log.md auto-block do CODE sinh từ events.jsonl (không nhờ agent ghi)
    tp = payload.get("transcript_path")  # Trụ 1 Cost Attribution: 1 cost record / run, upsert theo session (cumulative, idempotent)
    if tp:
        code_log(root, "--run-cost", f"--transcript={tp}", f"--session={payload.get('session_id') or ''}")
    regen_docs(root)               # overstack.html + CAPABILITIES tự cập nhật khi skill/rule đổi (repo framework)
    if framework_medic_mirror(root) == 2:  # T2: đụng framework → soi medic; FAIL thật thì chặn dừng
        sys.exit(2)
    if not wiki_changed(root):
        sys.exit(0)  # phiên không đụng wiki → không can thiệp

    wiki = find_wiki_dir(root)
    vdir = find_validators(root)
    if wiki is None or vdir is None:
        sys.exit(0)

    # (1) AUTO-INDEX: tự thêm row cho file wiki MỚI vào index.md (self-heal) NGAY khi có thay đổi —
    # index khớp mà không bắt agent sửa tay. Chiều 'stale' (xóa file mà còn row) vẫn để check bên dưới
    # chặn (gỡ row là quyết định của người). Fail-open: lỗi git/python → bỏ qua, không chặn lượt.
    try:
        subprocess.run([sys.executable, os.path.join(vdir, "index_sync.py"),
                        "--wiki-dir", str(wiki), "--fix"], capture_output=True, timeout=15)
    except Exception:
        pass

    rc, err = run_validator("index_sync.py", {"action": "stop", "wiki_dir": str(wiki)}, vdir)
    if rc == 2:
        print(err, file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
