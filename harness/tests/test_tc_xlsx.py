"""test_tc_xlsx — proof cho tc-xlsx.py (skill tc-run): extract nhiều sheet, classify ui/calc/gap/security/perf,
plan theo lô sinh PLAN qua được orca-graph build --strict, report payload đúng schema tester-kit."""
import importlib.util, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "harness/scripts/tc-xlsx.py"
_spec = importlib.util.spec_from_file_location("tcx", SCRIPT); tcx = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(tcx)

HDR = ["Test Case ID", "Test Case Description", "Test Data", "Test Steps", "Expected Result", "PIC", "Status", "Result", "Test Type", "Priority", "Severity"]
ROWS = {
    "TC - UI Cơ bản": [
        ["TC-UI-001", "[Menu] Mở màn hình danh sách, bấm nút Thêm", "—", "1. Mở menu\n2. Bấm Thêm", "Hộp thoại hiện", None, "Chưa chạy", None, "Positive", "P1", "High"],
        ["TC-UI-002", "[Menu] Nhấp đúp ô để sửa", "—", "1. Nhấp đúp", "Ô sửa hiện", None, "Chưa chạy", None, "Positive", "P2", "Medium"],
        ["TC-UI-003", "[Dự kiến] chờ nghiệp vụ", "—", "—", "—", None, "Cần làm rõ", None, "Gap-Verification", "P1", "High"],
    ],
    "TC - Công thức tính lương": [
        ["TC-CT-001", "[Lương] Tính đúng ngày công hưởng lương", "NV A 22 ngày", "1. Nhập chấm công\n2. Chạy tính", "Tổng đúng", None, "N/A", None, "Positive", "P0", "Critical"],
    ],
    "TC - Security": [
        ["TC-SEC-001", "[SSO] Đăng nhập bằng tài khoản công ty", "—", "1. Vào hệ thống\n2. Đăng nhập", "Vào được", None, "Chưa chạy", None, "Positive", "P0", "High"],
    ],
    "TC - Performance": [
        ["TC-PF-001", "[Đồng bộ] thời gian hợp lý", "—", "1. Đồng bộ", "< 5 phút", None, "Chưa chạy", None, "Performance", "P1", "High"],
    ],
}


def make_xlsx(p: Path) -> None:
    import openpyxl
    wb = openpyxl.Workbook(); wb.remove(wb.active)
    for name, rows in ROWS.items():
        ws = wb.create_sheet(name); ws.append(["ghi chú"]); ws.append(HDR)
        for r in rows:
            ws.append(r)
    wb.save(p)


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=ROOT)


def test_extract_classify_plan_report(tmp_path):
    x = tmp_path / "tc.xlsx"; make_xlsx(x)
    r = run("extract", str(x), "-o", str(tmp_path / "tcs.json")); assert r.returncode == 0, r.stderr
    tcs = json.loads((tmp_path / "tcs.json").read_text())
    assert {t["id"]: t["auto"] for t in tcs} == {"TC-UI-001": "ui", "TC-UI-002": "ui", "TC-UI-003": "gap", "TC-CT-001": "calc", "TC-SEC-001": "security", "TC-PF-001": "perf"}
    r = run("classify", str(tmp_path / "tcs.json")); assert "tự động hoá UI được: 2" in r.stdout
    plan = tmp_path / "150926-demo-PLAN.md"
    r = run("plan", str(tmp_path / "tcs.json"), "--app", "Demo (http://x)", "--batch", "1", "-o", str(plan)); assert r.returncode == 0, r.stderr
    assert plan.read_text().count("### Task") == 4                     # khảo sát + 2 lô + report
    r = subprocess.run([sys.executable, str(ROOT / "harness/scripts/orca-graph.py"), "--dir", str(tmp_path), "build", str(plan), "--strict"], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0 and "4 node" in r.stdout, r.stdout + r.stderr
    g = json.loads((tmp_path / "150926-demo.graph.json").read_text())
    assert {n["id"]: n["state"] for n in g["nodes"]}["t1"] == "blocked"   # Task 1 là HITL
    res = tmp_path / "lo1.json"; res.write_text(json.dumps([{"id": "TC-UI-001", "status": "PASS", "actual": "hộp thoại hiện", "screenshot": "shots/TC-UI-001.png"}]))
    r = run("report", str(res), "--tcs", str(tmp_path / "tcs.json"), "--url", "http://x"); payload = json.loads(r.stdout)
    c = payload["cases"][0]
    assert payload["url"] == "http://x" and c["priority"] == "High" and c["complexity"] == "High" and "STATUS: PASS" in c["description"] and set(c) == {"priority", "name", "shortDesc", "description", "complexity"}


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        test_extract_classify_plan_report(Path(d))
    print("ok test_extract_classify_plan_report")
