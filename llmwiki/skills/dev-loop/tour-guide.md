# Skill: tour-guide

## Purpose
Thêm interactive tour/onboarding overlay vào bất kỳ màn hình mobile nào trong bonbon-ai.
Tap logo CTD → spotlight các nút tương tác + tooltip hướng dẫn → tap bất kỳ để đóng.

## Khi nào dùng
- Thêm tour guide cho màn hình mới
- Mở rộng tour sang filter/request/department pages
- Cập nhật tooltip labels

## Component đã có

**File**: `fe/components/dms/tour-guide.tsx`

```typescript
import { TourGuide, type TourSpot } from "@/components/dms/tour-guide";
```

**MobileTopbar** hỗ trợ `onLogoTap` prop để trigger tour:
```typescript
<MobileTopbar onLogoTap={() => setTourActive(true)} />
```

## Steps để add tour vào màn hình mới

### 1. Thêm `data-tour` attributes vào các elements cần highlight

```tsx
<button data-tour="my-button" onClick={...}>...</button>
<div data-tour="my-section">...</div>
```

**Rules**:
- Mỗi selector phải **unique** trong DOM khi tour hiển thị
- Với conditional render (`{condition && <button>}`): phải ensure condition = true trước khi tour mở
- Không dùng selector position-based (`:nth-child`, `:first-child`) cho dynamic content

### 2. Định nghĩa TourSpot array với `useMemo`

```typescript
// ⚠️ PHẢI dùng useMemo — không được inline array literal trong render
// Lý do: inline array tạo mới mỗi render → useEffect trong TourGuide re-runs liên tục → sai vị trí
const MY_SCREEN_TOUR = useMemo<TourSpot[]>(() => [
    { selector: "header button:first-child",       label: "Nút điều hướng",    labelSide: "bottom" },
    { selector: "header button[data-tour='logo']", label: "Hướng dẫn",         labelSide: "bottom" },
    { selector: "[data-tour='my-button']",         label: "Mô tả hành động",   labelSide: "bottom" },
    { selector: "[data-nav='overdue']",            label: "Phiếu quá hạn",     labelSide: "top" },
], []);
```

**labelSide**:
- `"bottom"` (default): tooltip xuất hiện trong phần dưới của element (65% height), không đè title
- `"top"`: tooltip xuất hiện TRÊN element — dùng cho bottom nav buttons

### 3. Force điều kiện render trước khi tour mở

Nếu các elements chỉ hiển thị khi state = X:
```typescript
// ✅ Set state CÙNG LÚC với mở tour
onLogoTap={() => {
    setMyViewMode("all");     // đảm bảo elements có trong DOM
    setTourActive(v => !v);   // mở/đóng tour
}}
```

TourGuide tự delay 100ms để DOM settle trước khi measure.

### 4. Render TourGuide + MobileTopbar

```tsx
const [tourActive, setTourActive] = useState(false);

return (
    <div>
        <TourGuide
            active={tourActive}
            onClose={() => setTourActive(false)}
            spots={MY_SCREEN_TOUR}
        />
        <MobileTopbar
            showBack={...}
            onBack={...}
            onLogoTap={() => {
                setRequiredState("correct-value"); // if needed
                setTourActive(v => !v);
            }}
        />
        {/* rest of screen */}
    </div>
);
```

## TourSpot interface

```typescript
interface TourSpot {
    selector: string;       // CSS selector — must match exactly 1 element in DOM
    label: string;          // Vietnamese description text
    labelSide?: "top" | "bottom";  // default "bottom"
}
```

## Behavior

| Action | Effect |
|--------|--------|
| Tap logo CTD | Toggle overlay on/off |
| Overlay open | All elements spotlit + tooltips visible |
| Tap anywhere | Close overlay |
| Resize window | Re-measure element positions |

## Positioning logic

- **Header buttons** (small, h<50px): tooltip just below element
- **Card buttons** (tall, h>50px, labelSide="bottom"): tooltip at 65% of card height (below title/icon)
- **Nav buttons** (labelSide="top"): tooltip above element

## Known pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| Tooltip sai vị trí | `spots` array recreated mỗi render | Dùng `useMemo` |
| Element không tìm được | Conditional render chưa active khi tour mở | Force state trước khi `setTourActive(true)` |
| Duplicate tooltips | `data-tour` attribute trùng nhiều elements | Dùng tên unique, remove duplicates |
| Tooltip đè title text | `labelSide="bottom"` nhưng card có padding nhỏ | Tăng `r.height * 0.65` → `r.height * 0.75` |

## Ví dụ đang dùng

**Dashboard page** (`fe/app/(protected)/dashboard/page.tsx`):
- 8 spots: menu, logo, pending-card, dept-card, contract-card, overdue nav, all nav, logout nav
- Trigger: tap CTD logo → force `allViewMode="all"` → open tour

## Origin

Implemented 2026-05-29 via session với Orca devtools tracing.
Component: `fe/components/dms/tour-guide.tsx`
