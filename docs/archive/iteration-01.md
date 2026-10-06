# Iteration 01 — Application-led material discovery

2026-10-06

- Re-read official product specifications (HTTP 200): http://www.sigmacorp.com/cht/spec/spec.aspx
- Added zinc alloy ingots Zamak-3, Zamak-5, ZSG-3. No extra performance/availability claims.
- Added application finder: automotive/industrial, lightweight precision casting, packaging/rolling, zinc, molten supply.
- Finder opens the existing accessible product dialog; inquiry selection carries the product topic.
- Added static CSS/JS revision query to avoid old cached interaction bundles across deployments.
- Browser checks: 320/390/768/1440 px no horizontal overflow; zinc modal text, inquiry preselection, three-item casting filter all passed.
- axe-core WCAG 2A/2AA/2.1AA: zero violations, 30 passing rules on the tested desktop state.
- Reviewed desktop finder screenshot. Automated checks are not accessibility certification or engineering material recommendations.

Next: repeatable checked-in test harness, fuller alloy-specification access and performance/typography refinement.
