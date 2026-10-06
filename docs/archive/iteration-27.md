# Iteration 27 — Clipboard fallback regression

2026-10-06

Integrated clipboard-check as sixth permanent browser suite. Added controlled rejection test: manual fallback focuses draft and selects all text, status explains failure, retry enabled. Existing pending-write/clear race assertions retained. Tests substitute browser clipboard object and do not write actual system clipboard. Runner closes session; README suite list updated. No runtime UI change.
