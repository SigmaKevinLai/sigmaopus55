# Iteration 16 — Inquiry input quality

2026-10-06

Native constraint validation now rejects whitespace-only name and application description using Traditional Chinese custom messages. Draft generation trims boundary whitespace for name/email/message while preserving meaningful internal text. Reset clears custom validity so old errors do not survive clear-page action.

Browser tests passed: whitespace fields produce no draft and invalid name state; valid boundary-spaced text generates normalized draft; clear action removes custom errors. Full smoke, static integrity and syntax checks passed. No transmission/storage added. Native browser validation UI used rather than untested custom validation widgets.
