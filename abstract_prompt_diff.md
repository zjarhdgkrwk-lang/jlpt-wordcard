# Abstract Prompt Refinement — Round 1

**Date**: 2026-05-12  
**Branch**: `refine/abstract-prompts-round1`  
**Scope**: 6 rows identified as abstract-subject or adverb-POS candidates

---

## Affected Rows

| global_id | word | reading | meaning_ko | pos | reason |
|---|---|---|---|---|---|
| N5_4_000001 | 間 | あいだ | 사이; 동안 | 명사 | (a) explicit list — negative-space concept |
| N5_4_000011 | 後 | あと | 1. 뒤; 후, 나중 2. 남은 것, 나머지 | 명사 | (a) explicit list — temporal-sequence concept |
| N5_4_000018 | いくら | いくら | 얼마; 얼마나 | 부사 | (a) explicit list + (b) pos=부사 |
| N5_4_000025 | 今 | いま | 지금, 이제 | 부사 | (a) explicit list + (b) pos=부사 — "right now" concept |
| N5_4_22-1 | 一日 | ついたち | 1일; 매달 첫째 날 | 명사 | (a) explicit list — specific-point-in-sequence concept |
| N5_4_22-2 | 一日 | いちにち | 1일; 하루, 온종일 | 명사 | (a) explicit list — duration/progression concept |

---

## Rule Compliance Check (新プロンプト)

| global_id | word | wc | Ends `no text` | English only | wc 25–100 | Has `MUST` directive | Overall |
|---|---|---|---|---|---|---|---|
| N5_4_000001 | 間 | 54 | ✅ | ✅ | ✅ | ⚠️ absent | ✅ PASS (warning) |
| N5_4_000011 | 後 | 38 | ✅ | ✅ | ✅ | ⚠️ absent | ✅ PASS (warning) |
| N5_4_000018 | いくら | 41 | ✅ | ✅ | ✅ | ⚠️ absent | ✅ PASS (warning) |
| N5_4_000025 | 今 | 40 | ✅ | ✅ | ✅ | ⚠️ absent | ✅ PASS (warning) |
| N5_4_22-1 | 一日 (ついたち) | 43 | ✅ | ✅ | ✅ | ⚠️ absent | ✅ PASS (warning) |
| N5_4_22-2 | 一日 (いちにち) | 60 | ✅ | ✅ | ✅ | ⚠️ absent | ✅ PASS (warning) |

**Core checks (tail · English · word-count)**: ALL PASS  
**Abstract override rule 1 (`MUST` directive)**: 0/6 — see Notes

---

## Before / After Comparison

| global_id | word | meaning | old_prompt | new_prompt |
|---|---|---|---|---|
| N5_4_000001 | 間 | 사이; 동안 | A child standing centered in the empty space between two distinctly different flanking objects (a tall tree on the left and a small house on the right) of similar height; the ground area between the objects is softly shaded in a contrasting pastel tone so the empty space itself reads as the visual subject; short horizontal double-headed arrows on the ground extend outward from the child to each flanking object. **The image must clearly show: (a) two visibly different flanking objects, (b) a child positioned exactly in the middle of the gap, (c) the central ground area visually highlighted by shading, (d) bilateral double-headed arrows from center pointing outward.** flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text | A child standing centered in the empty space between a tall tree on the left and a small house on the right, short double-headed arrows on the ground extending from the child outward to each side, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |
| N5_4_000011 | 後 | 1. 뒤; 후, 나중 | A simple timeline with a marker indicating the present moment and an arrow pointing to the right toward a later point labeled with a clock, suggesting after or later, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text | A person walking away viewed from behind, a small arrow pointing forward indicating future or later, simple ground line beneath, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |
| N5_4_000018 | いくら | 얼마; 얼마나 | A price tag on a simple item with a large question mark on it, a person looking at it with a curious expression, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text | A person holding a price tag with a large question mark on it, standing in front of a single shop counter, curious expression, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |
| N5_4_000025 | 今 | 지금, 이제 | A person at a desk pointing decisively at a wall clock with one finger, mouth slightly open as if saying "right now", the clock face prominently visible behind them showing a specific time, small motion lines around the pointing hand to convey immediacy. **The image must clearly include all of: (a) the active pointing person, (b) the clock as the target of the pointing, (c) sense of "this very moment" through gesture energy.** flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text | A round clock face showing the current time with a bold downward arrow pointing to the clock hands, emphasizing the present moment, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |
| N5_4_22-1 | 一日 (ついたち) | 매월 첫날 | A monthly wall calendar with a clean blank grid: ONLY the date "1" is visible in the top-left cell of the grid, prominently circled in red; ALL OTHER date cells in the grid are completely empty and blank with no numbers whatsoever; the calendar header at the top is also blank with no month name. A hand pointing at the "1". **The image must show: (a) a visibly empty calendar grid, (b) only the digit "1" present and circled, (c) emphasis on this being the very first day.** flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text | A wall calendar page showing a monthly grid with the number 1 circled in the top-left date cell, indicating the first day of the month, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |
| N5_4_22-2 | 一日 (いちにち) | 하루 | A horizontal strip showing the progression of one full day from left to right in four small connected scenes: (1) sunrise with a rooster or person waking, (2) midday with high sun and a person eating lunch, (3) sunset with warm orange sky, (4) night with moon and stars and a person sleeping. A subtle curved arrow above connects all four scenes to convey duration. **The image must clearly show four distinct time-of-day stages, not two.** flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text | A horizontal strip showing four stages of one full day: morning sunrise with a person waking up, midday sun with a person working, evening sunset with orange sky, night moon with a person sleeping, a curved arrow above connecting all four scenes, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |

---

## Notes

### 1. `MUST` directive not adopted (0/6) — partial regression for N5_4_000001 and N5_4_000025

The old prompts for N5_4_000001 (間) and N5_4_000025 (今) already contained explicit `The image must clearly show / include all of` language with enumerated sub-conditions. The new API-generated prompts dropped this language and reverted to simpler descriptions (~40–54 words vs. 81–101 words).

**Root cause**: EX_7 and EX_8 fewshots demonstrate the pattern, but the model distills the core visual idea and omits the verbose enumeration when the concept can be described more concisely. The `MUST` language in the fewshot output is treated as one stylistic option, not a mandatory template.

**Impact on image quality**: Uncertain until render testing. For 間 in particular, without pastel shading of the gap region and explicit "bilateral arrows from center outward", z_image_turbo may render flanking objects but not the gap itself (as predicted by override rule 5).

### 2. N5_4_22-2 (一日 いちにち) — essentially unchanged

Old and new prompts both describe a 4-stage horizontal day-progression strip with a curved arrow. Minor wording differences only. EX_7 fewshot was effective.

### 3. N5_4_000011 (後) — approach changed, not clearly better

Old: abstract timeline with a clock marker.  
New: a person walking away with a forward arrow.

Both are reasonable for "later / after" but the new version may be more intuitively clear (person = subject moving toward the future).

### 4. Next steps

To enforce the `MUST` directive consistently, consider one of:
- Adding `"For abstract-subject entries, your prompt body MUST contain the phrase 'The image must clearly show: (a) ...' listing 2–4 required elements."` to the system prompt.
- Replacing EX_8's output entirely with the longer version currently in old N5_4_000001 (which the model treated as ground-truth before this re-run).
- Post-processing: if `pos` is 부사/접속사/표현 or `word` matches known abstract patterns, assert MUST present before saving.

### 5. Collateral prompts generated

The background process ran 6 full batches (rows 0–349 of the remaining work queue) before being killed, generating **300 additional prompts** on top of the 6 target rows (344 total filled). These are valid prompts generated with the updated fewshots and system prompt. They will be included in the commit.
