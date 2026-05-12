# Japanese Vocabulary Image Generation Pipeline

## 1. Project Overview

JLPT N5_4 ~ N1 일본어 어휘 카드 **8,042개**에 대해 각 단어별로 학습용 일러스트레이션을 생성하는 파이프라인. 출력 이미지는 Anki 카드의 비주얼 보조로 사용된다.

- 입력: `data/cards_normalized.csv` (단어, 읽기, 의미, 품사 정보 포함)
- 중간 산출물: `data/cards_with_prompts.csv` (영문 이미지 프롬프트가 추가됨)
- 최종 산출물: `images/{global_id}.webp` (768×768, webp, ~50KB)
- 사용 모델: **z_image_turbo_bf16.safetensors** (ComfyUI)
- 프롬프트 생성: **Claude Sonnet 4.6** via Anthropic API

### 핵심 아키텍처 원칙

Claude Code의 역할은 **파이프라인 스크립트의 작성·유지·디버깅·QA**이지, 8천 개의 프롬프트를 직접 작성하는 것이 아니다. 프롬프트 생성은 `scripts/generate_prompts.py`가 Anthropic API를 호출해 배치로 처리한다. Claude Code가 채팅 루프로 8천 번 돌리면 안 된다.

---

## 2. Directory Layout

```
.
├── CLAUDE.md                       # 이 파일
├── data/
│   ├── cards_normalized.csv        # 원본 (read-only)
│   ├── cards_with_prompts.csv      # 프롬프트가 채워진 작업 파일
│   └── progress.json               # 체크포인트 (마지막 완료 global_id, 실패 목록)
├── scripts/
│   ├── generate_prompts.py         # CSV → 영문 프롬프트 생성
│   ├── comfy_runner.py             # 프롬프트 → ComfyUI → webp
│   ├── sample_review.py            # QA용 샘플 50개 HTML 갤러리
│   └── verify_outputs.py           # 결손/깨진 webp 검출
├── workflows/
│   └── z_image_turbo.json          # ComfyUI workflow 템플릿 (placeholder 포함)
├── images/                         # 최종 출력 디렉토리
├── logs/
│   ├── generate_prompts.log
│   ├── comfy_runner.log
│   └── failures.jsonl              # 실패한 단어별 사유
└── samples/                        # sample_review.py 산출물
```

---

## 3. Prompt Style Guide (이 섹션은 generate_prompts.py의 system prompt에 그대로 들어간다)

> **언어**: 모든 출력 프롬프트는 영어. z_image_turbo가 영어에서 가장 안정적임.

### 3.1 Mandatory style tail (모든 프롬프트의 끝에 그대로 붙임)

```
flat vector illustration, soft pastel colors, minimal clean composition,
plain white background, centered, children's textbook style, no text
```

이 블록은 절대 변경하지 않는다. 실험에서 8,042개 전반에 걸쳐 시각적 일관성을 보장하는 것이 검증됨.

### 3.2 Prompt skeleton

```
<subject + action/scene (12-30 words)>,
<optional disambiguation cue (front_hint)>,
flat vector illustration, soft pastel colors, minimal clean composition,
plain white background, centered, children's textbook style, no text
```

Target total length: **25-50 words** including the mandatory style tail (~17 words). For abstract subject override cases (see §3.6), **60-90 words** is acceptable due to required element enumeration. Hard ceiling: **100 words**.

### 3.3 Composition rules

| 규칙 | 이유 |
|---|---|
| Single focal subject. 여러 객체는 의미에 꼭 필요한 경우에만. | 카드 썸네일 크기에서 식별 용이 |
| 측면 또는 3/4 시점을 선호. 정면 얼굴은 피사체가 사람일 때만. | 모델이 측면을 더 안정적으로 그림 |
| 텍스트 금지. 단, 한 자리 숫자(1~9)는 의미상 필수일 때 허용 (예: 一日=1, 二月=2). | 학습 카드 텍스트는 Anki UI에서 별도 제공 |
| 그림자·그라데이션 최소. 단색 면 위주. | flat vector 스타일 유지 |
| 배경 요소는 ≤2개. | 미니멀 일관성 |

### 3.4 Discouraged elements (z_image_turbo가 약한 부분)

- **복잡한 인체 포즈**: 절(おじぎ), 무릎 꿇기, 악수, 양손을 등 뒤로 묶기 등 → 단순 포즈로 대체
- **다인 상호작용에서의 손-손 접촉**: 손끝이 뭉개짐 → 둘 다 있되 거리 두기
- **복잡한 건축 원근**: 공항·역사·교실 내부 전체 → 상징물 1개로 축약 (예: 공항 → 비행기 한 대)
- **거울/반사 이미지, 액자 안 액자 구조**: 모델이 헷갈림
- **글자 렌더링이 필요한 표지·간판**: "no text" 위반

### 3.5 Encouraged tricks

- **방향 화살표**: 자동사·이동·증감 부사에 효과적 (`small arrow indicating upward direction`)
- **Before/after diptych**: 변화 부사·시간 부사에 효과적 (`split composition: left side shows X, right side shows Y, small arrow between them`)
- **단일 큰 객체 + 작은 환경 단서**: 형용사에 효과적 (예: bright → 큰 창문 + 바닥에 햇빛 자국)
- **Side profile + motion indicator**: 동사에 효과적

### 3.6 POS-specific rules

#### 명사 — 구체 (animal, object, food, nature)
한 객체 단독, 정면 또는 비스듬한 각도. 추가 소품 0~1개.
- 犬 → `A cute friendly dog sitting and looking forward, single subject, ...`
- 雨 → `Rain falling from a small gray cloud, several raindrops, a puddle on the ground below, ...`

#### 명사 — 추상 (귀국, 발휘, 사퇴, 手間 등)
그 개념이 발생하는 **전형적 한 장면**. 동명사 구조로 묘사("the act of ...", "a moment of ..."). 복잡한 배경은 상징물 1개로 축약.
- 帰国 → `A traveler with a suitcase smiling beside a small airplane on the ground, suggesting returning home, ...` (jet bridge 같은 복잡한 구조물 X)
- 発揮 → `A person on a stage performing confidently with a spotlight on them, showing their ability, ...`

#### 동사 — 타동사 (transitivity = 타동사)
주체 + 대상 + 그 사이의 명확한 영향 관계. 손이 대상에 닿는 결정적 순간.
- 開ける → `A hand pulling open a wooden door, the door visibly ajar, ...`
- verb_note의 활용형(5단/1단/サ변/カ변)은 프롬프트에 영향 없음 (시각 의미만 그림)

#### 동사 — 자동사 (transitivity = 자동사)
주체 자체의 상태 변화. 변화 방향을 화살표·자세·궤적으로 표현.
- 上がる → `A person walking up a flight of stairs viewed from the side, upward direction emphasized with a small arrow, ...`

#### 동사 — 양쪽 (transitivity 빈칸)
가장 흔한 용례로 그림. 명확하지 않으면 자동사 패턴.

#### い형용사 / な형용사
그 성질이 **두드러진 대상**을 직설적으로. 형용사가 사물의 성질이면 그 사물을, 사람의 성질이면 그 사람의 표정·자세를.
- 明るい → 단순히 "sunshine"이 아니라 `A sunny living room with bright sunlight streaming through a large window, warm yellow light pool on the wooden floor, simple furniture` — **반드시 context object(방·인테리어)를 함께 명시**해야 미니멀 과잉으로 빠지지 않음
- 多義어(明るい = 빛/성격)는 첫 의미만 그림. meaning_ko 첫 세미콜론 앞 사용.

#### 부사 — 정도/변화 (めっきり, ますます, だんだん, ぐっと)
**Before/after diptych** 패턴 사용.
- めっきり → `A split composition: left side shows a green leafy tree in summer, right side shows the same bare tree in winter snow, an arrow between them indicating noticeable change, ...`

#### 부사 — 양태 (のんびり, ゆっくり, しっかり, きちんと)
**행위자 + 그 manner를 드러내는 환경/자세**.
- のんびり → `A person relaxing in a hammock between two trees on a sunny afternoon, eyes closed, peaceful mood, ...`

#### 부사 — 빈도/시간 (まだ, もう, よく, ときどき)
시계·달력·반복 모티프 활용.
- まだ → `A clock showing 9 o'clock with a small "ongoing" arrow, a coffee cup half full beside it, suggesting something not yet finished, ...`

#### 접속사 (でも, ところで, けれども)
**두 장면 + 연결 기호**. 추상적이지만 시각적으로 풀 수 있음.
- でも → `Two panels side by side: left shows sunny weather with a person smiling, right shows the same person under rain but still smiling, connected by a small "but" arrow, ...`

#### 표현 (ありがとうございます, いただきます, よろしくお願いします)
**포즈가 아니라 상황을 그린다.** 절 같은 복잡 포즈는 z_image_turbo가 약하므로 회피.
- ありがとうございます → `A customer receiving a small gift-wrapped package from a shop clerk across a counter, both smiling warmly, simple shop interior, ...`
- いただきます → `A person sitting at a table with a bowl of rice and chopsticks, hands gently together in front of the chest, about to start a meal, ...`
- よろしくお願いします → `Two people facing each other with a small handshake gesture, friendly atmosphere, simple office setting, ...`

#### 연체사 (あんな, こんな, そんな, 大きな)
**손가락으로 가리키는 인물 + 대상 사물**.
- あんな → `A person pointing at a far-away object with a thoughtful expression, the object visible in the distance, ...`
- 大きな → `A small person standing next to a very large object (like a giant tree), size contrast emphasized, ...`

#### Abstract subject override (CRITICAL)

When the word is an abstract noun (time, space, social/action concepts)
or a time/degree/manner adverb, the "minimal single subject" preference
of the style tail produces ambiguous images at z_image_turbo's 8 steps.
For these, deliberately COUNTERACT the tail with explicit redundancy.

Rules:
1. Enumerate 2-4 required elements with a "MUST be visible" directive:
   "The image must clearly show: (a) ..., (b) ..., (c) ..."
2. Prefer "human actor + symbolic anchor" over symbol alone. A small
   person performing/inhabiting the concept grounds the abstraction.
3. For "specific point in a sequence" concepts: explicitly blank out
   competing elements. ("only X visible", "all other cells empty", "no
   labels on other items").
4. For duration/progression concepts: use a horizontal 3-4 stage
   left-to-right strip with a connecting arrow, not a single moment.
5. For NEGATIVE SPACE concepts (gap, between, interval): the empty
   space itself must be made visually conspicuous via (a) pastel
   shading of the empty region, (b) a person or marker placed in it,
   (c) bidirectional arrows from the center outward to flanking
   objects. Without this, models render the surrounding objects but
   not the gap itself.
6. For "this very moment / right now" concepts: use a person actively
   gesturing at the time indicator (pointing, looking at watch), not
   the indicator alone.
7. Avoid speech bubbles, captions, labels, signs — these tend to leak
   text in the output.

The mandatory style tail still appends as usual.

### 3.7 Polysemy handling (중요)

CSV에는 동일 word가 다른 `front_hint`와 `reading_hiragana`로 두 번 등장하는 경우가 있다 (예: 一日의 ついたち vs いちにち).

**규칙**:
1. `front_hint` 컬럼이 비어있지 않으면 → 그 hint가 가리키는 의미만 그린다. `meaning_ko`는 무시 가능.
2. `front_hint`가 비어있고 `meaning_ko`에 세미콜론(`;`)이 있으면 → 첫 번째 세미콜론 앞의 의미만 그린다.
3. `meaning_ko`에 번호(`1.`, `2.`)가 있으면 → `1.`의 의미만 그린다.
4. 두 의미를 한 이미지에 동시에 그리지 않는다.

예시:
- `word=一日, front_hint=매월 첫날, reading=ついたち` → 달력의 1일
- `word=一日, front_hint=하루, reading=いちにち` → 해뜨고 지는 하루의 흐름
- `word=後, meaning_ko="1. 뒤; 후, 나중 2. 남은 것, 나머지"` → "뒤·후"만 그림 (시계나 사람 뒤 화살표)

### 3.8 Few-shot exemplars (테스트에서 검증된 프롬프트)

generate_prompts.py에 few-shot으로 그대로 넣을 것:

```
[
  {"word": "犬", "reading": "いぬ", "meaning": "개", "pos": "명사",
   "prompt": "A cute friendly dog sitting and looking forward, single subject, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text"},

  {"word": "雨", "reading": "あめ", "meaning": "비", "pos": "명사",
   "prompt": "Rain falling from a small gray cloud, several visible raindrops, a puddle on the ground below, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text"},

  {"word": "開ける", "reading": "あける", "meaning": "열다", "pos": "동사", "transitivity": "타동사",
   "prompt": "A hand pulling open a wooden door, the door visibly ajar, motion arc suggesting opening action, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text"},

  {"word": "上がる", "reading": "あがる", "meaning": "올라가다", "pos": "동사", "transitivity": "자동사",
   "prompt": "A person walking up a flight of stairs viewed from the side, upward direction emphasized with a small arrow, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text"},

  {"word": "のんびり", "reading": "のんびり", "meaning": "느긋하게", "pos": "부사",
   "prompt": "A person relaxing in a hammock between two trees on a sunny afternoon, eyes closed, calm peaceful mood, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text"},

  {"word": "めっきり", "reading": "めっきり", "meaning": "눈에 띄게, 부쩍", "pos": "부사",
   "prompt": "A split composition: left side shows a green leafy tree in summer, right side shows the same tree bare with snow in winter, a small arrow between them indicating noticeable change, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text"},

  {"word": "一日", "reading": "ついたち", "meaning": "1일; 매달 첫째 날", "pos": "명사", "front_hint": "매월 첫날",
   "prompt": "A wall calendar page with the date \"1\" clearly marked and circled at the top-left corner of the month grid, indicating the first day of the month, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text"}
]
```

---

## 4. Prompt Generation (`scripts/generate_prompts.py`)

### 4.1 Input/Output contract

- **Input**: `data/cards_normalized.csv` (8,042 rows, UTF-8-sig)
- **Output**: `data/cards_with_prompts.csv` (input 컬럼 + `prompt`, `prompt_version` 컬럼 추가)
- **State**: `data/progress.json` — `{"last_completed_global_id": "...", "failed": [...]}` 형태

### 4.2 Batching

- **배치 사이즈: 50개/호출**. 시스템 프롬프트(스타일 가이드 ~2k 토큰) + 50개 단어 = 입력 ~3k, 출력 ~3.5k. 안전한 영역.
- 8,042 ÷ 50 ≈ **161회 호출**.
- 50보다 작으면 호출 횟수↑·캐시 효율 동일하나 wall-time↑. 100 이상으로 키우면 JSON 잘림·후반 품질 저하 사례 있음. 50이 검증된 sweet spot.

### 4.3 Prompt caching

시스템 프롬프트(이 CLAUDE.md의 섹션 3 전체 + few-shot exemplars)는 매 호출 동일하므로 **`cache_control: ephemeral`** 적용. 입력 비용 ~80% 절감.

```python
system = [
    {
        "type": "text",
        "text": STYLE_GUIDE_TEXT,  # 섹션 3 전체
        "cache_control": {"type": "ephemeral"}
    }
]
```

### 4.4 API call shape

- Model: `claude-sonnet-4-6` (또는 환경변수)
- Max tokens: 8000
- Temperature: 0.4 (창의성과 일관성의 절충)
- 응답 강제: `"Return ONLY a JSON array of 50 objects with keys `global_id` and `prompt`. No prose, no markdown code fences."`
- 파싱: `json.loads(response.content[0].text)`. 실패 시 한 번 재시도(temperature=0.2). 두 번째도 실패면 그 배치 전체를 failures.jsonl에 기록하고 다음 배치로.

### 4.5 Resume logic

`progress.json`의 `last_completed_global_id` 이후부터만 처리. `--restart` 플래그로 처음부터 가능. `cards_with_prompts.csv`는 append 모드가 아니라 매 배치마다 전체 rewrite (안전성 우선, 파일 크기 작음).

### 4.6 Common commands

```bash
# 처음부터 전체 생성
python scripts/generate_prompts.py

# 특정 범위만 (테스트용)
python scripts/generate_prompts.py --limit 100

# 실패한 단어만 재시도
python scripts/generate_prompts.py --retry-failed

# 특정 레벨만
python scripts/generate_prompts.py --level N5_4
```

---

## 5. ComfyUI Runner (`scripts/comfy_runner.py`)

### 5.1 Workflow JSON contract

`workflows/z_image_turbo.json`은 ComfyUI에서 `Save (API Format)`으로 export한 표준 JSON. 다음 노드 ID는 코드에서 placeholder를 주입할 위치:

| Node 역할 | 주입 필드 |
|---|---|
| Positive `CLIPTextEncode` | `inputs.text` ← prompt |
| Negative `CLIPTextEncode` | `inputs.text` ← 빈 문자열 또는 `"text, watermark, blurry, low quality"` |
| `KSampler` (또는 `KSamplerSelect`) | `inputs.seed` ← 결정적 시드 (아래 5.3) |
| `EmptyLatentImage` | `inputs.width`, `inputs.height` ← 768, 768 |
| `SaveImage` (또는 `SaveImageWebsocket`) | `inputs.filename_prefix` ← `global_id` |

노드 ID는 워크플로 변경 시 바뀌므로 코드에서 노드 ID로 직접 접근하지 말고 `class_type`으로 찾을 것:

```python
def find_node(workflow, class_type, title_contains=None):
    for nid, node in workflow.items():
        if node.get("class_type") == class_type:
            if title_contains is None or title_contains in (node.get("_meta", {}).get("title", "")):
                return nid
    raise KeyError(class_type)
```

### 5.2 Sampler 설정 (z_image_turbo 권장값)

- Steps: **8**
- CFG: **1.0**
- Sampler: `euler` 또는 `dpmpp_2m`
- Scheduler: `simple` 또는 `sgm_uniform`
- Width × Height: **768×768** (생성 비용·디스크 절감). 1024×1024 생성 후 다운스케일도 가능하나 768 native가 충분히 깨끗.

### 5.3 Seed 전략

**결정적 시드**: 동일 단어를 재생성해도 동일 이미지가 나와야 디버깅·재현이 쉽다.

```python
import hashlib
def seed_for(global_id: str) -> int:
    return int(hashlib.sha256(global_id.encode()).hexdigest()[:8], 16)
```

수동으로 특정 단어만 다시 뽑고 싶을 때는 `--reseed global_id1,global_id2,...` 옵션으로 시드를 +1씩 증분.

### 5.4 ComfyUI HTTP API 흐름

```
POST /prompt    {"prompt": workflow_json, "client_id": uuid} → {"prompt_id": ...}
WS /ws?clientId=uuid → 진행 상황 메시지, "executed" 메시지에서 파일명 추출
GET /history/{prompt_id} → 생성된 이미지 메타데이터
GET /view?filename=... → 이미지 바이트
```

또는 단순화: POST 후 polling으로 `/history/{prompt_id}`를 1초 간격 조회.

### 5.5 Concurrency

**동시성 1**부터 시작. RTX 4090 기준 z_image_turbo 1장 ~1-2초이므로 8,042장 = 약 3-5시간. 동시성을 늘리면 VRAM 스와핑으로 오히려 느려질 수 있음.

### 5.6 Resume logic

매 단어 처리 전 `images/{global_id}.webp`가 존재하고 파일 크기 > 5KB면 skip. `--force` 옵션으로 무시.

### 5.7 Output format

- 파일명: `images/{global_id}.webp` (CSV의 `image_filename` 컬럼과 정확히 일치해야 Anki에 그대로 사용 가능)
- 포맷: WebP, quality 85
- 파일 크기 목표: 30-80KB (8,042개 × 50KB ≈ 400MB)

### 5.8 Common commands

```bash
# 전체 생성
python scripts/comfy_runner.py

# 특정 레벨만
python scripts/comfy_runner.py --level N5_4

# 범위 지정
python scripts/comfy_runner.py --start 0 --count 100

# 특정 global_id 재생성 (시드 증분)
python scripts/comfy_runner.py --reseed N5_4_000004,N5_4_000023

# 강제 재생성
python scripts/comfy_runner.py --force --level N1
```

---

## 6. Quality Assurance

### 6.1 sample_review.py

배치 단위(예: 매 1,000개)마다 무작위 50개를 골라 HTML 갤러리 생성. 단어·읽기·의미·프롬프트·이미지를 한 화면에 보여줘 수동 검토.

```bash
python scripts/sample_review.py --range 0:1000 --count 50 --out samples/batch1.html
```

검수 체크리스트:
- [ ] 스타일이 batch 내에서 일관되는가
- [ ] 단어 의미가 한눈에 식별되는가 (적어도 50%)
- [ ] 텍스트(글자)가 끼어들지 않았는가
- [ ] 인체 손가락·얼굴이 심하게 깨지지 않았는가
- [ ] webp 파일 크기가 정상 범위 (5-200KB)

### 6.2 verify_outputs.py

```bash
python scripts/verify_outputs.py
```

다음을 검사:
1. `cards_with_prompts.csv`의 모든 행에 대해 `images/{global_id}.webp`가 존재하는가
2. 파일 크기가 5KB 이상인가 (0바이트 또는 깨진 파일 검출)
3. PIL로 열어서 768×768인가
4. 결손/이상 목록을 `logs/verify_report.json`에 기록 → `comfy_runner.py --retry-from logs/verify_report.json`으로 재실행

---

## 7. Failure Modes & Recovery

| 증상 | 원인 | 대응 |
|---|---|---|
| JSON parse error in generate_prompts | Sonnet이 markdown code fence를 두름 | 재시도(temp 낮춤), 두 번째도 실패면 failures.jsonl에 batch 단위 기록 |
| ComfyUI POST /prompt → 400 | workflow JSON에 빠진 필드 | workflow를 ComfyUI에서 다시 export, find_node로 동적 접근 유지 |
| ComfyUI 멈춤 (history는 비었는데 응답 없음) | 큐에 잠긴 prompt | 60초 타임아웃 → POST /interrupt → 다음 단어로 |
| webp 0바이트 | SaveImage가 권한 문제로 실패 | images/ 디렉토리 권한 확인, ComfyUI output 경로 설정 확인 |
| 손/얼굴 망가짐 | z_image_turbo의 약점 | reseed로 한두 번 더 시도, 그래도 안 되면 프롬프트에서 포즈 단순화 |
| 텍스트가 이미지에 끼어듦 | 프롬프트에 글자 묘사 단어 포함 | "no text"가 tail에 있어야 함, 본문에 "sign", "label", "letter" 등 단어 회피 |

---

## 8. Things NOT to do

- ❌ Claude Code 채팅 루프로 8천 개 단어를 직접 한 줄씩 생성하지 말 것 (반드시 스크립트 경유)
- ❌ 스타일 tail을 단어마다 다르게 쓰지 말 것 (일관성 깨짐, 이미 검증된 블록 사용)
- ❌ 한국어/일본어 프롬프트를 z_image_turbo에 넘기지 말 것 (영어가 가장 안정적)
- ❌ Negative prompt에 의존하지 말 것 (CFG=1에서 영향 작음, positive로 명시)
- ❌ 1024×1024로 생성하지 말 것 (디스크·시간 낭비, 768로 충분)
- ❌ 폴더에 단어를 직접 한국어/일본어 파일명으로 저장하지 말 것 (반드시 `global_id`.webp)
- ❌ progress.json 없이 작업 시작하지 말 것 (중단 시 처음부터 재시작해야 함)

---

## 9. Quick Start

```bash
# 0. ComfyUI를 별도 터미널에서 실행 (http://127.0.0.1:8188)
#    z_image_turbo_bf16.safetensors가 models/checkpoints/ 또는
#    models/unet/에 위치해야 함

# 1. 의존성
pip install anthropic pandas requests pillow tqdm websocket-client

# 2. API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. 프롬프트 생성 (1-2시간)
python scripts/generate_prompts.py

# 4. 50개 샘플로 프롬프트 품질 검수
python scripts/sample_review.py --range 0:8042 --count 50

# 5. 이미지 생성 (3-5시간, GPU 의존)
python scripts/comfy_runner.py

# 6. 결손/깨진 파일 검사
python scripts/verify_outputs.py

# 7. (필요시) 재시도
python scripts/comfy_runner.py --retry-from logs/verify_report.json
```
