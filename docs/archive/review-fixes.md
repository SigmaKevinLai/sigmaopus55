# Independent review fixes — 2026-10-06

1. Menu entry: opening compact navigation moves focus to first link; Escape restores toggle. Browser Enter activation confirmed.
2. Stale drafts: editing named fields clears the previous draft, hides preview, disables copy and announces rebuilding requirement. Programmatic topic selection from product dialog also invalidates draft. Rebuilding re-enables copy. Browser email edit and topic change cases passed.
3. Focus contrast: light backgrounds use dark #283522; dark hero/process/footer preserve orange; orange contact uses near-black. This addresses focus indicator contrast not covered by the prior text-only axe findings.

Full interaction smoke passes. WCAG 2 A/AA and 2.1 AA axe: zero violations, 33 passing rules in tested mobile draft state. Font subset refreshed for new feedback. These automated checks do not replace screen-reader/user testing or independent WCAG certification.
