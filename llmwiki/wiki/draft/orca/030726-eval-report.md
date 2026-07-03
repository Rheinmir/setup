---
type: draft
title: "030726-eval-report — distill phiên dev phân mảnh làm stress-test /fdk"
status: proposed
tags: [orca-eval, eval-report, fdk-hardening, stress-test]
timestamp: 2026-07-03
---

# 030726-eval-report
**Type:** draft
**Status:** proposed
**Tags:** orca-eval, eval-report, fdk-hardening, stress-test
**Proposed:** 2026-07-03
**Scope:** session hiện tại `b73d2c47-…jsonl` — MỘT phiên dev phân mảnh điển hình (thói quen "quên rồi quyết lại"), dùng làm stress-test cho /fdk.

## Chữ ký phiên (vì sao là stress-test)
~30 prompt, **8 chủ đề nhảy qua lại** trong một phiên: council-font → self-index-engine → medic → whiteboard → council-redesign → release → ship-skill → orca-eval. **6 vòng feedback design** trên cùng một artifact (council-report 013→018). Nhiều lần user **đổi ý / bổ sung ràng buộc giữa chừng** ("nhu cầu từ tôi", "giống wiki-graph cơ", "tên khác đi"). Đây là dạng làm việc thật: không tuyến tính, hay quên, sửa tới lui.

## Best practices (cái đã GIỮ hệ đứng vững)
| # | Tín hiệu | Loại | Bằng chứng |
|---|----------|------|-----------|
| 1 | Sửa ở **ENGINE/template**, không hand-edit output → mọi report re-render đều hưởng | Win | council-report font/lens/i18n vá 1 lần trong `render_report_html`, 013→018 tự đúng |
| 2 | **`medic` last-line** bắt drift lặp lại | Win | bắt capabilities-stale 3 lần + validator-drift + **cú sync SAI HƯỚNG của chính agent** (R7 rail-đen) → khôi phục |
| 3 | **Điểm số trung thực** khi bị chất vấn | Win | "hallucinate thấp thế tính sao" → thừa nhận abstain-bias; "0.842 thua rag?" → full-space 0.727 + N nhỏ, không overclaim |
| 4 | **Council chọn đề thi** chống ludic-fallacy | Win | benchmark ngoài-mẫu lộ 3 defect thật → vá self-contained |
| 5 | **Kim chỉ nam ghi vào SKILL (travel)**, không chỉ memory máy-local | Win | fdk hub-UX principles vào `skills/fdk/SKILL.md` |

## Friction / anti-pattern (cái LÀM CHẬM, dễ sai)
| # | Tín hiệu | Loại | Bằng chứng |
|---|----------|------|-----------|
| F1 | **Hand-author thay vì chạy generator** (phá kỷ luật "sinh-bằng-code") | Correction | "sao lại ra docs riêng không tuân thủ kỷ luật chạy file python" — dated HTML thay vì CLI |
| F2 | **Reinvent thay vì reuse engine** khi user nói "giống X" | Correction | whiteboard dựng layout thẻ tĩnh → user "muốn giống wiki-graph"; phải dựng lại qua build-wiki-graph |
| F3 | **Regression khi đổi convention** | Correction | seat-id vs persona-name; report toàn "seat-N" mất lens |
| F4 | **Sync drift SAI HƯỚNG** — ghi đè bản đang-cắn bằng bản cũ | Friction | copy src→hooks-copy làm R7 rail-đen; medic bắt, phải revert |
| F5 | **Thêm tool nhưng quên regen capabilities/docs** | Friction | medic báo build-capabilities stale 3 lần liên tiếp mỗi lần thêm .py |
| F6 | **Lẫn ngôn ngữ trong UI sinh ra** | Correction | "Winner/Most contested (Anh) cạnh Đồng thuận (Việt)" |
| F7 | **Over-correction trong design** | Correction | vá wall-of-text → bold cả khối (xấu hơn); viền trái màu = AI-slop; phải sửa lại |
| F8 | **selftest/verify bỏ quên** sau khi sửa engine | Friction | `re` import lỗi làm selftest FAIL; "File has not been read yet" |

## Đề xuất action — làm /fdk CHỊU được stress-test này
| # | Finding | Action | Phương án cụ thể |
|---|---------|--------|------------------|
| A1 | F1 hand-author phá kỷ luật generator | `add-rule`/`update-fdk` | Rule fdk: **artifact có generator thì PHẢI sinh qua generator** vào path canonical; hand-author = vi phạm. medic thêm probe "artifact khớp generator" (mở rộng `--check`). |
| A2 | F2 reinvent khi có engine | `update-fdk` | Kim chỉ nam fdk: user nói "giống X" / có engine sẵn (build-wiki-graph…) → **reuse engine trước khi tự dựng**. Pre-flight #3 mở rộng: "grep engine cùng loại". |
| A3 | F4 sync sai hướng | `add-guard` | `medic`/harness-doctor: khi phát hiện drift, **chỉ ra bản NÀO đang-cắn** (chạy bite-test cả 2) trước khi gợi ý sync — không đoán hướng. |
| A4 | F5 quên regen sau khi thêm tool | `add-hook`/`update-fdk` | Stop-hook đã chạy build-* ; bổ sung: thêm `.py` vào fdk/tools → **auto regen capabilities**. Hoặc: **chạy `medic` là bước kết-thúc-mặc-định** của mọi phiên đụng framework (fdk pre-flight #5). |
| A5 | F8 quên verify sau sửa engine | `update-fdk` | Pre-flight #5 fdk: sửa engine (council.py/build-*.py/validator) → **BẮT BUỘC selftest + medic** trước khi báo "xong". |
| A6 | F3/F6/F7 regression + lẫn ngôn ngữ + over-design | `keep`+`update-fdk` | Đã có nguyên tắc (fix-at-engine, HTML-gloss). Bổ sung: **đổi convention hiển thị → re-render + mắt-người/screenshot 1 mẫu** trước khi coi là xong. |
| A7 | Toàn cục | `keep` | Mô hình **"agent tự phá kỷ luật → medic/user bắt → vá gốc"** chính là anti-fragile đang chạy. Giữ + tăng coverage medic (5/17→17/17) để bắt sớm hơn. |

## Điểm cốt lõi cho /fdk (một câu)
Stress-test phơi bày: **agent dưới phiên phân mảnh HAY (a) hand-author thay vì generate, (b) reinvent thay vì reuse, (c) quên verify/regen sau khi sửa.** Ba cái này đều là **thiếu một vòng phản hồi tự-động** — đúng thứ `medic` + rule-generator + pre-flight-verify lấp. Hardening = **biến 3 thói quen quên đó thành cổng tự-cắn**, không dựa trí nhớ agent.

## Qua đánh giá /council (report `council-report-020-seed42.html`)
Roster: Linus · Taleb · Munger · Rams · Lão Tử. Winner **Lão Tử** (mean 1.67); gây tranh cãi nhất: **Taleb/A3**. Chairman chốt:

**Đòn bẩy gốc:** KHÔNG thêm 7 luật (dựa trí nhớ → thành giấy). Biến **medic thành GƯƠNG-SOI-CUỐI-PHIÊN khi phiên đụng framework** → 3 thói quen quên tự lộ, khỏi luật rời.

**LÀM (2 cổng tự-cắn cứng):**
- **A1** generator-only + medic probe phát hiện artifact-tay (chặn hand-author TRƯỚC khi lỗi).
- **A7** medic coverage 5/17→17/17 (cơ chế cho mọi check khác tồn tại).
- **A4+A5 gộp** = tiêu-chí-done: "sửa engine/đổi convention framework → chạy medic trước khi coi xong".
- **A3 HẤP THỤ vào A7** làm 1 hạng mục coverage ("so bản đang-cắn 2 chiều trước sync, cắn nếu lệch hướng") — không luật độc lập; giữ vì bất khả nghịch (agent đã sync sai hướng thật trong phiên).

**GỘP thành phụ lục /fdk (không rule chặn):** A2 (reuse-trước) + A6 (xem-mẫu khi đổi convention) — vi phạm chỉ lãng phí, không bất khả nghịch.

**KHOAN:** không "medic mặc định MỌI phiên" (Linus: theater). Chỉ tự kích khi **hook nhận diện phạm vi đụng framework** (file trong `fdk/` hoặc core `llmwiki/`).

**Bước tiếp (propose→gate):** (1) hook "framework-touch detector" kích medic-cuối-phiên; (2) mở rộng A7 5/17→17/17 kèm sync-direction-check (hấp thụ A3); (3) A2/A6 viết vào hướng dẫn /fdk.

## Origin
- **Sessions:** `~/.claude/projects/-Users-giatran-orca-setup-setup/b73d2c47-27fe-4f86-8a29-0802a2e7e2e3.jsonl`
- **Council:** `llmwiki/html/council/council-report-020-seed42.html`
- **Generated by:** /orca-eval
