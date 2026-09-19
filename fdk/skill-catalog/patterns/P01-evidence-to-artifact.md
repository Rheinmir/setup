# P01 — Evidence to artifact (pattern)

Nguồn: PRD SWH v1.1 §26.1. Trạng thái: active · `limited_evidence` (seed thiết kế, chưa đo trên production).

## WHAT
| Mục | Nội dung |
|---|---|
| Mục đích | Chuyển nguồn đã đọc thành artifact kiểm được nguồn và chất lượng |
| Áp dụng | PRD → tickets, meeting notes → action list, requirements → test plan, raw → wiki page |
| Không áp dụng | Chứng minh sự kiện không có trong nguồn; tự publish thay cho file draft (dùng P02) |
| Invariants | Không bịa nguồn; tách fact/assumption; output đạt schema + domain checks; thiếu required output thì không `succeeded` |
| Abstract ports | SourceRead · Propose · DomainValidate · ArtifactWrite |
| Trade-off | Tái dùng control flow + check nền; nghĩa domain vẫn cần validator/rubric riêng |

## HOW
read/pin source → normalize evidence → propose structured draft → domain checks → repair tối đa 1 lần nếu recoverable → render requested formats → persist artifact được phép → trả receipt + limitations.

- Nhánh thiếu source: blocked, hoặc thu hẹp scope nếu user chấp nhận.
- Nhánh extra export: đã chọn thì thành required, không lặng lẽ bỏ qua.
- Positive: 3 requirement → 3 dòng coverage có ticket ref. Negative: output bỏ R02 → fail coverage.

Template hiện thực: `templates/T01-evidence-to-artifact.md`.
