# Iteration 13 — Accessible deterministic reading position

2026-10-06

Replaced observer entry ordering with one requestAnimationFrame-coalesced scroll calculation at the header reading line. Current visible section updates both visual active class and aria-current=location. No stale state on hero or contact/footer when no matching navigation link exists. Passive scroll listener and only six section positions per frame; no dependencies.

New navigation-check tests rapid out-of-order jumps to knowledge/materials/global/circular/about at 390 and 1440 px and reset at hero/footer. Passed alongside full browser-smoke, JS syntax and static references/resources.
