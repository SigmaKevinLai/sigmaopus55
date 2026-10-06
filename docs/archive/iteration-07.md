# Iteration 07 — Touch and tablet ergonomics

2026-10-06

- Extended collapsible navigation through 900 px, avoiding a dense five-link header on tablets. Full desktop nav resumes at 901 px.
- Increased key control heights to at least 44 px (menu, brand link, CTA, source links, phone links); tabs at least 48 px.
- Mobile input/select/textarea font size 16 px to reduce unexpected iOS input zoom.
- Section focus indicator remains visible after navigation; initial modal title uses reading focus without unnecessary outlined heading.

Verification: full smoke passes. No horizontal overflow at 320/390/768/800/900/901/1024/1440. Tablet menu opens/closes and transfers focus correctly. Measured menu/CTA/brand/base select/name input at least 44 px tall. Doubling selected content text sizes via injected CSS caused no document overflow at 320/390/800/1440; this is a targeted stress test, not complete browser text-only zoom certification. axe WCAG 2 A/AA and 2.1 AA: zero violations, 30 passing rules on mobile tested state.

Next: final holistic review and maintainable source-data verification, rather than expanding content without purpose.
