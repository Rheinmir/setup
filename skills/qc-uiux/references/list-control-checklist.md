# List/table control checklist

Load this when the audited route/component is a dense list or table (a
queue, an admin grid, a ticket/request list, a dashboard summary strip).
Each item maps to one of the four qc-uiux mục — noted in brackets — so
findings slot straight into the normal report format.

1. **[3 Consistency] One loud color system per row.** If a row encodes
   status AND urgency AND priority, at most one of them should own the
   row's heavy paint (left border + full-row wash). The rest are small
   secondary cues (icon, tiny badge). Three independent hue-coded systems
   stacked on one row = drift, flag it even if each color is individually
   "correct."
2. **[4 Antipattern] Urgency must survive a "calm it down" pass.** If a
   color system was dialed back for legibility, check the state that's
   functionally urgent (breach, failure, blocker) wasn't softened along
   with everything else — it should still read as loud/distinct.
3. **[4 Antipattern] Sort comparators need non-competing buckets.**
   Sorting by a time/urgency value: confirm completed / paused / no-value
   rows are explicitly bucketed away from the active comparison, not left
   to interleave by coincidental raw timestamp.
4. **[1 A11y, measured] Headers don't wrap.** Multi-word column headers
   need `white-space: nowrap`. A wrapped 2-3 line header is a geometry
   smell — engine's `row-misalign`/overlap checks may miss it since it's
   not overlap, eyeball it.
5. **[4 Antipattern] Table fills its container.** `min-width` alone
   without `width: 100%` leaves an unstyled dead zone beside a table
   narrower than its viewport — flag as `major: layout`.
6. **[4 Antipattern] `overflow-x-auto` next to a popover = clipped
   popover.** Per spec, a non-`visible` value on one overflow axis makes
   the other axis compute to `auto` too. If a filter bar or row with a
   floating dropdown menu has `overflow-x-auto` on an ancestor, check the
   dropdown isn't silently unclickable — this is a `critical` interaction
   bug, not just a visual nit, and screenshots alone won't show it (dropdown
   renders fine until you actually try to open one that would overflow).
7. **[1 A11y] Mobile: filters collapse behind a toggle, not squeeze.**
   Below the mobile breakpoint, filter controls should hide behind a
   "Filters" toggle that reveals a dedicated row — not wrap into a messy
   multi-line header or overflow off-screen unreachable.
8. **[1 A11y, measured] Tap target + focus ring floors apply to "label-
   looking" controls too.** A sortable column header, a disclosure
   summary, anything clickable — even if styled as plain text — needs
   ≥24×24 CSS px hit area and a visible `:focus-visible` ring consistent
   with the rest of the app's interactive components. Measure it; don't
   assume a shared component already has it.
9. **[2 Hierarchy] Numbers inside muted labels need their own weight.**
   A count sitting in gray caption text ("Unassigned · 0") reads as inert
   if it's the same muted color as the label. Should be bold/accented.
10. **[3 Consistency] Rounded card touching a straight-edged neighbor
    with zero margin.** A `border-radius`'d section placed flush (no
    gap) against a header/toolbar above or beside it reads as broken —
    the curve has nothing to curve away from. Check first/last children
    in a no-gap flex column especially.
11. **[3 Consistency] "Done" states get a real color, not disabled-gray.**
    A completion icon/badge in flat muted gray reads as *inactive*, not
    *finished* — should use the app's actual success/resolved token.

Full rationale + code sketches for each rule: distilled originally into
a project wiki as `list-control-best-practice.md` (portable — copy it
into any repo's own notes/docs if useful there); this file is the
audit-checklist-shaped version qc-uiux consults directly.
