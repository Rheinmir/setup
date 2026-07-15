---
type: concept
title: "Skill-craft — bộ từ vựng để viết và soi một skill cho đúng"
status: active
tags: [skills, meta, context-load, predictability]
timestamp: 2026-07-15
---

# Skill-craft — viết một skill sao cho đoán được

Một skill tồn tại để **vắt tính tất định ra khỏi một hệ thống ngẫu nhiên**. Đức tính gốc là **predictability** (tính đoán được): agent đi **cùng một quy trình** mỗi lần chạy — không phải ra cùng một *output*, mà đi cùng một *đường*. Mọi nguyên tắc dưới đây đều phục vụ đúng một điều đó. Đây là concept tham chiếu — đọc khi viết hoặc soi một skill, không phải quy trình chạy từng bước.

Chưng cất từ `writing-great-skills` của `mattpocock/skills` (nguồn ngoài, xem `## Origin`), gọi tên bằng tiếng Việt và neo vào bối cảnh overstack.

## Hai loại phí — mỗi lần chia skill là tiêu một trong hai

Đây là khung kinh tế của toàn bộ chuyện viết skill:

- **Context load** (tải ngữ cảnh) — phí mà **máy** trả. Một skill model-invoked có `description` nằm trong cửa sổ ngữ cảnh **mọi lượt, mọi phiên**, kể cả phiên không bao giờ gọi nó. Nhiều skill model-invoked = nhiều token chết mỗi lượt.
- **Cognitive load** (tải nhận thức) — phí mà **người** trả. Một skill chỉ-gọi-tay (`disable-model-invocation: true`) không tốn context load nào, nhưng đổi lại *người dùng* trở thành cái chỉ mục phải nhớ rằng nó tồn tại.

Hai lựa chọn invocation, đổi hai loại phí khác nhau:

- **Model-invoked** — giữ `description` trong tầm với của agent, nên agent tự bắn được *và* skill khác gọi được. Trả context load. Dùng khi agent **phải tự bắt được ngữ cảnh** để gọi, hoặc **một skill khác phải gọi được nó**.
- **User-invoked** (`disable-model-invocation: true`) — chỉ người gõ tên mới gọi được; không skill nào khác với tới. Zero context load. Dùng khi skill **chỉ bao giờ chạy bằng tay**.

Khi số skill chỉ-gọi-tay nhiều quá sức nhớ, tải nhận thức dồn lại được chữa bằng một **router**: một skill (hoặc bản đồ) liệt kê những cái kia và khi nào với tới cái nào. Trong overstack, router là `/find-skills` + `CAPABILITIES.md`.

**Quy tắc chọn:** chỉ chọn model-invocation khi agent *phải* tự với tới, hoặc skill khác *phải* với tới. Nếu nó chỉ bao giờ chạy bằng tay → user-invoked, khỏi trả context load.

## Information hierarchy — cái gì nằm ở đâu

Một skill xây từ hai loại nội dung, trộn tự do: **step** (bước hành động, có thứ tự) và **reference** (định nghĩa/luật/sự kiện, tra khi cần). Xếp chúng trên một cái thang theo mức agent cần tới ngay:

1. **In-skill step** — hành động có thứ tự trong `SKILL.md`. Mỗi bước kết thúc bằng một **completion criterion** (xem dưới).
2. **In-skill reference** — định nghĩa/luật trong `SKILL.md`, tra khi cần. Thường là một tập phẳng hợp lệ (mọi luật của một cuộc review nằm cùng một bậc) — không phải mùi lỗi.
3. **External reference** — reference đẩy ra file riêng, với tới bằng một **context pointer**, chỉ nạp khi pointer bắn.

**Progressive disclosure** là cú đẩy xuống thang — ra khỏi `SKILL.md` vào một file liên kết — để phần đỉnh còn đọc được. Test sạch nhất là **branch** (nhánh): thứ mọi nhánh cần thì để inline; thứ chỉ vài nhánh với tới thì đẩy sau một pointer. **Wording của context pointer**, không phải đích của nó, quyết định khi nào và chắc đến đâu agent với tới.

Đẩy xuống ít quá thì đỉnh phình; đẩy nhiều quá thì giấu mất thứ agent thật sự cần. Căng thẳng đó là toàn bộ quyết định.

## Completion criterion — điều kiện để biết đã xong

Mỗi step kết thúc trên một **completion criterion**: điều kiện nói cho agent biết việc đã xong. Nó phải:

- **kiểm được** — agent phân biệt được *xong* với *chưa xong* (không phải "làm cho tốt").
- **vét cạn** khi cần — "mọi model đã sửa đều được tính đến", không phải "sinh một danh sách thay đổi".

Một criterion mơ hồ mời gọi **premature completion** — kết thúc một bước trước khi nó thật sự xong, vì sự chú ý trượt sang *cảm giác đã xong*. Đây là failure mode phổ biến nhất, và phòng thủ theo thứ tự: **làm sắc criterion trước** (rẻ, tại chỗ); chỉ khi nó *bất khả sắc* mà bạn *quan sát thấy* agent vội, mới giấu các bước sau bằng cách tách skill.

## Leading word — một từ neo cả một vùng hành vi

Một **leading word** (từ dẫn) là một khái niệm cô đọng **đã nằm sẵn trong pretraining** của model, mà agent nghĩ-bằng khi chạy skill — ví dụ *lesson*, *fog of war*, *tracer bullet*, *red*. Nhắc lại xuyên suốt (đôi khi chỉ cần một lần nếu từ đủ mạnh), nó tích luỹ một định nghĩa phân tán và **neo cả một vùng hành vi bằng ít token nhất**, bằng cách gọi dậy những prior model đã giữ.

Nó phục vụ predictability hai lần: trong thân skill nó neo *thi hành* (agent với tới cùng một hành vi mỗi lần từ đó xuất hiện); trong description nó neo *invocation* (khi cùng từ đó sống trong prompt, docs, code của bạn, agent nối ngôn ngữ chung ấy với skill và bắn tin cậy hơn).

Săn cơ hội refactor để dùng từ dẫn. Một bộ ba trải ra ở ba chỗ, một câu description gợi ý một ý — mỗi cái là một đoạn đang xin được **thu về một token**. Ví dụ: "nhanh, tất định, ít overhead" → *tight* (một vòng lặp *tight*); "một vòng lặp mình tin" → *red* (vòng lặp đỏ trên con bug, hoặc không). Thắng hai lần: ít token hơn, *và* một cái móc sắc hơn cho agent treo suy nghĩ.

## Năm failure mode — dùng để chẩn đoán một skill đang có vấn đề

- **Duplication** (trùng lặp) — cùng một ý ở nhiều hơn một chỗ. Tốn bảo trì và token, và **thổi phồng** thứ hạng của một ý trên cái thang quá mức thật của nó. Chữa: giữ mỗi ý ở **một nguồn chân lý**.
- **Sediment** (trầm tích) — các lớp cũ lắng lại vì thêm thì thấy an toàn, bỏ thì thấy rủi ro. Số phận mặc định của mọi skill không có kỷ luật cắt tỉa.
- **Sprawl** (phình) — skill đơn giản là quá dài, kể cả khi mọi dòng còn sống và không trùng. Hại đọc, hại bảo trì, tốn token. Thuốc là cái thang: đẩy reference sau pointer, tách theo nhánh hoặc theo chuỗi.
- **No-op** — một dòng model đã tuân theo mặc định, nên bạn trả tải để nói không-gì-cả. Test: nó có đổi hành vi so với mặc định không? Một từ dẫn yếu (*be thorough* khi agent vốn đã kha khá kỹ) là một no-op; thuốc là một từ mạnh hơn (*relentless*), không phải một kỹ thuật khác.
- **Negation** (phủ định) — lái bằng cấm đoán phản tác dụng: *đừng nghĩ về con voi* gọi tên con voi và làm nó **sẵn có hơn**, không ít đi. Prompt cái **khẳng định** — nêu hành vi đích để cái bị cấm không bao giờ được nói ra; chỉ giữ một cấm đoán khi nó là rào cứng không phát biểu xuôi được, và kể cả khi đó cũng ghép với *phải làm gì thay vào*.

## Cách cắt tỉa một skill

- **Relevance** — mỗi dòng còn dính tới việc skill làm không?
- **No-op sentence by sentence** — chạy test no-op trên **từng câu tách rời**; câu nào rớt thì **xoá cả câu**, đừng gọt chữ. Mạnh tay: phần lớn prose rớt nên bị xoá, không phải viết lại.
- **Single source of truth** — giữ mỗi ý ở một chỗ có thẩm quyền, để đổi hành vi là một lần sửa.

## Áp vào overstack

Đây là lý do concept này tồn tại, không phải để đọc cho biết:

- **Cắt context load** là đòn bẩy tác động *mọi phiên, mãi mãi* — đo được trước/sau.
- **`/new-skill`** phải trỏ tới concept này bằng context pointer, để mỗi skill mới sinh ra đã theo chuẩn.
- **`/lint`** biến các mục trên thành **số đo tất định**: đếm token description, tìm skill thiếu completion criterion, đo tỉ lệ negation, phát hiện sprawl và duplication. Một dữ kiện ("skill này 340 dòng, 0 completion criterion, 61% câu là câu cấm") đổi được hành vi; một lời khuyên ("hãy viết gọn") thì không.

## Origin
- Chưng cất từ `mattpocock/skills` — `skills/productivity/writing-great-skills/SKILL.md` + `GLOSSARY.md` (clone tại `scratchpad/mattpocock-skills/`, 2026-07-15).
- Absorb qua `/propose` → `150726-mattpocock-absorb` (T3), task `T-260715-01`.
- **Commit:** _(verify-before-commit điền)_
