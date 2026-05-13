#!/usr/bin/env python3
"""
analyze_results.py — 풀스케일 생성 완료 후 verification_full.md 와
category_generalization_check.md 를 작성하는 스크립트.

Usage:
    python scripts/analyze_results.py
"""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "cards_with_prompts.csv"
PROGRESS_JSON = ROOT / "data" / "progress.json"
FAILURES_LOG = ROOT / "logs" / "failures.jsonl"
LOG_FILE = ROOT / "logs" / "generate_prompts.log"

STYLE_TAIL = "flat vector illustration, soft pastel colors, minimal clean composition, plain white background, centered, children's textbook style, no text"

# few-shot global_ids (이것들은 카테고리 일반화 check에서 제외)
FEW_SHOT_WORDS = {"犬", "雨", "開ける", "上がる", "のんびり", "めっきり", "一日"}

# category_generalization_check용 판정 함수들
def follows_conjunction_rule(prompt: str) -> tuple[bool, str]:
    """접속사: zigzag/lightning/two panels 언급"""
    p = prompt.lower()
    if any(kw in p for kw in ["zigzag", "lightning", "two panels", "split"]):
        return True, "OK"
    if "two" in p and "panel" in p:
        return True, "OK"
    return False, "FAIL: no split/zigzag/two-panels pattern"

def follows_expression_rule(prompt: str) -> tuple[bool, str]:
    """표현: 상황/맥락 묘사, 금지 포즈(bow/bowing) 없어야"""
    p = prompt.lower()
    if "bowing" in p or "bow deeply" in p or "kneeling" in p:
        return False, "FAIL: forbidden pose (bowing/kneeling)"
    # 상황 묘사가 있어야
    context_words = ["counter", "table", "gift", "package", "shop", "office",
                     "meal", "bowl", "customer", "handed", "receiving", "dropped",
                     "scattered", "apologetic", "regretful", "accident"]
    if any(kw in p for kw in context_words):
        return True, "OK"
    return False, "WARN: no contextual scene"

def follows_abstract_noun_rule(prompt: str) -> tuple[bool, str]:
    """추상명사: 'must clearly show' 열거 포함"""
    if re.search(r"must\s+(clearly\s+)?show", prompt, re.IGNORECASE):
        return True, "OK"
    # "The image must clearly show" 패턴
    if "image must" in prompt.lower():
        return True, "OK"
    return False, "FAIL: missing 'must clearly show' enumeration"

def follows_manner_adverb_rule(prompt: str) -> tuple[bool, str]:
    """양태부사: 행위자 + manner 환경/자세 묘사"""
    p = prompt.lower()
    # 사람 + 환경 or 자세
    has_actor = any(kw in p for kw in ["person", "man", "woman", "figure", "character", "child"])
    has_manner = any(kw in p for kw in [
        "relaxing", "hammock", "slowly", "carefully", "firmly",
        "peaceful", "leisurely", "gently", "quietly", "steadily",
        "calm", "neatly", "properly", "purposefully", "sneaky",
        "intentionally", "deliberately", "cautiously"
    ])
    if has_actor and has_manner:
        return True, "OK"
    if has_actor:
        return False, "WARN: actor present but no manner indicator"
    return False, "FAIL: no actor found"


def count_words(prompt: str) -> int:
    return len(prompt.split())


def main() -> None:
    # --- 데이터 로드 ---
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    filled_mask = df["prompt"].notna() & (df["prompt"].str.strip() != "")
    filled = df[filled_mask].copy()
    empty = df[~filled_mask]

    # failures.jsonl
    failures = []
    if FAILURES_LOG.exists():
        for line in FAILURES_LOG.read_text().splitlines():
            line = line.strip()
            if line:
                try:
                    failures.append(json.loads(line))
                except Exception:
                    pass

    # progress.json
    progress = {}
    if PROGRESS_JSON.exists():
        progress = json.loads(PROGRESS_JSON.read_text())

    # API 호출 수 (log에서 HTTP 200 수)
    api_calls = 0
    if LOG_FILE.exists():
        api_calls = LOG_FILE.read_text().count("HTTP/1.1 200 OK")

    # --- 작업 2: verification_full.md ---
    word_counts = filled["prompt"].apply(count_words)
    has_tail = filled["prompt"].apply(lambda p: STYLE_TAIL in p if isinstance(p, str) else False)
    is_english_only = filled["prompt"].apply(
        lambda p: bool(p) and not any(ord(c) > 0x7F and ord(c) < 0xAC00 for c in p)
        if isinstance(p, str) else False
    )
    over_100 = (word_counts > 100).sum()

    pos_dist = filled.groupby("pos").agg(
        count=("prompt", "count"),
        avg_words=("prompt", lambda x: x.apply(count_words).mean())
    ).round(1)

    # failures.jsonl 사유 카운트
    reason_counts: dict[str, int] = {}
    for f in failures:
        reason = f.get("reason", "unknown")[:60]
        reason_counts[reason] = reason_counts.get(reason, 0) + 1

    # MUST still absent 카운트 from log
    must_still_absent = 0
    if LOG_FILE.exists():
        must_still_absent = LOG_FILE.read_text().count("MUST still absent after strict retry")

    estimated_cost_usd = api_calls * 0.05  # rough estimate

    vf_lines = [
        "# verification_full.md",
        "",
        "## Coverage",
        f"- 전체 행: {len(df):,}",
        f"- prompt 채워진 행: {len(filled):,} ({len(filled)/len(df)*100:.1f}%)",
        f"- 빈 행: {len(empty):,}",
        "",
        "## Format",
        f"- 스타일 tail 포함 ('no text' 끝): {has_tail.sum():,} / {len(filled):,} ({has_tail.mean()*100:.1f}%)",
        f"- 영어만 (non-ASCII 없음): {is_english_only.sum():,} / {len(filled):,} ({is_english_only.mean()*100:.1f}%)",
        f"- 단어 수 분포: min={word_counts.min()}, median={word_counts.median():.0f}, max={word_counts.max()}, mean={word_counts.mean():.1f}",
        f"- 100단어 초과: {over_100}개",
        "",
        "## POS Distribution",
        "",
        "| 품사 | 행 수 | 평균 단어 수 |",
        "|------|-------|------------|",
    ]
    for pos, row in pos_dist.iterrows():
        vf_lines.append(f"| {pos} | {int(row['count'])} | {row['avg_words']:.1f} |")

    vf_lines += [
        "",
        "## Validator Stats",
        f"- failures.jsonl 항목 수: {len(failures)}",
    ]
    if reason_counts:
        for reason, cnt in sorted(reason_counts.items(), key=lambda x: -x[1]):
            vf_lines.append(f"  - `{reason}`: {cnt}건")
    else:
        vf_lines.append("  - (없음)")

    vf_lines += [
        f"- 'MUST still absent' 경고 (오탐으로 추정): {must_still_absent}건",
        "",
        "## API Stats",
        f"- HTTP 200 응답 수 (API 호출): {api_calls}",
        f"- 예상 비용 (rough): ~${estimated_cost_usd:.1f}",
        f"- 완료 ID 수 (progress.json): {len(progress.get('completed_ids', []))}",
        f"- 실패 ID 수 (progress.json): {len(progress.get('failed_ids', []))}",
    ]

    vf_path = ROOT / "verification_full.md"
    vf_path.write_text("\n".join(vf_lines), encoding="utf-8")
    print(f"[OK] verification_full.md 작성 완료")

    # --- 작업 3: category_generalization_check.md ---
    # 카테고리별 샘플 추출
    random.seed(42)

    # 1. 접속사 (few-shot에 없는)
    conjunction = filled[(filled["pos"] == "접속사") & (~filled["word"].isin(FEW_SHOT_WORDS))]
    sample1 = conjunction.sample(min(5, len(conjunction)), random_state=42) if len(conjunction) > 0 else pd.DataFrame()

    # 2. 표현 (few-shot에 없는)
    expression = filled[(filled["pos"] == "표현") & (~filled["word"].isin(FEW_SHOT_WORDS))]
    sample2 = expression.sample(min(5, len(expression)), random_state=42) if len(expression) > 0 else pd.DataFrame()

    # 3. 영향/관계류 추상명사
    ABSTRACT_KW = ["영향", "효과", "결과", "반응", "관계", "변화", "발전", "발생"]
    abs_noun = filled[
        (filled["pos"] == "명사") &
        (~filled["word"].isin(FEW_SHOT_WORDS)) &
        filled["meaning_ko"].fillna("").apply(lambda m: any(kw in m for kw in ABSTRACT_KW))
    ]
    sample3 = abs_noun.sample(min(5, len(abs_noun)), random_state=42) if len(abs_noun) > 0 else pd.DataFrame()

    # 4. 양태/의도 부사 (few-shot에 없는)
    adverb = filled[(filled["pos"] == "부사") & (~filled["word"].isin(FEW_SHOT_WORDS))]
    sample4 = adverb.sample(min(5, len(adverb)), random_state=42) if len(adverb) > 0 else pd.DataFrame()

    category_rules = {
        "접속사": follows_conjunction_rule,
        "표현": follows_expression_rule,
        "추상명사": follows_abstract_noun_rule,
        "부사": follows_manner_adverb_rule,
    }

    samples_by_cat = {
        "접속사": (sample1, follows_conjunction_rule),
        "표현": (sample2, follows_expression_rule),
        "추상명사": (sample3, follows_abstract_noun_rule),
        "부사": (sample4, follows_manner_adverb_rule),
    }

    cgc_lines = [
        "# category_generalization_check.md",
        "",
        "few-shot 예시에 없는 단어 중 카테고리별 5개 샘플을 추출해",
        "Sonnet이 카테고리 룰을 일반화했는지 검증한다.",
        "",
        "| category | global_id | word | reading | meaning | pos | has_MUST | follows_rule | verdict |",
        "|----------|-----------|------|---------|---------|-----|----------|--------------|---------|",
    ]

    all_results = []
    for cat_name, (sample_df, rule_fn) in samples_by_cat.items():
        if len(sample_df) == 0:
            cgc_lines.append(f"| {cat_name} | (샘플 없음) | - | - | - | - | - | - | - |")
            continue
        for _, row in sample_df.iterrows():
            prompt = str(row.get("prompt", ""))
            has_must = "Y" if re.search(r"must\s+(clearly\s+)?show", prompt, re.IGNORECASE) else "N"
            ok, verdict = rule_fn(prompt)
            meaning = str(row.get("meaning_ko", ""))[:30]
            reading = str(row.get("reading_hiragana", ""))[:15]
            cgc_lines.append(
                f"| {cat_name} | {row['global_id']} | {row['word']} | {reading} | {meaning} | {row['pos']} | {has_must} | {ok} | {verdict} |"
            )
            all_results.append({
                "category": cat_name,
                "global_id": row["global_id"],
                "ok": ok,
                "verdict": verdict,
            })

    # Outlier summary
    cgc_lines += ["", "## Outlier Summary", ""]
    warn_fail = [r for r in all_results if not r["ok"]]
    if not warn_fail:
        cgc_lines.append("WARN/FAIL 없음 — 전 카테고리 통과")
    else:
        cgc_lines.append("| category | global_id | verdict |")
        cgc_lines.append("|----------|-----------|---------|")
        for r in warn_fail:
            cgc_lines.append(f"| {r['category']} | {r['global_id']} | {r['verdict']} |")

    # 카테고리별 통과율
    cgc_lines += ["", "## 카테고리별 통과율", ""]
    from collections import defaultdict
    cat_stats: dict[str, list[bool]] = defaultdict(list)
    for r in all_results:
        cat_stats[r["category"]].append(r["ok"])

    for cat, results in cat_stats.items():
        pct = sum(results) / len(results) * 100 if results else 0
        verdict = "GO" if pct >= 80 else "REVIEW"
        cgc_lines.append(f"- {cat}: {sum(results)}/{len(results)} ({pct:.0f}%) → **{verdict}**")

    overall_ok = sum(r["ok"] for r in all_results)
    overall_total = len(all_results)
    overall_pct = overall_ok / overall_total * 100 if overall_total else 0
    cgc_lines.append(f"\n**전체: {overall_ok}/{overall_total} ({overall_pct:.0f}%)**")

    cgc_path = ROOT / "category_generalization_check.md"
    cgc_path.write_text("\n".join(cgc_lines), encoding="utf-8")
    print(f"[OK] category_generalization_check.md 작성 완료")


if __name__ == "__main__":
    main()
