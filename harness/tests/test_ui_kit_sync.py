"""test_ui_kit_sync — phần tất định của skills/ui-kit-from-code/references/sync-kit.py (GH#186), không cần mạng:
id dự án, hash bỏ meta, số phiên bản, v1 bất biến khi ra v2, chạy lại không đổi thì không tạo bản mới."""
import importlib.util, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("sync_kit", ROOT / "skills/ui-kit-from-code/references/sync-kit.py")
sk = importlib.util.module_from_spec(spec); spec.loader.exec_module(sk)


def test_kit_id(tmp_path):
    assert sk.kit_id("https://www.drafted.ai/learn/x") == "drafted-ai"
    assert sk.kit_id("http://127.0.0.1:8765/fb.html") == "127-0-0-1"
    subprocess.run(["git", "init", "-q", str(tmp_path / "r")], check=True)
    assert sk.kit_id(str(tmp_path / "r")) == "r-local"
    subprocess.run(["git", "-C", str(tmp_path / "r"), "remote", "add", "origin", "git@github.com:LnkiAI/M3E-Canvas.git"], check=True)
    assert sk.kit_id(str(tmp_path / "r")) == "lnkiai-m3e-canvas"


def test_hash_ignores_id_meta():
    html = "<html><head><title>k</title></head><body>x</body></html>"
    assert sk.kit_hash(sk.stamp_id(html, "a")) == sk.kit_hash(html)
    assert sk.stamp_id(sk.stamp_id(html, "a"), "a").count("ui-kit-id") == 1


def test_versions(tmp_path):
    kit = "<html><head></head><body>--primary:#123</body></html>"
    meta = {"source_commit": "abc", "skill_version": "1.0.0"}
    assert sk.write_version(tmp_path, "p", kit, "src", meta) == (1, None)
    assert sk.write_version(tmp_path, "p", kit, "src", meta) == (None, 1)          # không đổi → không có v2
    v1 = (tmp_path / "p/v1/index.html").read_bytes()
    kit2 = kit.replace("#123", "#456")
    assert sk.write_version(tmp_path, "p", kit2, "src", meta) == (2, None)
    assert (tmp_path / "p/v1/index.html").read_bytes() == v1                          # v1 byte-for-byte
    assert "#456" in (tmp_path / "p/latest/index.html").read_text()
    assert json.loads((tmp_path / "registry.json").read_text())["p"]["latest"] == 2
    assert [x["v"] for x in json.loads((tmp_path / "p/manifest.json").read_text())["versions"]] == [1, 2]
    assert sk.write_version(tmp_path, "p", kit, "src", meta) == (3, None)           # quay về nội dung cũ vẫn là bản mới
