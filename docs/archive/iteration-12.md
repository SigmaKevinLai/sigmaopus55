# Iteration 12 — Deterministic cross-section focus

2026-10-06

Removed hard-coded 350ms focus timer after product inquiry. It could refocus name after a fast keyboard user had already moved to email. Inquiry now cancels native anchor default, closes dialog, sets focus synchronously without scroll, scrolls contact with CSS-controlled motion, and replaces fragment without introducing modal-return history entries. Reduced motion remains governed by existing stylesheet.

Updated focus regression to require immediate name focus, then Tab to email and wait 450ms to prove no delayed focus theft. Full focus and interaction suites pass, 45-ID/resource check passes, app syntax passes. No new content, tracking or external dependency added.
