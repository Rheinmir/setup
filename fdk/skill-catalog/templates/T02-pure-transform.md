---
name: ${skill_name}
description: ${discovery_description}
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
  reuse-base: "pure-transform@1.0.0"
---

# Skill: ${skill_name}

## WHAT

### Purpose và context
- **Purpose:** chuyển `${input_schema}` sang `${output_schema}` theo mapping `${mapping}` (pattern P03).
- **Trigger (use when):** ${applicability}
- **Non-goals:** không thêm dữ kiện domain, không đoán giá trị thiếu, không gọi mạng.

### Mental model
`bytes vào → parse → kiểm schema → mapping → kiểm output → bytes ra + hash`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | dữ liệu | có | parse được theo encoding `${encoding}`, tối đa ${max_records} bản ghi |
| Out | dữ liệu đã chuyển | có | đúng `${output_schema}`, kèm hash; lỗi thì typed failure |

### Rules và capabilities
- RULE-01 (MUST): không mất field/ID bắt buộc; không sinh ID giả để qua schema.
- RULE-02 (MUST): cùng input + mapping cho cùng output (tất định).
- RULE-03 (MUST): input hỏng thì fail trước khi ghi, không bỏ qua bản ghi âm thầm.
- Capabilities: Parser · Mapping · FormatValidator; chỉ ghi file khi skill bao ngoài yêu cầu.

### Failure boundaries
- Input không parse được hoặc sai schema → **failed** `INVALID_INPUT`.
- Output sai schema → **failed** `INVALID_OUTPUT`.
- Vượt ${max_records} bản ghi → **failed** có giới hạn rõ, không cắt ngầm.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | deterministic | bytes | Kiểm kích thước + encoding | ok | vượt → failed |
| W02 | deterministic | bytes | Parse + kiểm `${input_schema}` | records | sai → INVALID_INPUT |
| W03 | deterministic | records | Áp mapping `${mapping}` | records mới | — |
| W04 | deterministic | records mới | Kiểm `${output_schema}` | ok | sai → INVALID_OUTPUT |
| W05 | deterministic | output | Trả bytes + hash | kết quả | — |

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | user_optional | mapping đảo ngược được và user bật round-trip | chuyển ngược lại và so khớp | mapping mất thông tin có chủ đích → skip | W05 |

### Validation và stopping
Không retry cùng một input hỏng. Test pack: input rỗng hợp lệ, input hỏng, thiếu field bắt buộc, Unicode/escaping, vượt giới hạn, chạy lặp ra cùng kết quả.

### Examples
- **Positive:** ${example_positive}
- **Boundary/failure:** ${example_boundary}
