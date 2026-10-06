# Iteration 19 — Deployment integrity guards

2026-10-06

Extended dependency-free checks to enforce exact CJK preload/font-face URL match, one variable CJK face, real WOFF2 binary signatures, both SIL OFL license files, and nonofficial concept disclosure. Repeated optional live-source validation: all 40 alloy ranges still match. Existing 45-ID/reference/asset checks and app syntax pass.

These guards prevent future cache-version divergence, corrupt font downloads, accidental license omission or misleading loss of demo disclosure. No runtime payload changed.
