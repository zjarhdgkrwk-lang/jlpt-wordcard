# Sample Validation — Category Coverage Check

**Date**: 2026-05-13  
**Branch**: `sample/category-coverage-check`  
**Script**: inline `call_claude()` from `scripts/generate_prompts.py` (EX_1–EX_8 fewshots)  
**Batch**: 12 entries, single API call

---

## Per-Prompt Check

Abstract judgment:  
- `pos ∈ {부사, 접속사, 표현, 연체사}` → MUST required  
- `pos == 명사` + abstract meaning (발전/영향/사태/관계/변화 etc.) → MUST required  
- `pos ∈ {동사, い형용사, な형용사}` → MUST not required (concrete behaviour)

| # | word | pos | wc | ends "no text" | English only | "must clearly show" | issue? |
|---|---|---|---|---|---|---|---|
| 1 | 発展 | 명사(추상) | 54 | ✅ | ✅ | ❌ | MUST missing |
| 2 | 影響 | 명사(추상) | 43 | ✅ | ✅ | ❌ | MUST missing |
| 3 | 事態 | 명사(추상) | 47 | ✅ | ✅ | ❌ | MUST missing |
| 4 | 静かな | な형용사 | 41 | ✅ | ✅ | — (not required) | — |
| 5 | 大切な | な형용사 | 43 | ✅ | ✅ | — (not required) | — |
| 6 | こんな | 연체사 | 46 | ✅ | ✅ | ❌ | MUST missing |
| 7 | しかし | 접속사 | 54 | ✅ | ✅ | ❌ | MUST missing |
| 8 | それから | 접속사 | 51 | ✅ | ✅ | ❌ | MUST missing |
| 9 | おはようございます | 표현 | 46 | ✅ | ✅ | ❌ | MUST missing |
| 10 | すみません | 표현 | 41 | ✅ | ✅ | ❌ | MUST missing |
| 11 | わざと | 부사 | 39 | ✅ | ✅ | ❌ | MUST missing |
| 12 | 入れる | 동사(타동사) | 41 | ✅ | ✅ | — (not required) | — |

**Core checks (tail / English / wc 25–100)**: ALL 12 PASS  
**MUST directive**: 0/9 required entries have it — same systemic gap as Round 1

---

## Risk Flags

| Flag type | Count | Affected entries |
|---|---|---|
| `MUST` directive absent (abstract) | 9 | #1–3, #6–11 |
| Text-leak keywords (`saying`, `speech bubble`, etc.) | **0** ✅ | none |
| wc > 100 | **0** ✅ | none |
| Empty prompt | **0** ✅ | none |
| Non-English characters | **0** ✅ | none |

**표현 prompts (#9, #10) are CLEAN** — no "saying / as if speaking / speech bubble" patterns. Model correctly depicts situations, not gestures.

---

## Quality Assessment by POS

### 명사 — 추상 (#1 発展, #2 影響, #3 事態)

| # | word | approach | quality |
|---|---|---|---|
| 1 | 発展 | Before/after diptych: village → modern town, rightward arrow | ✅ Good visual metaphor |
| 2 | 影響 | Domino chain reaction, curved arrow | ✅ Strong intuitive metaphor |
| 3 | 事態 | People at table with map + warning exclamation mark | ⚠️ Concept may be ambiguous without MUST anchors |

発展 and 影響 produce naturally clear images even without MUST — the visual metaphors are unambiguous. 事態 (serious situation) is riskier: "people at table with map" could read as a planning meeting rather than an urgent state of affairs. MUST enumeration would help here.

### な형용사 (#4 静かな, #5 大切な)

Both correctly apply the §3.6 rule ("context object bearing the property"):
- 静かな: library corner + armchair reader (environment conveys quietness) ✅
- 大切な: child holding plant + warm glow (object + emotional emphasis) ✅

No MUST required — na-adjectives are concrete behaviour patterns.

### 연체사 (#6 こんな)

Person pointing at nearby gift box with short arrow — §3.6 adnominal rule ("person pointing + target object") correctly applied. Proximity ("right in front") conveys "this kind of" well.

### 접속사 (#7 しかし, #8 それから)

Both use two-panel compositions per §3.6 conjunction rule:
- しかし: sunny-sky panel vs rain-cloud panel, divider arrow — contrast is clear ✅
- それから: meal panel → walking-out panel, rightward arrow — sequence is clear ✅

Neither has MUST but both are structurally sound. Risk: z_image_turbo at 8 steps might collapse the two-panel layout into a single scene. MUST enumeration ("must clearly show: (a) left panel ... (b) right panel ... (c) connecting arrow") would reduce this risk.

### 표현 (#9 おはようございます, #10 すみません) — ✅ Notable success

- おはようございます: neighbors at doorstep, one waving hello, sunrise in background — SITUATION, no gesture ✅
- すみません: sidewalk bump, apologetic hand raise — SITUATION, no bow ✅

No text-leak keywords. Both correctly avoid the prohibited "bowing" pose (§3.6 표현). This category works well out of the box.

### 부사 (#11 わざと)

Child deliberately knocking over blocks + mischievous grin + motion lines. "Intentional" manner conveyed by gaze direction + expression, not language. ✅ Clean.

### 동사 타동사 (#12 入れる)

Hand dropping apple into box, side view, apple mid-fall — decisive contact moment per §3.6. ✅ Textbook example.

---

## Systemic Finding: MUST Directive Absent in 9/9 Abstract Cases

Same pattern as Round 1 and Round 1-regen. The model understands the visual structure (diptych, domino metaphor, two-panel) but never writes the enumeration directive. This is a system-prompt hardening issue, not a POS-rule issue.

**Recommendation for Part 2**: Add to SYSTEM_PROMPT before full-scale run:

```
HARD RULE: For any entry where pos is 부사, 접속사, 표현, 연체사,
OR where the noun meaning is abstract (action/relationship/social concept),
you MUST include the sentence:
  "The image must clearly show: (a) ..., (b) ..., (c) ..."
listing 2-4 required visual elements. Prompts without this sentence for
abstract entries will be rejected.
```

---

## Full Prompts

**#1 N3_000860 — 発展 (발전; 전개) [명사, N3]** wc=54  
A split before-and-after composition: left side shows a small simple village with a few huts, right side shows the same location grown into a modern town with taller buildings and trees, a rightward arrow between them, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text

---

**#2 N3_000078 — 影響 (영향) [명사, N3]** wc=43  
A large falling domino knocking over a row of smaller dominoes in a chain reaction, side view with a curved arrow showing the spreading effect, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text

---

**#3 N1_000542 — 事態 (사태; 상황) [명사, N1]** wc=47  
A group of three people gathered around a table looking at a map with worried expressions, a single warning exclamation symbol above the table suggesting a serious unfolding situation, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text

---

**#4 N5_4_000429 — 静かな (조용한, 고요한) [な형용사]** wc=41  
A calm library reading corner with a single person sitting quietly in an armchair reading a book, soft muted tones, no activity around, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text

---

**#5 N5_4_001266 — 大切な (소중한; 중요하다) [な형용사]** wc=43  
A child carefully holding a small potted plant with both hands, treating it gently and protectively, warm soft glow around the plant to convey preciousness, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text

---

**#6 N5_4_000428 — こんな (이런; 이와 같은) [연체사]** wc=46  
A person pointing at a small nearby object such as a colorful gift box right in front of them, short pointing arrow from hand to object indicating closeness, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text

---

**#7 N5_4_001340 — しかし (그러나; 하지만) [접속사]** wc=54  
Two small panels side by side: left panel shows a bright sunny sky with a smiling sun, right panel shows dark rain clouds with falling rain, a bold contrasting arrow or divider between them indicating contradiction, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text

---

**#8 N5_4_001343 — それから (그리고 나서; 그 후) [접속사]** wc=51  
Two small panels connected by a rightward arrow: left panel shows a person eating a meal at a table, right panel shows the same person walking out the door afterward, indicating sequential action, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text

---

**#9 N5_4_000525 — おはようございます (안녕하세요; 좋은 아침입니다) [표현]** wc=46  
Two neighbors meeting at a doorstep in the early morning, one opening the front door and the other waving hello, a soft sunrise glow visible in the background, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text

---

**#10 N5_4_000534 — すみません (죄송합니다; 실례합니다) [표현]** wc=41  
A person accidentally bumping into another person on a sidewalk, one person raising a hand in an apologetic gesture, both facing each other, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text

---

**#11 N3_001696 — わざと (일부러; 고의로) [부사]** wc=39  
A child deliberately knocking over a stack of blocks while looking sideways with a mischievous grin, motion lines showing intentional push, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text

---

**#12 N5_4_000308 — 入れる (넣다) [동사, 타동사]** wc=41  
A hand dropping a red apple into an open cardboard box, side view showing the apple mid-fall entering the box, decisive contact moment, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text
