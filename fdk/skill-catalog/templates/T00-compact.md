---
name: ${skill_name}
description: ${discovery_description}
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: ${skill_name}

## WHAT

### Purpose và context
<!-- `description` ở trên là thứ router khớp — giữ trigger phrase cụ thể ở đó. -->
- Purpose: ⟨TODO⟩ một câu outcome — skill giúp xong việc gì.
- Trigger: ⟨TODO⟩ 2–3 câu user nên kích hoạt; non-goals: ⟨TODO⟩ việc gần nghĩa KHÔNG thuộc skill.

### Mental model
⟨TODO⟩ thực thể → quan hệ → luồng khái niệm (vd `Input → Check → Artifact → Evidence`).

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | ⟨TODO⟩ | có | ⟨TODO⟩ |
| Out | ⟨TODO⟩ | — | ⟨TODO⟩ — "xong" nghĩa là gì, bằng chứng nào |

### Rules và capabilities
- RULE-01 (MUST): ⟨TODO⟩ bất biến kiểm được, không phá dù chọn HOW nào.
- Capabilities: ⟨TODO⟩ năng lực trừu tượng cần đọc/ghi/kiểm — không ghi cứng tên CLI/provider ở đây.

### Failure boundaries
⟨TODO⟩ khi nào clarify / partial / blocked / failed — và kết quả hợp lệ của từng trường hợp.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | deterministic | ⟨TODO⟩ | ⟨TODO⟩ preflight: kiểm input/scope/tool | ⟨TODO⟩ | thiếu input → blocked |
| W02 | judgment | ⟨TODO⟩ | ⟨TODO⟩ | ⟨TODO⟩ | ⟨TODO⟩ → W03 |
| W03 | deterministic | ⟨TODO⟩ | ⟨TODO⟩ kiểm kết quả | PASS → giao | FAIL → sửa 1 lần rồi dừng |

### Branches
Không có nhánh phụ trong version này. <!-- hoặc bảng: ID | kind | guard | effect | skip | failure | rejoin -->

### Validation và stopping
⟨TODO⟩ phần nào kiểm bằng code (lệnh + rc), phần nào cần review; trần lần sửa/retry.

### Examples
- Positive: ⟨TODO⟩ input hợp lệ → expected output.
- Boundary/failure: ⟨TODO⟩ input thiếu/sai → expected status (blocked/partial) + lý do.
