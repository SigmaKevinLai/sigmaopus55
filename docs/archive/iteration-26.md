# Iteration 26 — Clipboard async boundaries

2026-10-06

Copy captures an immutable draft snapshot, disables duplicate clicks during pending request and marks aria-busy. Completion/failure updates feedback and fallback selection only if that snapshot is still the displayed draft. Finally reflects actual draft visibility in button state. Clearing or editing during pending copy no longer gets overwritten by late success. Already submitted system clipboard writes cannot be canceled; page-clear does not promise clearing system clipboard.

Controlled pending-promise browser test passes: copy disabled, clear status preserved after late completion, cleared copy remains disabled. Five-suite regression and syntax checks pass. No new copy or font payload.
