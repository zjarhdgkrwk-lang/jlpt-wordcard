# Sample Prompts — 50-word Test Run

14 entries selected to maximize semantic diversity within the test batch (first 50 rows, N5_4 level).  
POS in this batch: 명사×48, 부사×2. All available adverb entries included; nouns sampled across subcategories.

| global_id | word | reading | meaning_ko | pos | transitivity | front_hint | prompt |
|---|---|---|---|---|---|---|---|
| N5_4_000024 | 犬 | いぬ | 개 | 명사 | | | A cute friendly dog sitting and looking forward with a wagging tail, single subject on plain background, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |
| N5_4_000015 | 雨 | あめ | 비 | 명사 | | | Dark rain clouds in the sky with large raindrops falling down, a small puddle forming on the ground below, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |
| N5_4_000004 | 朝ご飯 | あさごはん | 아침밥, 아침 식사 | 명사 | | | A breakfast table setting with a bowl of rice, miso soup, and chopsticks arranged neatly, morning light suggesting early hour, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |
| N5_4_000016 | 家 | いえ | 집, 집안 | 명사 | | | A simple cozy house with a triangular roof, front door, and one window, viewed from a slight angle, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |
| N5_4_000032 | 海 | うみ | 바다 | 명사 | | | A wide calm ocean scene with gentle blue waves, a bright horizon line, and a single seagull flying above the water, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |
| N5_4_000040 | 鉛筆 | えんぴつ | 연필 | 명사 | | | A single yellow pencil with a sharpened tip and a pink eraser on the end, viewed from a slight angle, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |
| N5_4_000001 | 間 | あいだ | 사이; 동안 | 명사 | | | Two simple houses side by side with a visible gap space between them, a small double-headed arrow spanning the gap to indicate the space between, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |
| N5_4_000011 | 後 | あと | 1. 뒤; 후, 나중 2. 남은 것, 나머지 | 명사 | | | A simple timeline with a marker indicating the present moment and an arrow pointing to the right toward a later point labeled with a clock, suggesting after or later, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |
| N5_4_000020 | 医者 | いしゃ | 의사 | 명사 | | | A doctor in a white coat holding a stethoscope, standing in a simple clinical setting with a small medical cross symbol, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |
| N5_4_22-1 | 一日 | ついたち | 1일; 매달 첫째 날 | 명사 | | 매월 첫날 | A wall calendar page with the number 1 circled prominently at the top of the month grid, indicating the very first day of the month, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |
| N5_4_22-2 | 一日 | いちにち | 1일; 하루, 온종일 | 명사 | | 하루 | A sunrise on the left side and a sunset on the right side of a single horizontal scene, a sun arc traveling across the sky representing one full day, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |
| N5_4_000018 | いくら | いくら | 얼마; 얼마나 | 부사 | | | A price tag on a simple item with a large question mark on it, a person looking at it with a curious expression, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |
| N5_4_000025 | 今 | いま | 지금, 이제 | 부사 | | | A clock face showing the current time with a bold arrow pointing to the clock, a small glowing dot suggesting the present moment right now, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |
| N5_4_000034 | 運動 | うんどう | 운동; 몸을 움직임 | 명사 | | | A person jogging outdoors in a park with motion lines behind them, wearing sporty clothes and sneakers, a small tree in the background, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text |

---

## Notes

- **一日 (N5_4_22-1 vs N5_4_22-2)**: Polysemy handling (§3.7) confirmed working. `front_hint="매월 첫날"` → calendar with "1" circled; `front_hint="하루"` → sun arc across the sky. Two distinct images, no overlap.
- **後 (N5_4_000011)**: Multi-meaning entry `"1. 뒤; 후, 나중 2. 남은 것, 나머지"` — model correctly drew only meaning #1 (temporal "after/later") using a timeline + arrow. §3.7 rule 3 observed.
- **間 (N5_4_000001)**: Abstract noun treated correctly — depicted as spatial gap between two houses with a double-headed arrow. "the act of / a moment of" pattern applied.
- **부사 (いくら, 今)**: Both use visual anchors (price-tag + question mark; clock + dot) rather than abstract depictions. §3.6 부사-빈도/시간 rule followed.
