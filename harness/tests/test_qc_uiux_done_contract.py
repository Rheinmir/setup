"""done-contract (qc-uiux): khoá DONE chống nới tiêu chí + ratchet chống vòng sau phá vòng trước."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
s = importlib.util.spec_from_file_location("done_contract", ROOT / "skills/qc-uiux/scripts/done-contract.py")
dc = importlib.util.module_from_spec(s); s.loader.exec_module(dc)


def report(tmp, flag):
    r = tmp / "r.md"
    r.write_text("# QC\n\n<!-- done:begin -->\n"
                 f"- D1: cờ còn đó — kiểm: `test -f {flag}`\n"
                 "- D2: màn đầu nói rõ bán gì (soi ảnh)\n"
                 "<!-- done:end -->\n\nphần còn lại\n", encoding="utf-8")
    return r


def test_lock_then_weakening_is_caught(tmp_path):
    r = report(tmp_path, tmp_path / "flag")
    assert dc.main(["check", str(r)]) == 1                       # chưa khoá
    assert dc.main(["lock", str(r)]) == 0 and dc.main(["check", str(r)]) == 0
    assert dc.main(["lock", str(r)]) == 0                         # khoá lại = no-op, không đổi hash
    r.write_text(r.read_text().replace("màn đầu nói rõ bán gì", "màn đầu có chữ"), encoding="utf-8")
    assert dc.main(["check", str(r)]) == 1                       # nới tiêu chí bị bắt


def test_ratchet_blocks_regression_of_earlier_round(tmp_path):
    flag = tmp_path / "flag"
    r = report(tmp_path, flag)
    dc.main(["lock", str(r)])
    assert dc.main(["pass", str(r), "D1"]) == 1                  # lệnh kiểm đỏ → không cho ghi đạt
    flag.write_text("x")
    assert dc.main(["pass", str(r), "D1", "D2"]) == 0
    assert dc.main(["status", str(r)]) == 0 and dc.main(["verify", str(r)]) == 0
    flag.unlink()                                                # vòng sau làm hỏng thứ vòng trước đã đúng
    assert dc.main(["verify", str(r)]) == 1


def test_unknown_id_and_missing_block(tmp_path):
    r = report(tmp_path, tmp_path / "flag"); dc.main(["lock", str(r)])
    assert dc.main(["pass", str(r), "D9"]) == 1
    bare = tmp_path / "b.md"; bare.write_text("không có DONE")
    try:
        dc.main(["lock", str(bare)]); assert False
    except SystemExit as e:
        assert "done:begin" in str(e)
