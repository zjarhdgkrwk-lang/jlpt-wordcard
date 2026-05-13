#!/usr/bin/env python3
"""
generate_prompts.py — JLPT 어휘 CSV를 받아 ComfyUI용 영문 이미지 프롬프트를 생성.

Usage:
    python scripts/generate_prompts.py
    python scripts/generate_prompts.py --limit 100
    python scripts/generate_prompts.py --level N5_4
    python scripts/generate_prompts.py --retry-failed
    python scripts/generate_prompts.py --restart
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from anthropic import Anthropic

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
INPUT_CSV = ROOT / "data" / "cards_normalized.csv"
OUTPUT_CSV = ROOT / "data" / "cards_with_prompts.csv"
PROGRESS_JSON = ROOT / "data" / "progress.json"
FAILURES_LOG = ROOT / "logs" / "failures.jsonl"
LOG_FILE = ROOT / "logs" / "generate_prompts.log"

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
BATCH_SIZE = 50
MAX_TOKENS = 8000
TEMPERATURE = 0.4
PROMPT_VERSION = "v1"

# -----------------------------------------------------------------------------
# Style guide (system prompt). CLAUDE.md 섹션 3을 그대로 옮겨와도 되지만,
# 토큰 절약을 위해 핵심만 압축. 변경 시 PROMPT_VERSION 올릴 것.
# -----------------------------------------------------------------------------

SYSTEM_PROMPT = """You write English image-generation prompts for an Anki Japanese-vocabulary deck. Images are made with z_image_turbo (8 steps, CFG 1.0, 768x768).

# Mandatory style tail (append verbatim at the end of EVERY prompt)
flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text

# Prompt skeleton
<subject + action/scene, 12-30 words>, <optional disambiguation cue>, <mandatory style tail>

Target total length: 40-70 words. Hard ceiling: 80 words.

# Composition rules
- Single focal subject. Background elements <= 2.
- Side or 3/4 view preferred. Frontal face only when subject is a person and pose isn't critical.
- No text in images. EXCEPTION: a single digit 1-9 is allowed when semantically required (e.g. 一日=1st, 二月=Feb).
- Flat solid colors, minimal shadows.

# Avoid (z_image_turbo weakness)
- Complex human poses: bowing, kneeling, handshakes touching, intricate multi-person interactions.
- Complex architectural perspective: airport interiors, station halls, classroom-wide shots. Reduce to a single iconic object.
- Mirrors, framed-within-frame, reflections.
- Signs, labels, billboards (would require text).

# Encouraged
- Small directional arrow for intransitive verbs and increase/decrease adverbs.
- Before/after diptych ("split composition: left ..., right ..., arrow between them") for change adverbs.
- Single prominent object + minimal context cue for adjectives (NOT just the property in empty space).
- Side profile + motion line for verbs.

# Part-of-speech rules
- Concrete noun: subject alone, plain.
- Abstract noun: one typical scene where the concept occurs ("the act of ...", "a moment of ..."). Simplify any architecture.
- Verb (transitive 타동사): subject + object + clear interaction, decisive moment with hand contact.
- Verb (intransitive 자동사): subject's own state change, motion arrow.
- I/Na-adjective (い형용사 / な형용사): a prominent context object that bears the property (e.g. 明るい requires a room with a window, not sunshine in empty space). For polysemy take the FIRST meaning.
- Adverb of manner (のんびり, ゆっくり): actor in an environment that conveys the manner.
- Adverb of degree/change (めっきり, ますます): before/after diptych with arrow.
- Adverb of time/frequency (まだ, よく): clock, calendar, repetition motif.
- Conjunction (でも, ところで): two small panels with a connector glyph.
- Expression (ありがとうございます, いただきます): depict the SITUATION, not the gesture. Avoid bowing.
- Adnominal (あんな, 大きな): a person pointing or a size-contrast pair.

# Polysemy
- If `front_hint` is non-empty, draw ONLY that sense.
- Else if `meaning_ko` has ';' or numbered senses '1. ... 2. ...', draw ONLY the first.
- Never draw two senses in one image.

# Output format
Return ONLY a JSON array. No prose, no markdown fences, no explanations.
Each element: {"global_id": "<as given>", "prompt": "<english prompt ending with the mandatory style tail>"}
The array length and order must match the input exactly.
"""

# -----------------------------------------------------------------------------
# Few-shot exemplars (검증된 케이스)
# -----------------------------------------------------------------------------

FEWSHOT_INPUT = [
    {"global_id": "EX_1", "word": "犬", "reading_hiragana": "いぬ", "meaning_ko": "개", "pos": "명사"},
    {"global_id": "EX_2", "word": "上がる", "reading_hiragana": "あがる", "meaning_ko": "올라가다; 오르다", "pos": "동사", "transitivity": "자동사"},
    {"global_id": "EX_3", "word": "明るい", "reading_hiragana": "あかるい", "meaning_ko": "밝다; 환하다, 명랑하다", "pos": "い형용사"},
    {"global_id": "EX_4", "word": "めっきり", "reading_hiragana": "めっきり", "meaning_ko": "눈에 띄게, 부쩍", "pos": "부사"},
    {"global_id": "EX_5", "word": "ありがとうございます", "reading_hiragana": "ありがとうございます", "meaning_ko": "감사합니다", "pos": "표현"},
    {"global_id": "EX_6", "word": "一日", "reading_hiragana": "ついたち", "meaning_ko": "1일; 매달 첫째 날", "pos": "명사", "front_hint": "매월 첫날"},
    {"global_id": "EX_7", "word": "一日", "reading_hiragana": "いちにち",
     "meaning_ko": "1일; 하루, 온종일", "pos": "명사"},
    {"global_id": "EX_8", "word": "間", "reading_hiragana": "あいだ",
     "meaning_ko": "사이; 동안", "pos": "명사"},
]

FEWSHOT_OUTPUT = [
    {"global_id": "EX_1",
     "prompt": "A cute friendly dog sitting and looking forward, single subject, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text"},
    {"global_id": "EX_2",
     "prompt": "A person walking up a flight of stairs viewed from the side, upward direction emphasized with a small arrow, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text"},
    {"global_id": "EX_3",
     "prompt": "A sunny living room with bright sunlight streaming through a large window, warm yellow light pool on the wooden floor, simple chair beside the window, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text"},
    {"global_id": "EX_4",
     "prompt": "A split composition: left side shows a green leafy tree in summer, right side shows the same tree bare with snow in winter, a small arrow between them indicating noticeable change, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text"},
    {"global_id": "EX_5",
     "prompt": "A customer receiving a small gift-wrapped package from a shop clerk across a counter, both smiling warmly, simple shop interior, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text"},
    {"global_id": "EX_6",
     "prompt": "A wall calendar page with the date \"1\" clearly marked and circled at the top-left corner of the month grid, indicating the first day of the month, flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text"},
    {"global_id": "EX_7",
     "prompt": "A horizontal strip showing the progression of one full day from left to right in four small connected scenes: morning sunrise with a person waking up, midday with high sun and a person at work, evening sunset with warm orange sky, night with moon and stars and a person sleeping; a subtle curved arrow above connects all four scenes to convey continuous duration. The image must clearly show four distinct time-of-day stages, not one or two. flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text"},
    {"global_id": "EX_8",
     "prompt": "A child standing centered in the empty space between two distinctly different flanking objects (a tall tree on the left and a small house on the right) of similar height; the ground area between the objects is softly shaded in a contrasting pastel tone so the empty space itself reads as the visual subject; short horizontal double-headed arrows on the ground extend outward from the child to each flanking object. The image must clearly show: (a) two visibly different flanking objects, (b) a child positioned exactly in the middle of the gap, (c) the central ground area visually highlighted by shading, (d) bilateral double-headed arrows from center pointing outward. flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text"},
]

# -----------------------------------------------------------------------------
# Data prep
# -----------------------------------------------------------------------------

INPUT_COLS_FOR_LLM = ["global_id", "word", "front_hint", "reading_hiragana",
                       "meaning_ko", "pos", "verb_note", "transitivity"]


def row_to_request(row: dict[str, Any]) -> dict[str, Any]:
    """LLM에 보낼 dict로 정리. NaN/빈 값은 제거."""
    out = {}
    for k in INPUT_COLS_FOR_LLM:
        v = row.get(k)
        if v is not None and not (isinstance(v, float) and pd.isna(v)) and str(v).strip() != "":
            out[k] = str(v).strip()
    return out


# -----------------------------------------------------------------------------
# API call
# -----------------------------------------------------------------------------

def call_claude(client: Anthropic, batch: list[dict[str, Any]], retry: int = 0) -> list[dict[str, str]]:
    """배치를 받아 [{global_id, prompt}, ...] 반환. JSON 파싱 실패 시 1회 재시도."""
    user_payload = json.dumps(batch, ensure_ascii=False, indent=2)
    fewshot_in = json.dumps(FEWSHOT_INPUT, ensure_ascii=False, indent=2)
    fewshot_out = json.dumps(FEWSHOT_OUTPUT, ensure_ascii=False, indent=2)

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE if retry == 0 else 0.2,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {"role": "user", "content": f"Here are example inputs:\n{fewshot_in}"},
            {"role": "assistant", "content": fewshot_out},
            {"role": "user", "content": f"Now generate prompts for these {len(batch)} entries. Return ONLY the JSON array:\n{user_payload}"},
        ],
    )

    text = response.content[0].text.strip()
    # markdown code fence 방어
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        if retry == 0:
            logging.warning("JSON parse failed, retrying with lower temperature: %s", e)
            return call_claude(client, batch, retry=1)
        raise

    if not isinstance(parsed, list) or len(parsed) != len(batch):
        raise ValueError(f"Expected list of {len(batch)}, got {type(parsed).__name__} of len {len(parsed) if hasattr(parsed, '__len__') else '?'}")

    # global_id 매칭 검증
    in_ids = [r["global_id"] for r in batch]
    out_ids = [r.get("global_id") for r in parsed]
    if in_ids != out_ids:
        raise ValueError(f"global_id mismatch. Expected {in_ids[:3]}..., got {out_ids[:3]}...")

    return parsed


# -----------------------------------------------------------------------------
# State management
# -----------------------------------------------------------------------------

@dataclass
class Progress:
    completed_ids: set[str]
    failed_ids: set[str]

    @classmethod
    def load(cls) -> "Progress":
        if not PROGRESS_JSON.exists():
            return cls(completed_ids=set(), failed_ids=set())
        d = json.loads(PROGRESS_JSON.read_text(encoding="utf-8"))
        return cls(
            completed_ids=set(d.get("completed_ids", [])),
            failed_ids=set(d.get("failed_ids", [])),
        )

    def save(self) -> None:
        PROGRESS_JSON.parent.mkdir(parents=True, exist_ok=True)
        PROGRESS_JSON.write_text(json.dumps({
            "completed_ids": sorted(self.completed_ids),
            "failed_ids": sorted(self.failed_ids),
        }, ensure_ascii=False, indent=2), encoding="utf-8")


def log_failure(batch: list[dict], error: str) -> None:
    FAILURES_LOG.parent.mkdir(parents=True, exist_ok=True)
    with FAILURES_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "global_ids": [r["global_id"] for r in batch],
            "error": error,
        }, ensure_ascii=False) + "\n")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="최대 N개만 처리 (테스트용)")
    parser.add_argument("--level", type=str, default=None, help="특정 level만 (N5_4/N3/N2/N1)")
    parser.add_argument("--retry-failed", action="store_true", help="실패 목록만 재시도")
    parser.add_argument("--restart", action="store_true", help="progress 무시하고 처음부터")
    args = parser.parse_args()

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler()],
    )

    client = Anthropic()
    df = pd.read_csv(INPUT_CSV, encoding="utf-8-sig", dtype=str).fillna("")
    logging.info("Loaded %d rows from %s", len(df), INPUT_CSV)

    progress = Progress(completed_ids=set(), failed_ids=set()) if args.restart else Progress.load()

    # 출력 CSV 로드/초기화
    if OUTPUT_CSV.exists() and not args.restart:
        out_df = pd.read_csv(OUTPUT_CSV, encoding="utf-8-sig", dtype=str).fillna("")
    else:
        out_df = df.copy()
        out_df["prompt"] = ""
        out_df["prompt_version"] = ""

    # 처리할 rows 선정
    work = out_df.copy()
    if args.level:
        work = work[work["level"] == args.level]
    if args.retry_failed:
        work = work[work["global_id"].isin(progress.failed_ids)]
    else:
        work = work[~work["global_id"].isin(progress.completed_ids)]
        work = work[work["prompt"].astype(str).str.strip() == ""]
    if args.limit:
        work = work.head(args.limit)

    logging.info("To process: %d rows", len(work))
    if len(work) == 0:
        return 0

    # 배치 처리
    work_records = work.to_dict(orient="records")
    total_batches = (len(work_records) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_idx in range(total_batches):
        start = batch_idx * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(work_records))
        raw_batch = work_records[start:end]
        api_batch = [row_to_request(r) for r in raw_batch]

        logging.info("Batch %d/%d (rows %d-%d)", batch_idx + 1, total_batches, start, end - 1)

        try:
            results = call_claude(client, api_batch)
        except Exception as e:
            logging.error("Batch failed: %s", e)
            log_failure(api_batch, str(e))
            progress.failed_ids.update(r["global_id"] for r in api_batch)
            progress.save()
            continue

        # 결과를 out_df에 반영
        prompt_map = {r["global_id"]: r["prompt"] for r in results}
        for gid, prompt in prompt_map.items():
            mask = out_df["global_id"] == gid
            out_df.loc[mask, "prompt"] = prompt
            out_df.loc[mask, "prompt_version"] = PROMPT_VERSION
            progress.completed_ids.add(gid)
            progress.failed_ids.discard(gid)

        # 매 배치마다 저장 (안전성)
        OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
        progress.save()

    logging.info("Done. Completed: %d, Failed: %d",
                 len(progress.completed_ids), len(progress.failed_ids))
    return 0 if not progress.failed_ids else 1


if __name__ == "__main__":
    sys.exit(main())
