# Iteration 23 — Product dialog semantics

2026-10-06

Dialog now exposes the concise product description through aria-describedby. Source and inquiry links get product-specific accessible names, retaining exact visible label phrases for speech-input compatibility and adding new-tab context to source links. Static checker validates aria-describedby references as well. Five-suite browser gate and syntax/integrity checks passed. No claims of screen-reader certification; semantic change keeps visual layout unchanged.
