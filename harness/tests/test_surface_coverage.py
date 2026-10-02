"""test_surface_coverage — GH#191: "phủ hết" phải là diff với bề mặt thật, thêm một trang là đỏ."""
import json
import subprocess
import sys
from pathlib import Path

TOOL = Path(__file__).resolve().parents[2] / "fdk/tools/surface-coverage.py"


def run(*a):
    r = subprocess.run([sys.executable, str(TOOL), *map(str, a)], capture_output=True, text=True)
    return r.returncode, r.stdout


def make_app(root: Path):
    for f in ["app/(dash)/servers/page.tsx", "app/billing/page.tsx", "app/api/jobs/route.ts",
              "pages/legacy/index.tsx", "pages/_app.tsx", "api/modules/members/index.ts",
              "node_modules/x/app/ignored/page.tsx"]:
        (root / f).parent.mkdir(parents=True, exist_ok=True)
        (root / f).write_text("export default function X() {}\n// line2\n")


def scan(root, tmp):
    out = tmp / "surface.json"
    assert run("scan", root, "--modules", "api/modules/*", "--out", out)[0] == 0
    return json.loads(out.read_text()), out


def write(tmp, name, data):
    (tmp / name).write_text(json.dumps(data))
    return tmp / name


def test_scan_lists_real_surface_and_skips_noise(tmp_path):
    root = tmp_path / "app-root"; make_app(root)
    s, _ = scan(root, tmp_path)
    assert set(s["items"]) == {"page:/servers", "page:/billing", "api:/api/jobs", "page:/legacy", "module:members"}


def test_full_ledger_green_then_new_page_turns_red(tmp_path):
    root = tmp_path / "app-root"; make_app(root)
    s, surf = scan(root, tmp_path)
    ledger = {k: {"by": ["flow:a"]} for k in s["items"]}
    ledger["page:/legacy"] = {"exclude": "chuyển hướng sang /servers, không có hành vi riêng"}
    cov = write(tmp_path, "coverage.json", {"commit": s["commit"], "items": ledger})
    rc, out = run("check", surf, cov)
    assert rc == 0 and "4/5 mục bề mặt được phủ, 1 loại trừ" in out

    (root / "app/clusters").mkdir(parents=True)
    (root / "app/clusters/page.tsx").write_text("x\n")
    _, surf = scan(root, tmp_path)
    rc, out = run("check", surf, cov)
    assert rc == 1 and "CHƯA PHỦ page:/clusters" in out


def test_exclusion_without_reason_and_stale_entry_are_red(tmp_path):
    root = tmp_path / "app-root"; make_app(root)
    s, surf = scan(root, tmp_path)
    ledger = {k: {"by": ["flow:a"]} for k in s["items"]}
    ledger["page:/billing"] = {"exclude": " "}
    ledger["page:/gone"] = {"by": ["flow:a"]}
    rc, out = run("check", surf, write(tmp_path, "c.json", {"items": ledger}))
    assert rc == 1 and "loại trừ không có lý do" in out and "page:/gone" in out


def test_flows_verify_ids_and_file_line(tmp_path):
    root = tmp_path / "app-root"; make_app(root)
    s, surf = scan(root, tmp_path)
    cov = write(tmp_path, "c.json", {"items": {k: {"by": ["flow:ok"]} for k in s["items"]}})
    good = {"domains": [{"flows": [{"id": "flow:ok", "steps": [{"id": "s1", "file": "app/billing/page.tsx", "line": 2}]}]}]}
    assert run("check", surf, cov, "--flows", write(tmp_path, "g.json", good), "--root", root)[0] == 0
    bad = {"domains": [{"flows": [{"id": "flow:other", "steps": [{"id": "s1", "file": "app/billing/page.tsx", "line": 99}]}]}]}
    rc, out = run("check", surf, cov, "--flows", write(tmp_path, "b.json", bad), "--root", root)
    assert rc == 1 and "flow không tồn tại flow:ok" in out and "dòng 99 nằm ngoài" in out
