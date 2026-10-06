# Iteration 20 — Reliable consolidated browser gate

2026-10-06

Added dependency-free runner for four interaction suites. Unique session, explicit Chromium environment, bounded process timeouts, per-suite reporting, finally cleanup and CLI error-text detection (because playwright-cli can return 0 while reporting ### Error). Optional target URL allows same gate against public Pages.

Executed all four suites on localhost: passed, browser closed. Repeated font/disclosure/resource/ID checks and official 40-value source verification: passed. README documents single-command quality gate. No runtime UI change or extra client payload.
