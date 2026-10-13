# bench/retrieval — đối chứng đường đọc 0 token (2026-10-13)

Mọi retriever ở đây tất định, không LLM, không dependency. Số đo cùng metric MemPalace (R@k, session-level, index user-turns).

| Bộ dữ liệu | Jaccard (cũ) | BM25 (lexrank.py) | Có cạnh file→trang | Embedding (MemPalace minilm) |
|---|---|---|---|---|
| LongMemEval_S 500 câu, R@5 | 0.628 | 0.956 (qua mem-rank.retrieve thật) | — | 0.966 |
| Wiki openship, 275 commit thật, R@1 | 0.444 (bench) · 0.415 (okf-scan thật, có NOOP) | 0.458 (bench) | 0.905 (okf-scan thật, `--files` = file commit chạm) | — |

- `bench_lme.py <longmemeval_s_cleaned.json>` — 7 biến thể trên LongMemEval.
- `bench_wiki.py <repo> [n_commit]` / `bench_wiki2.py` — truy vấn = tiêu đề commit, gold = trang trích dẫn file commit chạm.
  Lưu ý: kênh cạnh file dùng đúng file commit chạm nên ≈ oracle theo cách định nghĩa gold; ở hook thật file dirty từ `git status` là tín hiệu tương đương.
- `verify_shipped.py` — chạy bench qua ĐÚNG `mem-rank.retrieve` và `okf-scan.rank` đã cài (không qua bản sao).
- Dữ liệu LongMemEval_S (273MB, không chép vào repo): tải từ repo MemPalace `benchmarks/` hoặc HF `xiaowu0162/longmemeval`, đặt vào `data/longmemeval_s_cleaned.json`.

## Phía GHI + cột chi phí (2026-10-13, cùng ngày)

Đo trên 19 transcript thật của openship (`bench_cost_sessions.py <thư mục transcript>`), 379 prompt:

| Hook bơm vào context | lần | ≈token/phiên | ghi chú |
|---|---|---|---|
| docs-gate (bản repo-local `harness-events.py docs`) | 110 | 734 | bắn ĐÔI với hook global (global chỉ 2 lần vì có soi transcript) |
| recall đầu phiên | 30 | 407 | 3/3 dòng chuỗi trùng nhau; 3/4 slot là episode bản sao |
| Gợi ý recall được MỞ THẬT (đếm tool_use) | 7/72 = 0.10 | | okf-scan `verify` cũ báo 1.0 vì đếm cả chữ trong hook output |

Nguyên nhân gốc: Stop-hook ghi episode MỖI LƯỢT → 329 record giống hệt (cùng did, cùng files).

Sửa (nhánh `feat/retrieval-bm25-edges`):
- `stop.py secondary_memory`: một episode / phiên (cùng did+files → bỏ, đổi files → ghi đè cùng id). Test: `harness/tests/test_episode_once_per_session.py`.
- `mem-rank.py compact`: gộp store cũ (openship 329 → 22, bản gốc `.bak-*`).
- `okf-scan.py verify`: chỉ đếm tham số tool_use; `rank()` gộp theo (nguồn, tiêu đề).
- `session_start.py recall`: gộp dòng chuỗi trùng thành "×N phiên".
- `harness-events.py m_docs`: nhường docs-gate cho hook global khi repo có stamp.
- `okf-scan.py collect`: bỏ qua `sources/provenance/` theo mặc định (sổ tự ghi cho hệ khác, 15/43 mục openship); tuỳ chọn qua env `OKF_SCAN_SKIP` (rỗng = quét hết).

Kết quả đầu phiên openship: khối recall 1035 → 649 ký tự, 4 slot → 1 episode + 1 trang wiki (thay vì 3 episode bản sao);
docs-gate từ 2 lần/5 prompt (1 vô điều kiện) → 1 lần/5 prompt có điều kiện. Chất lượng truy hồi giữ nguyên
(`verify_shipped.py`: LME R@5 0.956; wiki R@1 0.909 / R@5 0.989).

### Self-attention: bơm MỘT lần có đủ không? (`bench_attention.py`, haiku, 10 case, 80 lời gọi, $3.58)

Khối recall (≤4 đường dẫn, gold nằm trong khối) đặt ĐẦU prompt, sau đó N ký tự hội thoại không liên quan (LongMemEval),
cuối cùng hỏi "đọc trang wiki nào trước". `use` = đáp án là một trang trong khối; `hit` = đúng trang gold.

| filler (ký tự) | không bơm | bơm 1 lần (use / hit / tok) | bơm lặp mỗi 40k (use / hit / tok) |
|---|---|---|---|
| 0 | 0.00 / 0.00 / 33.4k | 1.00 / 0.70 / 33.8k | — |
| 100k (≈36k tok) | 0.00 / 0.00 / 69.6k | 1.00 / 0.70 / 70.0k | 1.00 / 0.70 / 70.1k |
| 300k (≈104k tok) | 0.00 / 0.00 / 138.3k | 1.00 / 0.70 / 138.2k | 1.00 / 0.70 / 139.5k |
| 1.9M (≈650k tok, 3 case none) | 0.00 / 0.00 / 685.6k | 1.00 / 0.70 / 685.0k | 1.00 / 0.80 / 695.4k |

Kết luận: sau ~100k token nhiễu, model vẫn dùng khối bơm một lần y như bơm lặp (use 1.00 cả hai); nhắc lại chỉ thêm token.
Trần hit 0.70 là cùng 3 case ở mọi biến thể: khối có 2 trang wiki hợp lý và model chọn trang kia — đó là việc của bước XẾP HẠNG
(thứ tự trong khối), không phải attention. Hạn chế: haiku, filler là chat tiếng Anh chứ không phải tool output; chưa chạy trên model lớn.
Ở 650k token (23 lời gọi, $15.1): bơm 1 lần vẫn use 1.00, hit 0.70; bơm lặp 0.80 — 3 case đổi chiều (0 và 4 nghiêng về lặp, 8 nghiêng về 1 lần), cả 3 đều chọn
MỘT TRANG KHÁC TRONG KHỐI (use vẫn 1.00) → chọn ngẫu nhiên giữa các trang hợp lý, không phải mất dấu khối. Net +1/10 nằm trong nhiễu. Chi phí lặp +10k token/lời gọi (47 lần chèn).
Dữ liệu thô: `bench_attention_haiku_2026-10-13.json`, `bench_attention_haiku_650k_2026-10-13.json`.

## Chi phí từng stage (đo 2026-10-13, openship; token ≈ ký tự / 2.9 theo tỷ lệ đo được từ usage haiku)

| Stage | Ai trả | Trước | Sau | Đo bằng |
|---|---|---|---|---|
| 1. Ghi (Stop-hook: episode + provenance) | CPU máy local, 0 token LLM | 1 episode/lượt → 329 record | 1 episode/phiên → 22 record | `wc -l memory.jsonl` |
| 2. Chọn (SessionStart: okf-scan BM25 + cạnh file, 49 mục) | CPU local, 0 token LLM | — | 53 ms query · 154 ms cả hook | `time` |
| 3. Nạp khối recall vào context | token đầu vào, trả MỘT lần/cửa sổ context (đầu phiên, sau compact) | 1035 ký tự ≈ 357 tok, 3/4 slot bản sao | 649 ký tự ≈ 224 tok, 1 episode + 1 wiki | `session_start.py` stdout |
| 4. Nhắc lặp mỗi lượt (docs-gate) | token đầu vào, MỖI 5 prompt | 2 bản/5 prompt, 1 vô điều kiện, ≈734 tok/phiên | 1 bản/5 prompt, chỉ khi thiếu docs, ≈207 tok/lần | `bench_cost_sessions.py` |
| 5. Mở trang wiki được gợi ý | token đầu vào, chỉ khi agent Read | 17 trang concept/entity: TB 2008 ký tự ≈ 692 tok, max ≈ 1391 tok | không đổi | `wc -c` |
| 6. Self-attention tìm lại khối sau nhiễu | 0 token thêm nếu bơm 1 lần; +10k tok/lời gọi nếu bơm lặp 47 lần | — | use 1.00 ở 650k tok nhiễu cả hai cách | `bench_attention.py` |

Chi phí thí nghiệm (haiku, `claude -p`): bench 0/100k/300k = $3.58 (80 lời gọi); bench 650k = $15.18 (23 lời gọi, ≈0.66 $/lời).
Mọi bench truy hồi tất định (LME, wiki) = 0 token, chạy local vài giây đến vài phút.

## Truy vấn từ PROMPT (bench_prompt_query.py, 13/10/2026)

Câu hỏi: prompt thật ở openship 18/18 là tiếng Việt, title/tag wiki tiếng Anh → okf-scan có tìm đúng trang không, và
cần model hay không? Case: 268 commit (gold = trang trích dẫn file commit chạm, như bench_wiki), mỗi commit có 2 prompt
Việt do haiku viết (`data/wiki_queries_vi.json`, $0.44): *plain* không có định danh, *ident* nhắc 1 tên file.
Biến thể cùng gold, cùng `okf.rank` đã cài: `en` commit subject (trần trên), `vi_raw` nguyên văn, `vi_terms` qua
`okf-scan.prompt_terms` (định danh → từ vựng chỉ mục ASCII → bảng cầu Việt→Anh), `vi_llm` haiku viết lại ≤8 từ khoá Anh.
Cột "chữ" = không file; "+cạnh" = có file commit như lúc có file dirty. "¬hub" = gold bỏ active-work/architecture
(active-work chép nguyên commit subject nên `en` được lợi không thật).

| biến thể | R@1 chữ | R@4 chữ | R@1 +cạnh | R@4 +cạnh | R@1 chữ ¬hub |
|---|---|---|---|---|---|
| en (commit subject) | 0.444 | 0.504 | 0.787 | 0.896 | 0.450 |
| vi_plain_raw | 0.004 | 0.004 | 0.776 | 0.869 | 0.004 |
| vi_plain_terms | 0.175 | 0.302 | 0.776 | 0.899 | 0.181 |
| vi_ident_raw | 0.075 | 0.082 | 0.754 | 0.877 | 0.077 |
| vi_ident_terms | 0.313 | 0.437 | 0.754 | 0.903 | 0.331 |

Nửa sau held-out (bảng cầu mở rộng khi chỉ nhìn nửa đầu, `--half`): vi_plain_terms 0.142/0.269, vi_ident_terms 0.291/0.440,
en 0.500/0.545 — cùng bậc, không có dấu hiệu quá khớp.

Tầng 4 (haiku viết lại prompt thành ≤8 từ khoá Anh, 536 lượt, $0.54, không dùng cạnh file): vi_plain_llm 0.142/0.190,
vi_ident_llm 0.168/0.205 — KHÔNG hơn ba tầng tất định (0.175/0.302 và 0.313/0.437). Không cài tầng này.

Kết luận: (1) prompt Việt nguyên văn = 0, đúng như dự đoán; (2) ba tầng tất định kéo lên 0.18 (không định danh) và 0.31
(có 1 tên file, nhờ khớp basename mới trong `lexrank.edge_score`), gần trần `en` 0.44; (3) khi có file dirty, kênh cạnh
gánh hết (≈0.78/0.90) và chữ chỉ thêm 0–3 điểm R@4. Đã cài: `okf-scan query --prompt`, hook UserPromptSubmit
`prompt_recall` (prompt đầu phiên, chỉ bơm trang chưa in; test `harness/tests/test_prompt_recall.py`),
bảng cầu riêng dự án `<wiki>/.query-bridge.json`.

### Phiên thật (live_prompt_cases.py, 14/10/2026)

Trần của fdk-uat và của payload giả là "cài được / hook trả lời khi gọi tay". Chỉ phiên `claude -p` thật mới cho thấy khối hook
có vào context không, agent mở trang nào, có rác không. 12 prompt Việt (10 nhắm một trang, 2 chung chung), haiku, 3 vòng:

| vòng | gợi ý trúng | agent mở trúng | chung chung im lặng | trang rác do prompt | sửa sau vòng |
|---|---|---|---|---|---|
| 1 | 10/10 | 10/10 | 0/2 | 16 | từ vựng bỏ cả đường dẫn ("wiki" khớp mọi trang) |
| 2 | 10/10 | 10/10 | 2/2 | 8 | bảng cầu "khoá"/"phiên" → cụm dài; stoplist âm tiết không dấu |
| 3 | 10/10 | 10/10 | 2/2 | 4 (đều trang liên quan thật) | — |

Cách chạy: `python3 live_prompt_cases.py <repo>` rồi xoá biên lai/episode của các phiên thử khỏi `.harness/metrics/` (SIDS in ở cuối).
