---
type: eval
id: fdk-gate-git-env
title: "fdk-gate đỏ khi push mà chạy tay thì xanh — vì sao"
input: "Chạy tay python3 harness/scripts/fdk-gate.py thì đạt 21/21, nhưng git push qua hook pre-push lại đỏ ở harness-doctor, graph-engineering, BNAL self-tests với Traceback, và index git bị xoá sạch. Nguyên nhân là gì và sửa ở đâu?"
expected: "Git export GIT_DIR, GIT_INDEX_FILE và các biến GIT_* khác vào môi trường của hook pre-push. fdk-gate truyền nguyên môi trường đó cho từng bước, nên các self-test dựng repo tạm bằng git -C /tmp/x init/commit thực ra thao tác trên repo thật: commit lén vào repo ngoài, ghi đè index, tạo nhánh rác. Sửa một chỗ trong hàm run() của fdk-gate: gỡ mọi biến GIT_* khỏi env của subprocess, chỉ giữ GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL, GIT_COMMITTER_NAME, GIT_COMMITTER_EMAIL. Tái hiện: GIT_DIR=$(git rev-parse --git-dir) python3 harness/scripts/fdk-gate.py; test khoá hồi quy là harness/tests/fdk-gate-git-env-test.sh."
asserts:
  - 'icontains:GIT_DIR'
  - 'regex:(?i)hook|pre-push'
  - 'regex:(?i)env|môi trường'
  - 'regex:(?i)run\(\)|subprocess'
rubric: "ĐẠT nếu chỉ ra biến GIT_* do git export trong hook rò vào subprocess của gate, khiến thao tác git trong repo tạm trúng repo thật, và sửa bằng cách lọc env ở MỘT chỗ (run()). KHÔNG đạt nếu đổ cho flaky, cho máy CI, hoặc đề xuất --no-verify."
---

# Golden: fdk-gate-git-env

Bài học của PR #173: cổng chạy khác nhau trong hook và khi chạy tay vì môi trường git của hook rò vào các bước con.

## Origin
- Phiên 2601b4e7, 27/09/2026 — push lên fork bị pre-push gate chặn 3/21 với Traceback; tái hiện bằng `GIT_DIR=$(git rev-parse --git-dir) python3 harness/scripts/fdk-gate.py` (3/21 đỏ + index bị wipe). Sửa ở `09f92cc4`. Test khoá hồi quy `harness/tests/fdk-gate-git-env-test.sh` thêm 02/10/2026: bản trước sửa (`9ca37051`) đỏ 2 check, repo ngoài bị commit lén 1 → 2.
