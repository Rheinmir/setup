---
name: dym-harness-sdk-evals
description: "Chấm chất lượng agent bằng Strands Evals SDK (repo ngoài strands-agents/evals) — Experiment/Case/Evaluator, chấm OUTPUT/TRACE/SESSION, gate CI bằng --fail-on. CHƯA KIỂM CHỨNG: chỉ đối chiếu docs trong harness-sdk."
disable-model-invocation: true
---

# Skill: dym-harness-sdk-evals — chấm điểm agent (chưa kiểm chứng)

## When to use
- Cần điểm số chất lượng (không chỉ pass/fail hiệu ứng) cho agent Strands, hoặc chấm trace production đã có.
- **Trạng thái:** mọi thứ dưới đây lấy từ docs `site/src/content/docs/.../evals-sdk/` trong harness-sdk; code nằm ở repo `strands-agents/evals` chưa clone, chưa chạy. Coi là giả thuyết.

## Steps
1. Mô hình: **Experiment → Case → Task → Evaluator → Detector** (`how-evaluation-works.mdx:17-48`).
   - Evaluator chấm ở 3 mức: OUTPUT (câu trả lời) · TRACE (chuỗi span/tool) · SESSION (cả phiên).
   - Evaluator có loại LLM-judge và loại tất định (`evaluators/deterministic_evaluators.mdx`).
   - Detector đọc trace của run FAIL để tìm nguyên nhân (tách "có đạt không" khỏi "vì sao").
   - Simulator đóng vai user/tool cho test nhiều lượt.
2. Chấm trace production không cần chạy lại agent: trace provider lấy span OTel từ CloudWatch/Langfuse (`how-to/trace_providers.mdx`). Harness phát span khi `OTEL_TRACES_EXPORTER` được đặt.
3. Gate CI: CLI `run ... --fail-on threshold:0.8` (`cli/run.mdx:104,110`); kết quả task cache theo `case.name` (`how-to/result_caching.mdx:44`) — đổi input mà giữ tên case thì dính cache cũ.
4. Đa phương thức (design `0010`): MLLM-as-judge, Likert-5 cho chất lượng tổng + nhị phân cho correctness/faithfulness.

## Rules
- Chưa kiểm chứng — trước khi dùng: clone `strands-agents/evals`, đối chiếu `--help` thật, sửa file này.
- Harness-sdk KHÔNG dùng evals SDK trong CI của chính nó (grep `strands_evals` trong harness-py/ts/.github = rỗng) → đổi default harness không có regression eval tự động.
- Con số "benchmarked defaults" (trung bình 6 benchmark: alfworld, ContextBench, GAIA, WebShop, τ³-bench, Terminal-Bench 2.1) chép tay trong `site/public/embeds/strands-harness-benchmarks.html`; file số liệu gốc và harness chạy benchmark (`strands-labs/benchmark-harnesses`, Harbor trên EC2) KHÔNG có trong repo → không tái lập được.
