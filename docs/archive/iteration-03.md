# Iteration 03 — Local typography

2026-10-06

## Change
Removed Google Fonts stylesheet and remote preconnections. Added self-hosted WOFF2 subsets: one Noto Sans TC variable face (100–900), four Barlow Condensed weights. Existing current HTML/JS copy supplies the character subset; system fallback covers other characters and user input. Retained SIL OFL license text for both font families. Preloaded the CJK face and brand/display 800 face.

## Evidence
- Previous font stylesheet alone transferred approximately 173 KB and discovered over 20 CJK segment requests in the observed browser.
- New local font payload: Noto 169,160 bytes plus Barlow 62,532 bytes, total 231,692 bytes, five font files; this is not a measured whole-page load-time improvement or direct comparison of total cold-cache payload.
- document.fonts reports all five faces loaded.
- Resource Timing shows zero external resource requests in the tested application page before injecting test tooling.
- Full browser regression passes: four widths, five product paths, composition, tabs, dialog, menu focus and draft-only inquiry.
- Blocking all WOFF2 requests: no overflow at 320/390/1440 widths.
- axe WCAG 2 A/AA and 2.1 AA: zero violations on desktop initial tested state (30 passing rules).

## Maintenance
When editing content, regenerate the CJK subset or rely on fallback for new characters until regenerated. Font subset is a performance artifact, not a complete CJK font. Do not delete license files. Third-party font download was used during development, not at runtime.

Next: add source-controlled font-generation script, cold-load timing/CLS measurement and visual refinement.
