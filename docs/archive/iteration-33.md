# Iteration 33 — Metadata disclosure regression guard

2026-10-06

Static gate now checks title/search description/OG title/OG description for explicit nonofficial wording and exact Pages sharing destination. Supports equivalent Traditional Chinese wording 非官方 / 不是官方 instead of brittle single phrase. Initial assertion caught wording variance, not missing disclosure; corrected and reran. All 48 IDs/font/license checks and live 40-value source verification pass. No runtime changes.
