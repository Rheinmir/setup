---
type: source
title: "Reprise PRD v1.0 — Personal Work Continuity: mở lại là làm tiếp; state machine Thread/Wait/Pack và luật bền state"
status: ingested
tags: [prd, reprise, state-machine, idempotency, lease, checkpoint, orca-graph]
timestamp: 2026-09-12
id: 120926-reprise-prd-work-continuity
relations:
  - {rel: informs, to: orca-graph}
  - {rel: raw, path: /Users/giatran/Downloads/Reprise-PRD-Product-Grade.md}
---

# Reprise PRD v1.0 — Personal Work Continuity

## Tóm tắt

Reprise là một sản phẩm cá nhân với lời hứa "mở lại là làm tiếp": người dùng dừng việc giữa chừng, và khi quay lại thì phần việc đã được chuẩn bị sẵn (checkpoint, pack tiếp việc, bằng chứng build). PRD dài 1.189 dòng, viết cho một fresher có thể nhận ticket mà không phải tự đoán. Với framework này, phần đáng giá nhất không phải tính năng sản phẩm mà là **bộ luật bền state** ở §5, §9.2 và §10.1, vì nó được nghĩ kỹ hơn bất cứ tool file-based nào chúng ta tự viết.

## Những luật đã được rút ra và áp vào orca-graph

Mười sáu bất biến ở §5.1 và mô tả transaction ở §9.2 đã được đối chiếu ngày 12/09/2026 khi thiết kế `/orca-graph`. Các luật được vay trực tiếp:

- **Idempotent theo operation key** (bất biến 3): retry cùng thao tác không nhân đôi checkpoint, pack, job hay receipt. Trong orca-graph, mỗi lệnh `set` mang `op_key`; op_key đã có trong sổ sự kiện thì lệnh là no-op.
- **CAS revision** (bảng `threads.revision`): hai tab cùng ghi một thread thì một bên phải thua. orca-graph có `--if-rev`.
- **Generation của job** (bất biến 9): kết quả từ thế hệ cũ không được publish. orca-graph tăng `gen` mỗi lần dispatch và chặn `done` mang gen cũ.
- **Watcher stale không tự kết luận** (bất biến 7): hết lease thì trạng thái là `unknown`, không phải `failed`; phải reconcile trước khi retry.
- **Không có provenance thì không được ghi "đã xác minh"** (bất biến 5): node chỉ đạt `done` khi lệnh verify trả 0; người báo tay được gắn `done_user_reported`.
- **Ba chiều tách nhau** của Pack (`build_state`, `freshness`, `readiness` ở §5.3): orca-graph tách `state`, `verified`, `fresh`.
- **Ghi artifact an toàn** (§9.2): temp cùng filesystem, fsync, atomic rename, rồi mới publish. Cache `graph.json` ghi đúng cách này; sổ sự kiện append + fsync.
- **Checkpoint đã ack phải sống qua crash trên cấu hình hỗ trợ, test thật không mock** (bất biến 6): test `kill -9` giữa lúc ghi trong `test_orca_graph.py`.

## Những gì cố ý không vay

SQLite WAL với `BEGIN IMMEDIATE`, quota theo profile, connector Jenkins, recipe học từ hành vi. orca-graph là tool một máy, một writer là orchestrator; JSONL cộng lockfile đủ cho vài trăm node. Đường nâng cấp lên SQLite được ghi thành marker trong proposal, không làm sớm.

## Origin

- Nguồn thô: `/Users/giatran/Downloads/Reprise-PRD-Product-Grade.md` (ngoài repo, không chép vào raw/) (user đưa ngày 12/09/2026, yêu cầu "còn về quản lý state của graph check PRD này").
- Đối chiếu và rút luật trong phiên /fdk ngày 12/09/2026; kết quả áp vào `harness/scripts/orca-graph.py` và ghi ở [[orca-graph]].
