# Iteration 06 — Focus and provenance polish

2026-10-06

- Mobile/desktop navigation now transfers focus to the destination section before native anchor scrolling, instead of retaining focus on hidden navigation.
- Product dialog initial focus is its title for reading context.
- Added product-specific source link (introduction for A356.2/slab/liquid, official specs for ADC/zinc).
- Manual-style keyboard automation found a Tab cycle moving to browser chrome at the end of the native dialog controls; explicit forward/backward wrap now keeps the cycle in the modal.
- Five product focus cycles, Escape restoring each trigger, finder trigger restoration and inquiry name-field focus transfer all passed.
- Full prior smoke suite passed before focus-wrap addition. Open zinc dialog axe WCAG 2 A/AA and 2.1 AA: zero violations (16 passing rules, background inert).
- Native dialog semantics, Escape behavior and source provenance remain intact. Tests are not screen-reader certification.

Next: rerun full final smoke suite, increase target-size coverage, source validation script and polish mid-size navigation layout.
