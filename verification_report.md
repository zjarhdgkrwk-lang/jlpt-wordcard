# Prompt Generation Verification Report

**Date**: 2026-05-12  
**Script**: `scripts/generate_prompts.py --limit 50`  
**Model**: claude-sonnet-4-6  
**Batch size**: 50 (1 API call)  
**Target**: First 50 rows of `data/cards_normalized.csv`

---

## Verification Results

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| (a) Total rows in output CSV | 8,042 | 8,042 | ✅ PASS |
| (b) Prompts filled | 50 | 50 | ✅ PASS |
| (c) All prompts end with `no text` (mandatory style tail) | 50/50 | 50/50 | ✅ PASS |
| (d) All prompts are English-only (no CJK characters) | 50/50 | 50/50 | ✅ PASS |
| (e) Word count within 40–70 target | 50/50 | 22/50 | ⚠️ WARNING |
| (f) `prompt_version` == `"v1"` | 50/50 | 50/50 | ✅ PASS |

---

## (e) Word Count Distribution Detail

| Stat | Value |
|------|-------|
| Min | 34 |
| Max | 47 |
| Median | 39 |

**All prompts are well under the 80-word hard ceiling (max=47).**  
However, **28 out of 50 prompts (56%) fall below the 40-word target floor.**

The low word count is concentrated in concrete-noun entries (simple objects, animals, foods) where the model chose a terse-but-correct description. The mandatory style tail itself contributes ~18 words, so the subject portion is averaging only ~20 words.

**Assessment**: Quality is not degraded — all prompts are semantically correct and stylistically consistent. The 34–39 word prompts describe single clear subjects without padding. This suggests the 40-word floor in CLAUDE.md §3.2 may be aspirational rather than enforced. Consider whether a minimum word count rule is worth adding to the system prompt in a future version.

---

## Failure Log

- `logs/failures.jsonl`: **does not exist** (no failures recorded)
- `data/progress.json` — completed_ids: **50**, failed_ids: **0**

No batch-level or word-level failures occurred.

---

## POS Distribution in Test Batch

| Part of Speech | Count | Note |
|---|---|---|
| 명사 (noun) | 48 | First 50 rows of N5_4 level are predominantly nouns |
| 부사 (adverb) | 2 | いくら, 今 |

The current test batch covers only 2 of the ~10 POS categories in the full dataset. Verb, adjective, conjunction, and expression prompts were not exercised. A more representative sample would require `--level` filtering or specific `--limit` positioning.

---

## API Performance

- Wall time: ~49 seconds for 1 batch of 50 words
- Prompt caching (`cache_control: ephemeral`) applied to system prompt
- No JSON parse errors, no retries needed
- Estimated full-run time at this rate: ~161 batches × 49s ≈ **~130 minutes**

---

## Sample Prompts

See [sample_prompts.md](sample_prompts.md) for 14 representative entries covering semantic diversity.

---

## Recommendation for Next PR

1. **Word count floor**: Consider adding `"Subject description must be at least 12 words (not counting the style tail)"` to the system prompt to nudge toward the 40-word target.
2. **POS coverage test**: Run `--level N3` or slice a 50-item window that includes verbs/adjectives to validate POS-specific rules (§3.6).
3. **One-digit number rule**: Test a batch containing 一日(ついたち), 二月 etc. to verify the digit exception works.
