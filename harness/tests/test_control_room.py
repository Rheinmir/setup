"""test_control_room — cockpit của overstack đọc graph qua SHIM orca-graph (engine thật ở repo Rheinmir/orca-graph).
Phủ hai thứ một lúc: shim import được bằng importlib + chạy được bằng CLI, và control-room render từ store thật.
Test của chính engine nằm ở repo engine (tests/ + evals/), không còn ở đây."""
import os, subprocess, sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "harness/scripts/orca-graph.py"
ENGINE = Path(os.environ.get("ORCA_GRAPH_ENGINE_DIR") or Path.home() / ".orca-graph/repo/engine") / "orca-graph.py"
pytestmark = pytest.mark.skipif(not ENGINE.is_file(), reason="chưa cài engine orca-graph (install.sh của Rheinmir/orca-graph)")

PLAN = """# X
### Task 1: A
**Files:**
- Tạo: `a.py`
**Verify:** `true`
### Task 2: B
**Files:**
- Sửa: `b.py`
**Depends:** Task 1 (data)
**Verify:** `true`
"""


def run(d, *args):
    return subprocess.run([sys.executable, str(SCRIPT), "--dir", str(d), *args], capture_output=True, text=True, cwd=ROOT)


def setup(tmp_path):
    p = tmp_path / "x-PLAN.md"; p.write_text(PLAN, encoding="utf-8")
    r = run(tmp_path, "build", str(p)); assert r.returncode == 0, r.stderr
    return "x"


def test_control_room(tmp_path):
    gid = setup(tmp_path); run(tmp_path, "lock", gid, "t1"); run(tmp_path, "set", gid, "t1", "dispatched", "--op-key", "k")
    out = tmp_path / "control-room.html"
    env = dict(os.environ, ORCA_GRAPH_HOME=str(tmp_path / "home"))
    r = subprocess.run([sys.executable, str(ROOT / "fdk/tools/build-control-room.py"), "--dirs", str(tmp_path), "-o", str(out)], capture_output=True, text=True, cwd=ROOT, env=env)
    assert r.returncode == 0, r.stderr
    h = out.read_text(encoding="utf-8")
    assert "theme-switch" in h and 'class="path"' in h and 'http-equiv="refresh"' in h and ">t1<" in h and "đã giao" in h, h[:300]


def test_shim_reports_missing_engine_with_install_command(tmp_path):
    env = dict(os.environ, ORCA_GRAPH_ENGINE_DIR=str(tmp_path / "nope"), HOME=str(tmp_path))
    r = subprocess.run([sys.executable, str(SCRIPT), "--version"], capture_output=True, text=True, env=env)
    assert r.returncode == 3 and "Rheinmir/orca-graph/main/install.sh" in r.stderr


def test_shim_keeps_file_pointing_at_overstack_layout():
    import importlib.util
    spec = importlib.util.spec_from_file_location("og_shim", SCRIPT); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    assert Path(m.__file__) == SCRIPT and Path(m.__engine_dir__) == ENGINE.parent and callable(m.audit_edges)


def test_viz_and_atlas_shims_render(tmp_path):
    """fdk/tools/graph-viz.py + fdk/tools/graph-atlas.py là shim: atlas nạp graph-viz CẠNH `__file__` (tức shim kia) — cả chuỗi phải chạy."""
    gid = setup(tmp_path)
    env = dict(os.environ, ORCA_GRAPH_HOME=str(tmp_path / "home"))
    r = subprocess.run([sys.executable, str(ROOT / "fdk/tools/graph-viz.py"), str(tmp_path / f"{gid}.graph.json")], capture_output=True, text=True, cwd=ROOT, env=env)
    assert r.returncode == 0 and "data-reason=\"data\"" in (tmp_path / f"{gid}.graph.html").read_text(encoding="utf-8"), r.stderr
    r = subprocess.run([sys.executable, str(ROOT / "fdk/tools/graph-atlas.py"), str(tmp_path)], capture_output=True, text=True, cwd=ROOT, env=env)
    assert r.returncode == 0 and (tmp_path / "atlas.html").exists(), r.stderr
