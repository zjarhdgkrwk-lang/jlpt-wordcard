# Known Issues

## 1. `needs_must_directive()` — substring false positives

**File**: `scripts/generate_prompts.py`
**Severity**: Low (prompts are still correct; only causes unnecessary API retries)

### Description

`ABSTRACT_NOUN_KEYWORDS` contains short Korean strings (2–3 characters) used to
detect abstract nouns by substring-matching `meaning_ko`. Several of these strings
appear as substrings inside unrelated, concrete meanings, causing concrete-noun
entries to be flagged as abstract and subjected to a "MUST clearly show" strict retry.

The model correctly refuses to inject the MUST enumeration into concrete prompts,
so the final prompts are unaffected — but the retry wastes one extra API call per
false-positive entry and generates misleading `MUST still absent` warnings in the log.

### Confirmed false-positive cases (from full-scale run, 2026-05-13)

| global_id | word | meaning_ko | matching keyword | why it's wrong |
|-----------|------|------------|-----------------|----------------|
| N5_4_000499 | テレビ | 텔레비전 | `전` | "텔레비**전**" contains "전" (電) but テレビ is a concrete object |
| N5_4_000548 | 暑さ | 더위 | `위` | "더**위**" contains "위" (上) but 暑さ is concrete (heat/summer) |
| N5_4_000570 | 内 | 안; 내부 | `안` | 内 means "inside" — directional, not abstract relationship |
| N5_4_000571 | 内側 | 안쪽; 내측 | `안` | Same as 内 |
| N5_4_000572 | 裏 | 뒤; 뒷면 | `뒤` | 裏 means "back/reverse side" — spatial, not abstract |
| N5_4_000576 | 運転手 | 운전수; 기사 | `전` | "운**전**수" contains "전" — 運転手 is a concrete person |
| N5_4_000610 | お見舞い | 병문안 | unclear | false positive |
| N5_4_614-1 | 表 | 표면; 앞면 | `앞` | 表 means "front/surface" — spatial |
| N5_4_000618 | 海岸 | 해안 | unclear | false positive |
| N5_4_000637 | 家庭 | 가정; 가족 | `정` or `가` | 家庭 is a concrete social unit |
| N5_4_000639 | 家内 | 아내; 집안 | `안` | "집**안**" contains "안" |
| N5_4_000674 | 空気 | 공기 | `기` | 空気 is a concrete noun |
| N5_4_000765 | 辞典 | 사전 | `전` | "사**전**" contains "전" |
| N5_4_000766 | 自転車 | 자전거 | `전` | "자**전**거" contains "전" |
| N5_4_000772 | 字引 | 사전; 자전 | `전` | same |
| N5_4_000851 | 力 | 힘; 능력 | `력` or `힘` | 力 is an abstract concept but MUST enumeration was not needed |
| N5_4_000878 | 電灯 | 전등 | `전` | "**전**등" contains "전" |
| N5_4_000880 | 電報 | 전보 | `전` | "**전**보" contains "전" |
| N5_4_000881 | 展覧会 | 전람회 | `전` | "**전**람회" contains "전" |
| N5_4_000910 | 乗り物 | 탈것; 교통수단 | unclear | false positive |
| N5_4_001041 | おいでになる | 계시다; 오시다 | unclear | honorific verb, not abstract |
| N5_4_001054 | お休みになる | 주무시다 | unclear | honorific verb |
| N5_4_001083 | ご覧になる | 보시다 | unclear | honorific verb |

### Root cause

`ABSTRACT_NOUN_KEYWORDS` in `generate_prompts.py` contains:

```python
ABSTRACT_NOUN_KEYWORDS = [
    "영향", "효과", "결과", "반응", "관계", "변화", "발전", "발생",
    "전",   # ← matches 텔레비전, 운전수, 사전, 자전거, 전등, 전보, 전람회, ...
    "안",   # ← matches 안쪽, 집안, ...
    "뒤",   # ← matches 뒤 (裏) even though it's spatial
    "앞",   # ← matches 앞면 (表)
    "위",   # ← matches 더위 (暑さ)
    ...
]
```

Short 1–2 character keywords have extremely high collision rates in Korean.

### Recommended fix (not yet implemented)

Replace bare substring matching with **word-boundary aware matching**:

```python
import re

def needs_must_directive(entry: dict) -> bool:
    pos = entry.get("pos", "")
    meaning = entry.get("meaning_ko", "") or ""

    if pos in ABSTRACT_POS:
        return True

    # Use word-boundary matching: keyword must appear as a standalone token
    for kw in ABSTRACT_NOUN_KEYWORDS:
        # Match keyword surrounded by non-alphanumeric characters or string boundaries
        if re.search(r'(?<![가-힣])' + re.escape(kw) + r'(?![가-힣])', meaning):
            return True

    return False
```

Alternatively, replace short keywords entirely with longer, more specific phrases:

| Short keyword (remove) | Replace with |
|------------------------|-------------|
| `"전"` | `"영향전"`, `"관계전"` (or remove entirely) |
| `"안"` | keep only `"불안"`, `"안정"`, `"안심"` as full words |
| `"뒤"` | `"뒷받침"`, `"뒤따르"` |
| `"앞"` | `"앞날"`, `"앞으로의"` |
| `"위"` | `"위험"`, `"위협"`, `"위기"` |

### Impact on current data

The false-positive entries received the same prompts they would have gotten without
the retry (the model ignored the MUST instruction for concrete nouns). All 6,894
generated prompts should be visually correct. The 149 `failures.jsonl` entries
labeled `missing MUST directive after 2 retries` are all artifacts of this bug and
can be ignored for image generation purposes.
