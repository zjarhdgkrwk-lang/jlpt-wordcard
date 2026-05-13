# Validator Unit Test Results

**Date**: 2026-05-13  
**Branch**: `harden/must-validator-round4`  
**Result**: 16/16 PASS

---

## (5a) `needs_must_directive()` — 11/11 PASS

| Entry | Expected | Got | Status |
|---|---|---|---|
| `{"pos": "부사"}` | True | True | PASS |
| `{"pos": "접속사"}` | True | True | PASS |
| `{"pos": "표현"}` | True | True | PASS |
| `{"pos": "연체사"}` | True | True | PASS |
| `{"pos": "명사", "meaning_ko": "발전"}` | True | True | PASS |
| `{"pos": "명사", "meaning_ko": "영향"}` | True | True | PASS |
| `{"pos": "명사", "meaning_ko": "개"}` | False | False | PASS |
| `{"pos": "명사", "meaning_ko": "비"}` | False | False | PASS |
| `{"pos": "동사"}` | False | False | PASS |
| `{"pos": "い형용사", "meaning_ko": "밝다"}` | False | False | PASS |
| `{"pos": "な형용사", "meaning_ko": "소중함"}` | False | False | PASS |

---

## (5b) `MUST_PATTERN` regex — 5/5 PASS

| Input | Expected | Got | Status |
|---|---|---|---|
| `"The image must clearly show: (a) ..."` | match | match | PASS |
| `"The image must show: ..."` | match | match | PASS |
| `"the image MUST CLEARLY SHOW"` | match | match | PASS |
| `"The image SHOULD clearly show"` | no match | no match | PASS |
| `"A cute dog sitting on grass, flat vector ..."` | no match | no match | PASS |

---

## Notes

- `needs_must_directive` correctly classifies all 4 abstract POS types as requiring MUST
- Abstract noun keywords trigger on "발전" and "영향" but not on concrete nouns "개" / "비"
- `な형용사` with meaning "소중함" returns False (concrete adjective rule — no MUST needed)
- MUST_PATTERN is case-insensitive and matches both "must show" and "must clearly show"
- "SHOULD clearly show" correctly does NOT match (strict MUST only)
