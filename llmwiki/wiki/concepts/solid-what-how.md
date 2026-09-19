---
type: concept
title: "SWH (solid-what-how/1) — chuẩn bắt buộc WHAT/HOW cho mọi skill native"
status: active
tags: [skills, standard, solid, contract, swh, conformance]
timestamp: 2026-09-19
---

# SWH — mỗi skill có WHAT (lời hứa) và HOW (cách thực hiện lời hứa)

**SWH** (`solid-what-how/1`) là profile thiết kế nội bộ đặt lên trên cách đóng gói `SKILL.md` của Agent Skills. Mọi skill **native** (framework tự viết, sở hữu) tạo mới hoặc chuẩn hoá PHẢI có hai lớp logic. Thiếu một lớp là blocking finding: skill đó chưa được nghiệm thu, chưa được phát hành. Skill ngoài (kéo từ upstream) nằm ngoài phạm vi migrate, xem [[adapt-modes]].

> WHAT là lời hứa của skill. HOW là cách thực hiện lời hứa. Nhánh optional được phép thêm cách làm, không được âm thầm thay lời hứa.

## WHAT — lớp trừu tượng (bắt buộc)

| Mục | Câu hỏi phải trả lời |
|---|---|
| Purpose + context/trigger | Skill giúp xong việc gì, khi nào áp dụng, ví dụ trigger |
| Non-goals | Việc dễ hiểu nhầm nhưng không thuộc skill |
| Mental model | Thực thể, quan hệ, luồng khái niệm (vd `Requirement → Ticket → Evidence`) |
| Input / output contract | Cần gì, field nào optional, thiếu thì sao; giao gì, "xong" nghĩa là gì |
| Rules (có ID, mức MUST/SHOULD/MAY) | Bất biến không được phá dù chọn HOW nào |
| Capabilities | Năng lực trừu tượng cần đọc/ghi/kiểm; KHÔNG ghi cứng tên CLI/provider (DIP) |
| Failure boundaries | Khi nào clarify / partial / blocked / failed / cancelled |

## HOW — lớp thực thi (bắt buộc)

Preflight → main path có step ID (input · action · output · exit) → branches (guard, requiredness, skip, failure, rejoin; không có thì ghi rõ "không có nhánh phụ") → error/retry/stop có trần → validation (phần nào kiểm bằng code, phần nào cần review) → **ít nhất một ví dụ positive và một ví dụ boundary/failure** có expected result → delivery.

Ba loại bước: `deterministic` (code/rule trên input đã pin), `judgment` (agent đề xuất theo rubric, có validator), `effect` (tác động state ngoài, cần quyền và reconcile). "Luồng tất định" nghĩa là transitions, guards, checks, điều kiện dừng xác định rõ, không phải model ra cùng chữ.

## SOLID áp vào skill (ánh xạ đề xuất, không phải định nghĩa của Uncle Bob)

- **S**: một năng lực, một lý do thay đổi. Không tách theo từng động từ.
- **O**: mở rộng ở extension point đã khai, core contract giữ ổn định; sửa bug core vẫn được.
- **L**: implementation thay thế giữ input domain, output semantics, failure và quyền; không chỉ giống JSON shape.
- **I**: workflow chỉ phụ thuộc phần contract/tool nó cần (đọc tách ghi tách publish).
- **D**: WHAT nói năng lực trừu tượng; HOW/adapter bind công cụ cụ thể.

## Hai profile đóng gói và hai mức bảo đảm

- **Compact**: một `SKILL.md` có `## WHAT` + `## HOW`. Mặc định cho hầu hết skill; không tạo thư mục rỗng cho đủ bộ.
- **Expanded**: `SKILL.md` giữ purpose, invariants và bảng routing có điều kiện, tới `references/how-main.md`, `references/branches/*.md`. Invariant toàn skill không được giấu trong file nhánh.
- **Documented** vs **enforced**: skill chỉ được host đọc như Markdown thì ghi documented, không claim enforced. Metadata tự khai "compliant" không phải receipt.

## Lint: cấu trúc ≠ hành vi

Blocking rules SWH-001…014 (thiếu WHAT/HOW, thiếu contract, thiếu main path/exit, branch thiếu guard/rejoin, thiếu ví dụ positive+boundary, unknown bị coi là false để bỏ gate…). Linter trả `review_required` cho điều không chứng minh được bằng regex, **không suy ra PASS vì regex không thấy lỗi**. Trong overstack, lint cấu trúc bổ sung cho [[skill-craft]] (đo hình dạng) và `skill-health --fidelity` (đo bảo chân).

## Áp vào overstack

- Phạm vi migrate = skill **native** trong `skills/`. 23 skill kéo từ upstream (taste-skill, caveman, find-skills, last30days, agent-reach) chuyển vào category riêng `skills/external/`, vẫn cài xuống downstream qua `npx skills add` (CLI quét sâu một cấp dưới `skills/`), không viết lại theo SWH vì mỗi lần kéo upstream sẽ đè mất. hallmark, fable5 và i-have-adhd có gốc upstream nhưng đã sửa nhiều ở local nên tính là native (user chốt 19/09/2026).
- Migrate giữ nguyên hành vi: chỉ sắp lại nội dung đã có vào WHAT/HOW, bổ sung contract/ví dụ còn thiếu, không đổi scope (PRD §15.2).

## Reuse Layer (v1.1) — skill kế tiếp kế thừa phần đã chuẩn hoá

Lời hứa: lần tạo skill sau tái dùng được workflow, contract, test và cách xử lý lỗi đã chuẩn hoá của lần trước, nên **chi phí biên** (MC, chi phí tăng thêm cho một episode mới) có thể giảm. Đây là giả thuyết phải đo, không phải bảo đảm: tổng chi phí chia đều (AC) giảm không chứng minh MC giảm.

- **Sáu loại tài sản:** pattern (bài toán lặp + bất biến), template (khung có tham số typed), component (một trách nhiệm), test pack, recipe (skill này ghép gì, pin version + hash), skill instance.
- **Kế thừa bằng composition + delta**, không bằng chuỗi override: skill = base template + component chọn + domain delta. Core contract đóng băng; chỉ đổi qua tham số có schema, slot có contract, nhánh đã khai, và delta có test riêng. Delta không được giảm bảo đảm của core.
- **Mỗi lần tạo skill ghi một `reuse_decision`:** reuse, compose, scratch hoặc catalog_unavailable, kèm lý do. Không ép reuse để tăng tỉ lệ; mẫu không có lợi thì chọn scratch, và scratch vẫn phải qua mọi cổng SWH.
- **Recipe pin hash chính xác**; bytes đổi mà cùng version thì hash mismatch và report cũ mất hiệu lực. Recipe còn `lock_status: unresolved` hoặc còn placeholder `${...}` thì không được phát hành.
- **Đo trung thực:** thiếu baseline thì ghi `benefit_unproven`; episode thất bại vẫn tính vào mẫu số.
- **Hiện thực trong overstack (mức local MVP, 19/09/2026):** catalog `fdk/skill-catalog/` (P01 · P02 candidate · P03, template T00 compact · T01 evidence-to-artifact · T02 pure-transform), tool `fdk/tools/skill-reuse.py` (search · render · verify · episode · report), `new-skill.py --from` ghi recipe vào `fdk/skill-catalog/recipes/`, `swh-lint` thêm SWH-PLACEHOLDER và SWH-LOCK. Chưa làm: promotion tự động, upgrade/quarantine lan truyền, pilot đo chi phí có baseline.

## Origin
- **Source:** `raw/prd/Skill-Design-Standard-SOLID-WHAT-HOW-PRD.md` (PRD v1.0) và `raw/prd/Skill-Design-Standard-SOLID-WHAT-HOW-PRD (1).md` (v1.1 Reuse Layer), 19/09/2026, tóm tắt tại [[190926-skill-design-standard-swh-prd]].
- **Date:** 2026-09-19
