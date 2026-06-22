---
name: tour-guide
description: >
  Thêm một in-app product tour (spotlight onboarding overlay) tự viết, KHÔNG cần thư viện
  (không joyride/intro.js/driver.js). Vẽ lớp tối + khoét spotlight quanh từng phần tử theo
  CSS selector, gắn tooltip nhãn, và 1 pill "tap để đóng" đặt vào khoảng trống lớn nhất.
  Responsive mobile/desktop, lock scroll, đo bằng getBoundingClientRect, click bất kỳ đâu để đóng.
  Dùng khi user muốn: "thêm tour guide", "onboarding tour", "hướng dẫn trong app", "spotlight
  tour", "product tour", "walkthrough", "tour kiểu bonbon", hoặc invoke /tour-guide. Hợp với
  React/Next.js + Tailwind. Mỗi route tự định nghĩa danh sách điểm dừng (spots); phần tử được
  đánh dấu bằng thuộc tính data-tour ổn định.
---

# tour-guide — In-app spotlight tour (no library)

Pattern đã chạy thật trong bonbon DMS. Một component duy nhất + quy ước `data-tour` + mảng `spots` mỗi route.

## Cách hoạt động
1. Đánh dấu phần tử cần highlight bằng `data-tour="..."` (ổn định hơn class).
2. Một state `tourActive` + nút trigger (vd tap logo) bật/tắt.
3. Mỗi route khai báo `spots: TourSpot[]` (selector + label) truyền vào `<TourGuide>`.
4. Component đo DOM, vẽ SVG dim + spotlight cutout + tooltip, click đâu cũng đóng.

## Bước 1 — Component (copy nguyên file)

Tạo `components/ui/tour-guide.tsx` (hoặc nơi tương đương). 0 dependency ngoài React.
Chỉnh 6 token màu trong `TOUR_THEME` cho khớp brand; `dismissText` đổi qua prop.

```tsx
"use client";
import { useEffect, useState, useCallback } from "react";

/** Sửa 6 token này cho khớp brand của bạn. */
const TOUR_THEME = {
  scrim: "rgba(0,0,0,0.72)",                 // lớp tối
  ring: "rgba(255,255,255,0.2)",             // viền spotlight
  tipDesktop: "border border-sky-400 bg-white text-slate-900 shadow-[0_2px_8px_rgba(56,189,248,0.2)]",
  tipMobile: "bg-sky-100 text-slate-900",
  hintDesktop: "bg-slate-900 text-white",
  hintMobile: "bg-white/25 text-white backdrop-blur-sm",
};

export interface TourSpot {
  selector: string;                          // CSS selector phần tử (ưu tiên [data-tour='...'])
  label: string;                             // chữ tooltip ("" nếu chỉ muốn spotlight)
  labelSide?: "top" | "bottom" | "right";    // hướng đặt tooltip
  spotlightOnly?: boolean;                   // chỉ khoét spotlight, không tooltip
  tooltipOnly?: boolean;                     // chỉ tooltip, không khoét spotlight
}

interface MeasuredSpot {
  top: number; left: number; width: number; height: number;
  label: string; labelSide: "top" | "bottom" | "right";
  spotlightOnly?: boolean; tooltipOnly?: boolean;
}

function measure(spots: TourSpot[]): MeasuredSpot[] {
  return spots.flatMap(spot => {
    const el = document.querySelector(spot.selector);
    if (!el) return [];
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) return [];
    if (r.top < -20 || r.top > window.innerHeight) return []; // off-screen → bỏ
    const vh = window.innerHeight;
    return [{
      top: r.top, left: r.left, width: r.width, height: r.height,
      label: spot.label,
      labelSide: spot.labelSide ?? (r.top > vh * 0.6 ? "top" : "bottom"),
      spotlightOnly: spot.spotlightOnly,
      tooltipOnly: spot.tooltipOnly,
    }];
  });
}

export function TourGuide({
  active, onClose, spots, dismissText = "Tap anywhere to close",
}: {
  active: boolean; onClose: () => void; spots: TourSpot[]; dismissText?: string;
}) {
  const [maskId] = useState(() => `tm-${Math.random().toString(36).slice(2, 8)}`);
  const [rects, setRects] = useState<MeasuredSpot[]>([]);

  const remeasure = useCallback(() => { if (active) setRects(measure(spots)); }, [active, spots]);

  useEffect(() => {
    if (!active) { setRects([]); document.body.style.overflow = ""; return; }
    window.scrollTo({ top: 0, behavior: "instant" });
    document.body.style.overflow = "hidden";
    const id = setTimeout(() => setRects(measure(spots)), 300) as unknown as number;
    window.addEventListener("resize", remeasure);
    return () => {
      clearTimeout(id);
      window.removeEventListener("resize", remeasure);
      document.body.style.overflow = "";
    };
  }, [active, remeasure]);

  if (!active) return null;

  const PAD = 8;
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const isDesktop = vw >= 768;

  return (
    <div className="fixed inset-0 z-[500]" onClick={onClose}>
      <svg className="pointer-events-none absolute inset-0" width={vw} height={vh}>
        <defs>
          <mask id={maskId}>
            <rect width="100%" height="100%" fill="white" />
            {rects.filter(r => !r.tooltipOnly).map((r, i) => (
              <rect key={i} x={r.left - PAD} y={r.top - PAD}
                width={r.width + PAD * 2} height={r.height + PAD * 2} rx={12} fill="black" />
            ))}
          </mask>
        </defs>
        <rect width="100%" height="100%" fill={TOUR_THEME.scrim} mask={`url(#${maskId})`} />
        {rects.filter(r => !r.tooltipOnly).map((r, i) => (
          <rect key={i} x={r.left - PAD} y={r.top - PAD}
            width={r.width + PAD * 2} height={r.height + PAD * 2} rx={12}
            fill="none" stroke={TOUR_THEME.ring} strokeWidth={1.5} />
        ))}
      </svg>

      {rects.filter(r => !r.spotlightOnly).map((r, i) => {
        const isTop = r.labelSide === "top";
        const isRight = r.labelSide === "right";
        const isTall = r.height > 50 && r.height <= 200;
        const tip = `whitespace-nowrap rounded-lg px-2.5 py-1 text-[10px] font-semibold shadow-md ${isDesktop ? TOUR_THEME.tipDesktop : TOUR_THEME.tipMobile}`;
        let tooltipTop: number;
        if (isRight) {
          const estWR = Math.min(r.label.length * 7 + 24, 220);
          tooltipTop = r.top + r.height / 2 - 14;
          const rightLeft = r.left + r.width + PAD + 6;
          return (
            <div key={i} className="pointer-events-none fixed z-[501]"
              style={{ top: tooltipTop, left: Math.min(rightLeft, vw - estWR - 8) }}>
              <div className={tip}>{r.label}</div>
            </div>
          );
        } else if (isTop) {
          tooltipTop = Math.max(8, r.top - 30);
        } else if (isTall) {
          tooltipTop = Math.min(r.top + r.height * 0.82, vh - 40);
        } else if (r.height > 200 && (!isDesktop || r.tooltipOnly)) {
          return null; // card mở rộng (mobile luôn ẩn; desktop chỉ ẩn khi tooltipOnly)
        } else {
          tooltipTop = Math.min(r.top + r.height + 6, vh - 40);
        }
        const estW = Math.min(r.label.length * 7 + 24, 220);
        const centerX = r.left + r.width / 2 - estW / 2;
        const tooltipLeft = Math.max(8, Math.min(centerX, vw - estW - 8));
        return (
          <div key={i} className="pointer-events-none fixed z-[501]"
            style={{ top: tooltipTop, left: tooltipLeft }}>
            <div className={tip}>{r.label}</div>
          </div>
        );
      })}

      {(() => {
        const PILL_H = 40, MARGIN = 16;
        const zones: [number, number][] = rects.map(r => [r.top - PAD - 36, r.top + r.height + PAD + 36]);
        zones.sort((a, b) => a[0] - b[0]);
        const merged: [number, number][] = [];
        for (const z of zones) {
          if (merged.length && z[0] <= merged[merged.length - 1][1]) {
            merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], z[1]);
          } else { merged.push([...z] as [number, number]); }
        }
        const gaps: { top: number; bot: number; size: number }[] = [];
        let prev = 80;
        for (const [zTop, zBot] of merged) {
          if (zTop - prev >= PILL_H + MARGIN * 2) gaps.push({ top: prev, bot: zTop, size: zTop - prev });
          prev = zBot;
        }
        if (vh - prev >= PILL_H + MARGIN * 2) gaps.push({ top: prev, bot: vh, size: vh - prev });
        const best = gaps.sort((a, b) => b.size - a.size)[0];
        if (!best || best.size < PILL_H + MARGIN * 2) return null;
        const pillTop = best.top + (best.size - PILL_H) / 2;
        return (
          <div className={`pointer-events-none fixed left-1/2 z-[501] -translate-x-1/2 rounded-full px-5 py-2.5 text-xs font-semibold shadow-lg ${isDesktop ? TOUR_THEME.hintDesktop : TOUR_THEME.hintMobile}`}
            style={{ top: pillTop }}>
            {dismissText}
          </div>
        );
      })()}
    </div>
  );
}
```

## Bước 2 — Đánh dấu phần tử bằng `data-tour`

Trên các phần tử muốn highlight, thêm attribute ổn định:
```tsx
<button data-tour="logo" onClick={() => setTourActive(true)}>…</button>
<input data-tour="search-input" … />
<div  data-tour="list-item" … />
```
> Dùng `data-tour` thay vì class — class hay đổi do refactor/Tailwind; `data-tour` bền.

## Bước 3 — Wire vào route (state + trigger + spots)

```tsx
import { TourGuide, type TourSpot } from "@/components/ui/tour-guide";
import { useMemo, useState } from "react";

const [tourActive, setTourActive] = useState(false);

const SPOTS = useMemo<TourSpot[]>(() => [
  { selector: "[data-tour='logo']",         label: "Mở hướng dẫn",       labelSide: "bottom" },
  { selector: "[data-tour='search-input']", label: "Tìm kiếm ở đây",     labelSide: "bottom" },
  { selector: "[data-tour='list-item']",    label: "Nhấn để xem chi tiết", labelSide: "bottom" },
  { selector: "[data-tour='action-approve']", label: "Duyệt",            labelSide: "top" },
], []);

// …trong JSX:
<button data-tour="logo" onClick={() => setTourActive(true)}>Hướng dẫn</button>
<TourGuide active={tourActive} onClose={() => setTourActive(false)} spots={SPOTS} dismissText="Nhấn bất kỳ đâu để đóng" />
```

## TourSpot — tham chiếu
| field | ý nghĩa |
|---|---|
| `selector` | CSS selector (ưu tiên `[data-tour='x']`); element không tồn tại/khuất → tự bỏ qua |
| `label` | chữ tooltip; `""` + `spotlightOnly` = chỉ khoét sáng |
| `labelSide` | `top` / `bottom` / `right` (mặc định: tự chọn theo vị trí) |
| `spotlightOnly` | khoét spotlight, KHÔNG tooltip |
| `tooltipOnly` | tooltip nổi, KHÔNG khoét (cho phần tử quá to / desktop) |

## Mobile vs Desktop
Vì layout 2 dạng khác nhau, khai báo 2 mảng spots (selector `data-tour='desktop-*'` riêng) rồi chọn theo `window.innerWidth >= 768` (hoặc `useMediaQuery`). Phần tử desktop ẩn trên mobile sẽ tự bị `measure()` bỏ qua, nên trộn chung 1 mảng cũng chạy — nhưng tách rõ ràng dễ chỉnh nhãn hơn.

## Gotchas
- **z-index:** overlay `z-[500]`, tooltip/hint `z-[501]`. Nâng nếu app có thứ cao hơn.
- **Đo trễ 300ms:** chờ layout/animation ổn định trước khi đo. Nếu list load async, mở tour sau khi data có (hoặc gọi remeasure).
- **Lock scroll:** set `document.body.style.overflow='hidden'` khi active, nhớ khôi phục khi đóng (đã handle trong cleanup).
- **Click-to-close:** toàn overlay `onClick={onClose}`; tooltip/hint là `pointer-events-none` nên không chặn click đóng.
- **Element khuất:** spot off-screen tự loại — nên cuộn lên đầu (`scrollTo top`) trước khi đo (đã làm).

## Origin
Trích & generalize từ bonbon DMS `components/dms/tour-guide.tsx` (đã chạy production, mobile+desktop).
