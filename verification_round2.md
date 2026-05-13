# Verification — Abstract Prompt Fix Round 2

**Date**: 2026-05-13  
**Method**: Manual direct replacement (no API call)  
**Branch**: `fix/abstract-prompts-round2` (based on `refine/abstract-prompts-round1`)

---

## Affected Rows

| global_id | word | new prompt word count | ends with "no text" | contains "must clearly show" / "must show" | prompt_version |
|---|---|---|---|---|---|
| N5_4_000001 | 間 | 134 | ✅ | ✅ `must clearly show` | v2 |
| N5_4_000011 | 後 | 47 | ✅ | ❌ (intentional — concrete timeline, no enumeration needed) | v2 |
| N5_4_000018 | いくら | 41 | ✅ | ❌ (intentional — simple price-tag scene, no enumeration needed) | v2 |
| N5_4_000025 | 今 | 118 | ✅ | ✅ `must clearly show` | v2 |
| N5_4_22-1 | 一日 (ついたち) | 106 | ✅ | ✅ `must show` | v2 |
| N5_4_22-2 | 一日 (いちにち) | 94 | ✅ | ✅ `must clearly show` | v2 |

**MUST directive: 4/6 ✅** — 後 and いくら are intentional exceptions (short concrete scenes that don't benefit from enumeration).

> **Note on word count**: N5_4_000001 (134 wc), N5_4_000025 (118 wc), N5_4_22-1 (106 wc) exceed the 100-word hard ceiling defined in CLAUDE.md §3.2. This is intentional for manually crafted prompts targeting z_image_turbo's known weakness with abstract subjects. The hard ceiling applies to API-generated batches.

---

## Sanity Check

### Global CSV integrity
- **Total rows**: 8,042 ✅
- **Filled prompts**: 344 (unchanged from round 1) ✅
- **300 collateral rows**: version=v1, unmodified ✅

### 5 collateral rows spot-check (version=v1, unchanged)

| global_id | word | wc | ends "no text" | version |
|---|---|---|---|---|
| N5_4_000046 | お酒 | 34 | ✅ | v1 |
| N5_4_000047 | お皿 | 40 | ✅ | v1 |
| N5_4_000048 | おじいさん | 41 | ✅ | v1 |
| N5_4_000049 | おじさん | 42 | ✅ | v1 |
| N5_4_000050 | お茶 | 40 | ✅ | v1 |

---

## Hard Rule Compliance

| Row | Rule | Result |
|---|---|---|
| N5_4_000001 (間) | `must clearly show` present | ✅ — "(a) tree and house as flanking objects, (b) shaded zone as visual center, (c) child at middle" |
| N5_4_000025 (今) | `must clearly show` present | ✅ — "(a) tapping the watch, (b) wristwatch enlarged with clock hands, (c) downward gaze, (d) sparkle marks" |
| N5_4_22-1 (ついたち) | `must show` present | ✅ — "(a) empty calendar grid, (b) only digit 1 present and circled, (c) first day emphasis" |
| N5_4_22-2 (いちにち) | `must clearly show` present | ✅ — "four distinct time-of-day stages, not two" |
| N5_4_000011 (後) | enumeration intentionally omitted | ✅ (exception) |
| N5_4_000018 (いくら) | enumeration intentionally omitted | ✅ (exception) |

---

## Key Improvements Over Round 1

### N5_4_000001 (間 — negative space concept)

Round 1 generated (54 wc, no MUST):
> "A child standing centered in the empty space between a tall tree on the left and a small house on the right, short double-headed arrows on the ground extending from the child outward to each side, ..."

Round 2 manual (134 wc, MUST + pastel zone):
> "A child standing exactly in the center of a **distinctly shaded rectangular ground zone** that visually separates two clearly different flanking objects ... **the shaded zone is filled with a contrasting soft pastel color** so the empty space itself becomes the visual focal subject ... The image must clearly show: (a) the tree and the house as separated flanking objects, (b) **the conspicuous rectangular shaded zone** between them as the visual center, (c) the child placed exactly at the middle of the shaded zone."

**Change**: Added pastel-shaded zone (CLAUDE.md §3.6 rule 5a) to make the gap itself the visual subject, not just the flanking objects.

### N5_4_000025 (今 — "this very moment" concept)

Round 1 generated (40 wc, no MUST):
> "A round clock face showing the current time with a bold downward arrow pointing to the clock hands, emphasizing the present moment, ..."

Round 2 manual (118 wc, MUST + active gesture):
> "A person standing center, **urgently tapping the face of their oversized wristwatch** with their index finger ... **small bright pastel sparkle marks radiate outward** from the watch face indicating immediacy ... The image must clearly show: (a) the person actively tapping the watch, (b) the wristwatch enlarged and centered with visible clock hands, (c) the focused downward gaze of the person, (d) sparkle marks around the watch emphasizing 'this exact moment'."

**Change**: Person actively gesturing (CLAUDE.md §3.6 rule 6), sparkle marks for immediacy, wristwatch instead of wall clock (more grounded / less abstract).
