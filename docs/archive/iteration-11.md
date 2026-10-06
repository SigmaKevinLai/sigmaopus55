# Iteration 11 — Controlled throttled performance

2026-10-06

Added repeatable Chromium CDP test with three fresh 390x844 contexts, cache disabled, 150ms network latency, 1.6Mbps download / 750Kbps upload, 4x CPU slowdown. Uses active page site root. Each context closed even on failure; failures retained per sample instead of losing whole batch.

Local controlled results:
| Sample | LCP ms | summed CLS | resource transfer bytes | external requests |
|---|---:|---:|---:|---:|
| 1 | 980 | 0.0037 | 306194 | 0 |
| 2 | 968 | 0.0184 | 306194 | 0 |
| 3 | 968 | 0.0183 | 306194 | 0 |

Median LCP 968 ms; median summed CLS 0.0183. Transfer excludes navigation HTML. CLS is summed observed non-input shifts, not formal session-window field CLS; values reflect loaded local browser test only. No assertion of internet field CWV or interaction latency/INP.

Attempted same cold-context lab on public Pages; first sample exceeded 60s navigation timeout in this environment. No public throttled number claimed. Public ordinary rendered and interaction verification passed in iteration 10. Keep this network failure separate from measured local evidence rather than extrapolating. No extra preload was added without measurable need.

README includes run commands and interpretation. Follow-up: repeat controlled measurements after asset changes and collect real-user testing outside this harness.
