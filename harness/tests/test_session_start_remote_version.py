"""test_session_start_remote_version — nhắc lệch bản đầu phiên (PLAN 141026-skills-split T4):
máy cũ hơn bản chuẩn (harness hoặc bộ skill) → in đúng 1 dòng `⬆ [version]`; bằng/ mới hơn → im lặng; URL hỏng → im lặng;
cache 1 lần/ngày (đổi nguồn trong ngày không hỏi lại); OVERSTACK_VERSION_NUDGE=0 tắt.
Chạy: python3 -m pytest -q harness/tests/test_session_start_remote_version.py"""
import importlib.util
import io
import json
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOKS = ROOT / "llmwiki" / ".claude" / "hooks"


def _load(tmp_home: Path):
    os.environ["OVERSTACK_HARNESS_HOME"] = str(tmp_home)
    for m in ("hooklib", "session_start"):
        sys.modules.pop(m, None)
    sys.path.insert(0, str(HOOKS))
    spec = importlib.util.spec_from_file_location("session_start", HOOKS / "session_start.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run(mod, root: Path) -> str:
    buf = io.StringIO()
    with redirect_stdout(buf):
        mod.remote_version_nudge(root)
    return buf.getvalue()


def test_nudge_when_behind_silent_when_current(tmp_path):
    home = tmp_path / "harness"
    home.mkdir()
    (home / "version.json").write_text(json.dumps({"template_version": "1.3.120"}))
    (home / "skills-version.json").write_text(json.dumps({"version": "1.0.0"}))
    src = tmp_path / "healthz.json"
    src.write_text(json.dumps({"ok": True, "harness": "1.3.127", "skills": {"version": "1.0.3", "count": 106}}))
    os.environ["OVERSTACK_VERSION_URL"] = src.as_uri()
    os.environ.pop("OVERSTACK_VERSION_NUDGE", None)
    mod = _load(home)
    out = _run(mod, tmp_path)
    assert out.count("⬆ [version]") == 1, out
    assert "v1.3.120 < bản chuẩn v1.3.127" in out and "bộ skill v1.0.0 < bản chuẩn v1.0.3" in out, out
    # cache trong ngày: đổi nguồn không hỏi lại
    src.write_text(json.dumps({"harness": "9.9.9", "skills": {"version": "9.9.9"}}))
    out2 = _run(mod, tmp_path)
    assert "v1.3.127" in out2 and "9.9.9" not in out2, out2
    # máy đã cập nhật → im lặng
    (home / "version.json").write_text(json.dumps({"template_version": "1.3.127"}))
    (home / "skills-version.json").write_text(json.dumps({"version": "1.0.3"}))
    assert _run(mod, tmp_path) == ""
    # tắt bằng env
    (home / "version.json").write_text(json.dumps({"template_version": "1.0.0"}))
    os.environ["OVERSTACK_VERSION_NUDGE"] = "0"
    assert _run(mod, tmp_path) == ""
    os.environ.pop("OVERSTACK_VERSION_NUDGE", None)


def test_fail_open_on_bad_url_and_missing_home(tmp_path):
    home = tmp_path / "harness"
    home.mkdir()
    (home / "version.json").write_text(json.dumps({"template_version": "1.0.0"}))
    os.environ["OVERSTACK_VERSION_URL"] = (tmp_path / "khong-co.json").as_uri()
    mod = _load(home)
    assert _run(mod, tmp_path) == ""
    assert not (home / ".remote-version.json").is_file() or "harness" in json.loads((home / ".remote-version.json").read_text()) or True
    # không có version.json → im lặng, không ghi cache
    empty = tmp_path / "empty-home"
    empty.mkdir()
    mod2 = _load(empty)
    assert _run(mod2, tmp_path) == ""
    assert not (empty / ".remote-version.json").exists()
    os.environ.pop("OVERSTACK_VERSION_URL", None)


if __name__ == "__main__":
    import tempfile
    for fn in (test_nudge_when_behind_silent_when_current, test_fail_open_on_bad_url_and_missing_home):
        with tempfile.TemporaryDirectory() as td:
            fn(Path(td))
    print("test_session_start_remote_version OK")
