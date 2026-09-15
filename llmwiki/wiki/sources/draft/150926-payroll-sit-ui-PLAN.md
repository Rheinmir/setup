---
type: draft
title: "Payroll (tingtingstage.coteccons.vn) — chạy 74 test case ui theo 11 lô trên phiên đăng nhập sẵn, xuất report tester-kit — PLAN thi hành"
status: proposed
tags: [plan, sit, playwright, tester-kit, orca-graph]
timestamp: 2026-09-15
---

# Payroll (tingtingstage.coteccons.vn) — 74 TC ui · 11 lô

**Goal:** chạy từng lô TC trên trình duyệt đã đăng nhập (claude-in-chrome hoặc Playwright connectOverCDP), ghi `results/<lô>.json` (PASS/FAIL/BLOCK + ảnh + actual), rồi xuất mỗi lô một report `.xlsx` tester-kit.

## Origin
Sinh bởi `tc-xlsx.py plan` từ file test case do user cung cấp (335 TC, 7 sheet); chỉ lấy loại `ui`. Phân loại là heuristic — TC bị xếp sai thì sửa nhãn `auto` trong tcs.json rồi sinh lại.

## Global constraints
- Không nhập mật khẩu/không vượt SSO; không có phiên đăng nhập → node `blocked` (HITL).
- Không thao tác phá huỷ dữ liệu thật: dừng trước Lưu/Xoá/Cập nhật → ghi `BLOCK — cần môi trường SIT riêng`, trừ khi user cho phép rõ.
- Mỗi TC → `{"id","status":"PASS|FAIL|BLOCK","actual","screenshot","evidence":[…]}`; verify của lô = đủ số TC và status hợp lệ.
- Report: `tao_report_test` (tester-kit) — priority P0/P1→High, P2→Medium, P3→Low; description = steps + expected + ACTUAL + status.

## File structure
- `scratchpad/150926-payroll-sit-ui/app.json` · `results/<lô>.json` · `shots/` · `report-<lô>.xlsx` · `summary.md`

### Task 1: Khảo sát app — URL, menu, phiên đăng nhập

**Kind:** research
**Mode:** hitl
**Files:**
- Tạo: `scratchpad/150926-payroll-sit-ui/app.json`
**Interfaces:**
- Consumes: URL do user cung cấp; tab trình duyệt đã đăng nhập.
- Produces: `app.json = {url, logged_in, menus}`.

**Depends:** —

- [ ] **Step 1:** mở URL trong tab mới, xác nhận không phải trang login; ghi selector các menu.

```json
{"url": "<URL app>", "logged_in": true, "menus": {}}
```

**Verify:** `python3 -c "import json;d=json.load(open('scratchpad/150926-payroll-sit-ui/app.json'));assert d['logged_in'] and d['url'].startswith('http')"`

### Task 2: Lô 1 — TC - UI, Tích hợp & Báo cáo — TC-TH-086…TC-TH-004

**Kind:** test
**Files:**
- Tạo: `scratchpad/150926-payroll-sit-ui/results/lo1.json`
**Interfaces:**
- Consumes: `app.json` (Task 1).
- Produces: `results/lo1.json` 8 mục: TC-TH-086, TC-TH-085, TC-TH-094, TC-TH-088, TC-TH-090, TC-TH-083, TC-TH-001, TC-TH-004.

**Depends:** Task 1

- [ ] **Step 1:** với mỗi TC: làm theo Test Steps, chụp ảnh `shots/<id>.png`, so Expected Result → status; dừng trước thao tác phá huỷ.

```json
{"id": "TC-TH-086", "status": "PASS|FAIL|BLOCK", "actual": "…", "screenshot": "shots/TC-TH-086.png", "evidence": []}
```

**Verify:** `python3 -c "import json;r=json.load(open('scratchpad/150926-payroll-sit-ui/results/lo1.json'));assert len(r)==8 and all(x['status'] in ('PASS','FAIL','BLOCK') for x in r)"`

### Task 3: Lô 2 — TC - UI, Tích hợp & Báo cáo — TC-TH-006…TC-TH-022

**Kind:** test
**Files:**
- Tạo: `scratchpad/150926-payroll-sit-ui/results/lo2.json`
**Interfaces:**
- Consumes: `app.json` (Task 1).
- Produces: `results/lo2.json` 8 mục: TC-TH-006, TC-TH-012, TC-TH-013, TC-TH-016, TC-TH-087, TC-TH-111, TC-TH-112, TC-TH-022.

**Depends:** Task 1

- [ ] **Step 1:** với mỗi TC: làm theo Test Steps, chụp ảnh `shots/<id>.png`, so Expected Result → status; dừng trước thao tác phá huỷ.

```json
{"id": "TC-TH-006", "status": "PASS|FAIL|BLOCK", "actual": "…", "screenshot": "shots/TC-TH-006.png", "evidence": []}
```

**Verify:** `python3 -c "import json;r=json.load(open('scratchpad/150926-payroll-sit-ui/results/lo2.json'));assert len(r)==8 and all(x['status'] in ('PASS','FAIL','BLOCK') for x in r)"`

### Task 4: Lô 3 — TC - UI, Tích hợp & Báo cáo — TC-TH-025…TC-TH-095

**Kind:** test
**Files:**
- Tạo: `scratchpad/150926-payroll-sit-ui/results/lo3.json`
**Interfaces:**
- Consumes: `app.json` (Task 1).
- Produces: `results/lo3.json` 8 mục: TC-TH-025, TC-TH-026, TC-TH-098, TC-TH-027, TC-TH-031, TC-TH-032, TC-TH-084, TC-TH-095.

**Depends:** Task 1

- [ ] **Step 1:** với mỗi TC: làm theo Test Steps, chụp ảnh `shots/<id>.png`, so Expected Result → status; dừng trước thao tác phá huỷ.

```json
{"id": "TC-TH-025", "status": "PASS|FAIL|BLOCK", "actual": "…", "screenshot": "shots/TC-TH-025.png", "evidence": []}
```

**Verify:** `python3 -c "import json;r=json.load(open('scratchpad/150926-payroll-sit-ui/results/lo3.json'));assert len(r)==8 and all(x['status'] in ('PASS','FAIL','BLOCK') for x in r)"`

### Task 5: Lô 4 — TC - UI, Tích hợp & Báo cáo — TC-TH-035…TC-TH-046

**Kind:** test
**Files:**
- Tạo: `scratchpad/150926-payroll-sit-ui/results/lo4.json`
**Interfaces:**
- Consumes: `app.json` (Task 1).
- Produces: `results/lo4.json` 8 mục: TC-TH-035, TC-TH-037, TC-TH-038, TC-TH-041, TC-TH-042, TC-TH-044, TC-TH-045, TC-TH-046.

**Depends:** Task 1

- [ ] **Step 1:** với mỗi TC: làm theo Test Steps, chụp ảnh `shots/<id>.png`, so Expected Result → status; dừng trước thao tác phá huỷ.

```json
{"id": "TC-TH-035", "status": "PASS|FAIL|BLOCK", "actual": "…", "screenshot": "shots/TC-TH-035.png", "evidence": []}
```

**Verify:** `python3 -c "import json;r=json.load(open('scratchpad/150926-payroll-sit-ui/results/lo4.json'));assert len(r)==8 and all(x['status'] in ('PASS','FAIL','BLOCK') for x in r)"`

### Task 6: Lô 5 — TC - UI, Tích hợp & Báo cáo — TC-TH-113…TC-TH-053

**Kind:** test
**Files:**
- Tạo: `scratchpad/150926-payroll-sit-ui/results/lo5.json`
**Interfaces:**
- Consumes: `app.json` (Task 1).
- Produces: `results/lo5.json` 8 mục: TC-TH-113, TC-TH-047, TC-TH-048, TC-TH-049, TC-TH-050, TC-TH-051, TC-TH-052, TC-TH-053.

**Depends:** Task 1

- [ ] **Step 1:** với mỗi TC: làm theo Test Steps, chụp ảnh `shots/<id>.png`, so Expected Result → status; dừng trước thao tác phá huỷ.

```json
{"id": "TC-TH-113", "status": "PASS|FAIL|BLOCK", "actual": "…", "screenshot": "shots/TC-TH-113.png", "evidence": []}
```

**Verify:** `python3 -c "import json;r=json.load(open('scratchpad/150926-payroll-sit-ui/results/lo5.json'));assert len(r)==8 and all(x['status'] in ('PASS','FAIL','BLOCK') for x in r)"`

### Task 7: Lô 6 — TC - UI, Tích hợp & Báo cáo — TC-TH-054…TC-TH-061

**Kind:** test
**Files:**
- Tạo: `scratchpad/150926-payroll-sit-ui/results/lo6.json`
**Interfaces:**
- Consumes: `app.json` (Task 1).
- Produces: `results/lo6.json` 8 mục: TC-TH-054, TC-TH-055, TC-TH-056, TC-TH-057, TC-TH-058, TC-TH-059, TC-TH-060, TC-TH-061.

**Depends:** Task 1

- [ ] **Step 1:** với mỗi TC: làm theo Test Steps, chụp ảnh `shots/<id>.png`, so Expected Result → status; dừng trước thao tác phá huỷ.

```json
{"id": "TC-TH-054", "status": "PASS|FAIL|BLOCK", "actual": "…", "screenshot": "shots/TC-TH-054.png", "evidence": []}
```

**Verify:** `python3 -c "import json;r=json.load(open('scratchpad/150926-payroll-sit-ui/results/lo6.json'));assert len(r)==8 and all(x['status'] in ('PASS','FAIL','BLOCK') for x in r)"`

### Task 8: Lô 7 — TC - UI, Tích hợp & Báo cáo — TC-TH-062…TC-TH-063

**Kind:** test
**Files:**
- Tạo: `scratchpad/150926-payroll-sit-ui/results/lo7.json`
**Interfaces:**
- Consumes: `app.json` (Task 1).
- Produces: `results/lo7.json` 2 mục: TC-TH-062, TC-TH-063.

**Depends:** Task 1

- [ ] **Step 1:** với mỗi TC: làm theo Test Steps, chụp ảnh `shots/<id>.png`, so Expected Result → status; dừng trước thao tác phá huỷ.

```json
{"id": "TC-TH-062", "status": "PASS|FAIL|BLOCK", "actual": "…", "screenshot": "shots/TC-TH-062.png", "evidence": []}
```

**Verify:** `python3 -c "import json;r=json.load(open('scratchpad/150926-payroll-sit-ui/results/lo7.json'));assert len(r)==2 and all(x['status'] in ('PASS','FAIL','BLOCK') for x in r)"`

### Task 9: Lô 8 — TC - UI Sửa công thức (Auto) — TC-AU-001…TC-AU-008

**Kind:** test
**Files:**
- Tạo: `scratchpad/150926-payroll-sit-ui/results/lo8.json`
**Interfaces:**
- Consumes: `app.json` (Task 1).
- Produces: `results/lo8.json` 8 mục: TC-AU-001, TC-AU-002, TC-AU-003, TC-AU-004, TC-AU-005, TC-AU-006, TC-AU-007, TC-AU-008.

**Depends:** Task 1

- [ ] **Step 1:** với mỗi TC: làm theo Test Steps, chụp ảnh `shots/<id>.png`, so Expected Result → status; dừng trước thao tác phá huỷ.

```json
{"id": "TC-AU-001", "status": "PASS|FAIL|BLOCK", "actual": "…", "screenshot": "shots/TC-AU-001.png", "evidence": []}
```

**Verify:** `python3 -c "import json;r=json.load(open('scratchpad/150926-payroll-sit-ui/results/lo8.json'));assert len(r)==8 and all(x['status'] in ('PASS','FAIL','BLOCK') for x in r)"`

### Task 10: Lô 9 — TC - UI Sửa công thức (Auto) — TC-AU-009…TC-AU-012

**Kind:** test
**Files:**
- Tạo: `scratchpad/150926-payroll-sit-ui/results/lo9.json`
**Interfaces:**
- Consumes: `app.json` (Task 1).
- Produces: `results/lo9.json` 4 mục: TC-AU-009, TC-AU-010, TC-AU-011, TC-AU-012.

**Depends:** Task 1

- [ ] **Step 1:** với mỗi TC: làm theo Test Steps, chụp ảnh `shots/<id>.png`, so Expected Result → status; dừng trước thao tác phá huỷ.

```json
{"id": "TC-AU-009", "status": "PASS|FAIL|BLOCK", "actual": "…", "screenshot": "shots/TC-AU-009.png", "evidence": []}
```

**Verify:** `python3 -c "import json;r=json.load(open('scratchpad/150926-payroll-sit-ui/results/lo9.json'));assert len(r)==4 and all(x['status'] in ('PASS','FAIL','BLOCK') for x in r)"`

### Task 11: Lô 10 — TC - UI Cơ bản & Thao tác — TC-UI-001…TC-UI-009

**Kind:** test
**Files:**
- Tạo: `scratchpad/150926-payroll-sit-ui/results/lo10.json`
**Interfaces:**
- Consumes: `app.json` (Task 1).
- Produces: `results/lo10.json` 6 mục: TC-UI-001, TC-UI-002, TC-UI-005, TC-UI-006, TC-UI-008, TC-UI-009.

**Depends:** Task 1

- [ ] **Step 1:** với mỗi TC: làm theo Test Steps, chụp ảnh `shots/<id>.png`, so Expected Result → status; dừng trước thao tác phá huỷ.

```json
{"id": "TC-UI-001", "status": "PASS|FAIL|BLOCK", "actual": "…", "screenshot": "shots/TC-UI-001.png", "evidence": []}
```

**Verify:** `python3 -c "import json;r=json.load(open('scratchpad/150926-payroll-sit-ui/results/lo10.json'));assert len(r)==6 and all(x['status'] in ('PASS','FAIL','BLOCK') for x in r)"`

### Task 12: Lô 11 — TC - Cấu hình & Phân quyền — TC-CFG-001…TC-CFG-009

**Kind:** test
**Files:**
- Tạo: `scratchpad/150926-payroll-sit-ui/results/lo11.json`
**Interfaces:**
- Consumes: `app.json` (Task 1).
- Produces: `results/lo11.json` 6 mục: TC-CFG-001, TC-CFG-004, TC-CFG-006, TC-CFG-007, TC-CFG-008, TC-CFG-009.

**Depends:** Task 1

- [ ] **Step 1:** với mỗi TC: làm theo Test Steps, chụp ảnh `shots/<id>.png`, so Expected Result → status; dừng trước thao tác phá huỷ.

```json
{"id": "TC-CFG-001", "status": "PASS|FAIL|BLOCK", "actual": "…", "screenshot": "shots/TC-CFG-001.png", "evidence": []}
```

**Verify:** `python3 -c "import json;r=json.load(open('scratchpad/150926-payroll-sit-ui/results/lo11.json'));assert len(r)==6 and all(x['status'] in ('PASS','FAIL','BLOCK') for x in r)"`

### Task 13: Xuất 11 report tester-kit + tổng hợp

**Kind:** docs
**Files:**
- Tạo: `scratchpad/150926-payroll-sit-ui/report-lo1.xlsx`, `scratchpad/150926-payroll-sit-ui/report-lo2.xlsx`, `scratchpad/150926-payroll-sit-ui/report-lo3.xlsx`, `scratchpad/150926-payroll-sit-ui/report-lo4.xlsx`, `scratchpad/150926-payroll-sit-ui/report-lo5.xlsx`, `scratchpad/150926-payroll-sit-ui/report-lo6.xlsx`, `scratchpad/150926-payroll-sit-ui/report-lo7.xlsx`, `scratchpad/150926-payroll-sit-ui/report-lo8.xlsx`, `scratchpad/150926-payroll-sit-ui/report-lo9.xlsx`, `scratchpad/150926-payroll-sit-ui/report-lo10.xlsx`, `scratchpad/150926-payroll-sit-ui/report-lo11.xlsx`, `scratchpad/150926-payroll-sit-ui/summary.md`
**Interfaces:**
- Consumes: mọi `results/*.json`.
- Produces: report xlsx mỗi lô + `summary.md` (PASS/FAIL/BLOCK theo lô, TC cần người).

**Depends:** Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12

- [ ] **Step 1:** `tc-xlsx.py report results/<lô>.json --url <URL>` in payload → gọi `tao_report_test` → chép xlsx về; viết summary.

```json
{"url": "<URL app>", "cases": [{"priority": "High", "name": "TC-…", "shortDesc": "…", "description": "Steps…\nExpected…\nActual…\nStatus: PASS", "complexity": "Medium"}]}
```

**Verify:** `ls scratchpad/150926-payroll-sit-ui/report-lo1.xlsx scratchpad/150926-payroll-sit-ui/report-lo2.xlsx scratchpad/150926-payroll-sit-ui/report-lo3.xlsx scratchpad/150926-payroll-sit-ui/report-lo4.xlsx scratchpad/150926-payroll-sit-ui/report-lo5.xlsx scratchpad/150926-payroll-sit-ui/report-lo6.xlsx scratchpad/150926-payroll-sit-ui/report-lo7.xlsx scratchpad/150926-payroll-sit-ui/report-lo8.xlsx scratchpad/150926-payroll-sit-ui/report-lo9.xlsx scratchpad/150926-payroll-sit-ui/report-lo10.xlsx scratchpad/150926-payroll-sit-ui/report-lo11.xlsx scratchpad/150926-payroll-sit-ui/summary.md`
