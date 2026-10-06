# Iteration 18 — Responsive focus continuity

2026-10-06

Reset compact menu state at 900px breakpoint changes. Move focus from desktop nav becoming hidden to compact toggle; reverse from disappearing toggle to first desktop nav link. Preserve last header focus because Chromium auto-blurs display:none targets before media-query callback. Escape no longer moves desktop nav focus to hidden toggle.

Initial responsive test exposed auto-blur timing; fixed and reran successfully. Tests cover menu state reset, desktop Escape retention, desktop-to-compact and compact-to-desktop focus. Full smoke passed before timing correction; final focus and responsive checks passed after correction. No new dependencies.
