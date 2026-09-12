---
type: eval
id: downstream-layout-awareness
title: "Layout máy khách khác layout repo framework — agent sửa hook có biết code của mình chạy ở đâu không"
input: "Tôi đang sửa hook stop.py trong repo framework overstack. Ở một dự án khách vừa cài bằng lệnh curl bootstrap, file stamp và thư mục wiki nằm ở đâu, hook và engine chạy từ đâu, và trong code tôi phải dựng đường dẫn tới thư mục wiki và metrics thế nào để chạy đúng ở cả repo framework lẫn dự án khách? Làm sao chứng minh nó chạy đúng ở máy khách?"
expected: "Dự án khách dùng layout ẩn: .llmwiki/ (wiki ở .llmwiki/wiki, stamp ở .llmwiki/.harness-stamp) và .harness/ (poc-vendor-neutral, metrics ở .harness/metrics). Hook chạy từ bản global ~/.claude/harness/hooks (đăng ký trong ~/.claude/settings.json, chỉ bật khi thấy stamp), engine cũng ở ~/.claude/harness; dự án khách không chứa hook hay engine. Repo framework giữ llmwiki/ và harness/ trần, không bao giờ migrate. Không ghi cứng llmwiki/ hay harness/: engine đi qua overstack_paths, hook đi qua hooklib.overstack_dir / harness_dir / stamp_path / find_wiki_dir. Chứng minh bằng test chạy hook thật trong fixture layout dot (dot-layout-runtime-test.sh, HOME cô lập, cài engine từ working tree), lint bare_path_lint, và UAT curl thật (/fdk-uat)."
asserts:
  - 'contains:.llmwiki/.harness-stamp'
  - 'contains:.harness/metrics'
  - 'regex:~/\.claude/harness/hooks'
  - 'regex:(?i)(overstack_paths|stamp_path|harness_dir|overstack_dir|find_wiki_dir|project_wiki)'
  - 'regex:(?i)(dot-layout-runtime|fixture|layout dot|fdk-uat|dự án trống|project rỗng)'
rubric: "ĐẠT nếu đủ bốn ý: (1) máy khách dùng layout ẩn .llmwiki/ + .harness/, stamp ở .llmwiki/.harness-stamp; (2) hook và engine chạy từ ~/.claude/harness global; (3) cấm ghi cứng đường trần và chỉ ra resolver dùng chung; (4) chứng minh bằng cách chạy hook thật trong một dự án hay fixture layout dot, không phải chỉ chạy test trong repo framework. KHÔNG đạt nếu trả lời stamp ở llmwiki/.harness-stamp cho dự án khách, hoặc cho rằng test xanh trong repo framework là đủ."
---

# Golden: downstream-layout-awareness

Golden này đo đúng nỗi lo gốc của PLAN `110926-downstream-layout-awareness`: một phiên dev trên repo framework chỉ nhìn thấy cây `llmwiki/` + `harness/` trần, nên dễ viết và kiểm code theo cây đó, trong khi thứ thật sự chạy ở máy khách là `.llmwiki/` + `.harness/` + engine global. Trước thay đổi, chính các hook của framework đọc `llmwiki/.harness-stamp` trần và câm ở mọi dự án khách (xem [[framework-dev-antipatterns]] mục AP-7).

Năm assert là phần tất định: đáp án phải nêu đúng vị trí stamp và metrics ở máy khách, nơi hook global chạy, một resolver dùng chung, và cách chứng minh bằng môi trường đích. Rubric bắt nốt phần ngữ nghĩa mà assert không diễn tả được.

## Kết quả A/B lần đầu (2026-09-12)

Hai agent Sonnet mới, mỗi bên chỉ được đọc một bản xuất sạch của repo (không chứa golden này) cùng đúng output `session_start` của bản đó. Bên A dùng `5ad733d`, trước thay đổi, không có khối `[downstream-map]`. Bên B dùng `4f4db2e`, sau thay đổi, có khối đó. Nguyên văn câu trả lời và điểm nằm ở `harness/evals/downstream-layout-ab-120926.json`.

| Câu trả lời | Bản 1 (4 assert) | Bản 2 (5 assert) | Lỗi thật |
|---|---|---|---|
| Đối chứng dương (đáp án) | PASS 4/4 | PASS 5/5 | không |
| Đối chứng âm (câu sai điển hình) | FAIL 1/4 | FAIL 0/5 | toàn bộ |
| A — trước thay đổi | FAIL 3/4 | FAIL 4/5 | khuyên dựng `root/"harness"/"metrics"` vì "metrics luôn project-local" — đúng lỗi Task 2b đã sửa |
| B — sau thay đổi | PASS 4/4 | FAIL 4/5 | nói hook chạy từ `.llmwiki/.claude/hooks` trong dự án khách; thật ra hook chạy từ `~/.claude/harness/hooks` |

Bản 1 bị siết thành bản 2 vì hai khuyết điểm lộ ra khi chấm: assert "chứng minh" khớp cả cụm "dự án khách" có sẵn trong câu hỏi, và regex resolver thiếu `find_wiki_dir`, nên A trượt vì lý do sai còn B lọt dù sai. Bản 2 thêm hai assert khẳng định (`.harness/metrics`, `~/.claude/harness/hooks`) thay vì assert phủ định, để không phạt nhầm câu trả lời đúng có nói "không nằm ở …".

Theo rubric, cả hai bên đạt ba trên bốn ý. Ngữ cảnh mới sửa được ý (3) và (4): B dùng đúng resolver, đúng chỗ metrics, và chứng minh bằng `dot-layout-runtime-test.sh`. Nó chưa sửa được ý (2): B đọc `dot-layout-migrate-test.sh`, nơi fixture đời cũ còn ghi hook vào `.llmwiki/.claude/hooks`, và tin fixture hơn dòng bản đồ `llmwiki/.claude/hooks → ~/.claude/harness/{…,hooks}/`. Việc nên làm tiếp: khối `[downstream-map]` nói thẳng "dự án khách không chứa hook", rồi chạy lại bên B trên bản đó.

Cách dùng như một phép đo A/B: hỏi cùng câu `input` cho một agent mới ở repo trước thay đổi (`5ad733d`) và ở repo sau thay đổi (`4f4db2e`), mỗi bên kèm đúng output `session_start` mà phiên thật được bơm vào, rồi chấm cả hai bằng `harness/scripts/wikieval.py`.

## Origin
- Sinh 2026-09-12 khi nghiệm thu PLAN `llmwiki/wiki/sources/draft/110926-downstream-layout-awareness-PLAN.md` (commit `684e73b`, `4f4db2e`), theo yêu cầu bổ sung đánh giá của user sau UAT.
- Đáp án kiểm chứng bằng chạy thật: UAT canary và smoke đường chính trên dự án cài bằng curl cho thấy stamp ở `.llmwiki/.harness-stamp`, engine ở `~/.claude/harness`, và `dot-layout-runtime-test.sh` 5/5.
