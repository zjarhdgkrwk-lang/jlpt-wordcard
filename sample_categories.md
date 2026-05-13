# Sample Categories — Pre-Fullscale Coverage Check

12 entries selected to test prompt generation rules across untested POS categories.  
All confirmed present in `data/cards_normalized.csv`.

| # | global_id | level | word | reading | meaning_ko | pos | category_test_point |
|---|---|---|---|---|---|---|---|
| 1 | N3_000860 | N3 | 発展 | はってん | 발전; 전개 | 명사 | N3 추상명사 — abstract noun (development/progress) |
| 2 | N3_000078 | N3 | 影響 | えいきょう | 영향 | 명사 | N2-equiv 추상명사 — abstract noun (influence/impact); found in N3 dataset |
| 3 | N1_000542 | N1 | 事態 | じたい | 사태; 상황 | 명사 | N1 추상명사 — abstract noun (situation/state of affairs) |
| 4 | N5_4_000429 | N5_4 | 静かな | しずかな | 조용한, 고요한 | な형용사 | な형용사 — property adjective (quiet/calm) |
| 5 | N5_4_001266 | N5_4 | 大切な | たいせつな | 소중한; 중요하다 | な형용사 | な형용사 — abstract value adjective (precious/important) |
| 6 | N5_4_000428 | N5_4 | こんな | こんな | 이런; 이와 같은 | 연체사 | 연체사 — adnominal (this kind of) |
| 7 | N5_4_001340 | N5_4 | しかし | しかし | 그러나; 하지만 | 접속사 | 접속사 — conjunction (however/but) |
| 8 | N5_4_001343 | N5_4 | それから | それから | 그리고 나서; 그 후 | 접속사 | 접속사 — conjunction (and then/after that) |
| 9 | N5_4_000525 | N5_4 | おはようございます | おはようございます | 안녕하세요; 좋은 아침입니다 | 표현 | 표현 — expression (good morning greeting) |
| 10 | N5_4_000534 | N5_4 | すみません | すみません | 죄송합니다; 실례합니다 | 표현 | 표현 — expression (excuse me/sorry) |
| 11 | N3_001696 | N3 | わざと | わざと | 일부러; 고의로 | 부사 | 부사(양태) — manner adverb (on purpose/deliberately) |
| 12 | N5_4_000308 | N5_4 | 入れる | いれる | 넣다 | 동사 | 동사(타동사) — transitive verb (to put in/insert) |

## Notes

- **#2 (影響)**: Listed as N3 in the dataset but semantically equivalent to the N2 abstract noun test target (영향/influence). Tests the same abstract-noun pattern.
- **#5 (大切な)**: Borderline abstract な形容詞 — "precious/important" could be depicted concretely (a treasured object) or abstractly. Good stress test for the POS rule.
- **#7/#8 (しかし/それから)**: Both conjunctions but with different visual logic — しかし requires a contrast scene, それから requires a temporal sequence.
- **#9/#10 (おはよう/すみません)**: Expressions must depict the SITUATION not the gesture (§3.6). Risk: model may include text-bubble or speech text.
