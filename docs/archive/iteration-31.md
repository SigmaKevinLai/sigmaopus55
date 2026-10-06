# Iteration 31 — Public transport/artifact diagnosis

2026-10-06

Inspected prior failure: Chromium navigation exceeded 60s before DOMContentLoaded, not a specific assertion or UI exception. Independent curl HEAD returns HTTP 200; GitHub API reports built on main root. Root cause beyond these observations is not established.

Added bounded dependency-free public verifier comparing index/app/style/fonts bytes with checkout and returning nonzero on unavailable transport or mismatch. All four public artifacts matched current checkout. This establishes artifact publication, not seven-suite browser interaction pass. README distinguishes evidence classes. No runtime UI payload change.
