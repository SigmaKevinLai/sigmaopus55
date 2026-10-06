# Iteration 02 — ADC composition comparison

2026-10-06

## Content
Five ADC alloy series (3/6/10/12/14), eight elements, transcribed from official specifications: http://www.sigmacorp.com/cht/spec/spec.aspx (HTTP 200 verified in prior research round).
Values retain original ranges/precision; max is displayed as ≤. Reference percentages are labeled, remaining elements and delivery specification must be confirmed with the supplier. No comparative mechanical-performance ranking is inferred.

## Experience
Progressive disclosure avoids overwhelming the main brand story. Two native selectors update semantic row/column headers and status. Differing values receive both visual emphasis and hidden textual explanation. Identical-alloy selection gives a clear status, not an error. No API, tracking or third-party execution dependency is added.

## Verification
- JavaScript syntax passed.
- Eight composition rows render.
- ADC12 silicon range 9.6–12.0 verified.
- ADC14 vs ADC12: six different listed ranges.
- Same-alloy comparison: zero marked differences.
- Open comparison: widths 320/390/768/1440 no document overflow.
- Reusable browser smoke suite passes prior product paths, tabs, dialogs, menu focus and local draft.
- axe WCAG 2 A/AA and 2.1 AA: 0 violations, 33 passing rules on mobile tested state after source-note contrast fix.
- Mobile table screenshot inspected. Automated checks do not constitute certification.

Next: full source-to-data transcription assertion, eliminate render-blocking external typography and performance measurement; broader screen-reader/manual checks.
