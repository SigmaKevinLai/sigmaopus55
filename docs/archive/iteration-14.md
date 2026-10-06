# Iteration 14 — Forced-colors support

2026-10-06

Added system-color borders for cards/buttons/input controls and native Highlight focus indicators in forced-colors mode. Selected tabs and current-location links retain non-color-only emphasis. Decorative product/network/cycle illustrations selectively preserve conceptual colors; readable product captions keep a dark-on-light backing rather than relying on gradient visibility. No blanket opt-out from user contrast settings for interactive text.

Chromium forcedColors=active at 390px: menu keyboard entry, modal opening/closing, and full smoke suite (including widths/filter/comparison/draft invalidate/rebuild/clear) passed. Inspected native system-colored product dialog screenshot: borders, links, closing control and content remain readable. Browser emulation is not actual Windows assistive-technology certification.
