# Iteration 04 — Finishing the inquiry journey

2026-10-06

- Added one-click clipboard copy, explicit failure fallback to selected text, and clear-page-data operation.
- Clearing resets fields and draft, hides actions and restores name-field focus. Message clarifies that the system clipboard is not automatically erased.
- No transmission, recipient guess or local storage added.
- Clipboard success verified with granted browser permission; clipboard rejection verified using injected failure. Existing product/comparison/mobile regression passes after narrowing the submit-button test locator.
- axe WCAG 2 A/AA and 2.1 AA: 0 violations, 33 passing rules with visible draft actions.
- Added repeatable performance lab and font-subset maintenance scripts.

## Local fresh-context measurement before final font refresh
No network/CPU throttling; localhost, one sample per viewport, not production field Core Web Vitals.
- 390 px: LCP 136 ms, cumulative observed layout shifts 0.0177.
- 1440 px: LCP 168 ms, cumulative observed layout shifts 0.0012.
- Both: 0 external requests, resource transfers 277,253 bytes excluding HTML.

These timings are not representative of real-world internet latency. Font coverage refreshed for new UI text, increasing Noto subset by 5,796 bytes; font URL revision avoids stale assets. Do not compare these local metrics to award-winning design quality or claim a load-time improvement percentage.

Next: visual rhythm/editorial refinement, formal source-to-data test script and broader dialog/screen-reader manual checks.
