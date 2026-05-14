# category_generalization_check.md

few-shot 예시에 없는 단어 중 카테고리별 5개 샘플을 추출해
Sonnet이 카테고리 룰을 일반화했는지 검증한다.

| category | global_id | word | reading | meaning | pos | has_MUST | follows_rule | verdict |
|----------|-----------|------|---------|---------|-----|----------|--------------|---------|
| 접속사 | N2_002182 | さて | さて | 그런데, 자 | 접속사 | Y | False | FAIL: no split/zigzag/two-panels pattern |
| 접속사 | N2_002166 | もしも | もしも | 만일, 혹시 | 접속사 | Y | True | OK |
| 접속사 | N2_002119 | なぜなら | なぜなら | 왜냐하면 | 접속사 | Y | True | OK |
| 접속사 | N2_002189 | それでも | それでも | 그럼에도, 그래도 | 접속사 | Y | True | OK |
| 접속사 | N5_4_001341 | すると | すると | 그러자; 그러면 | 접속사 | Y | True | OK |
| 표현 | N5_4_000524 | お願いします | おねがいします | 부탁합니다; 부탁드려요 | 표현 | Y | True | OK |
| 표현 | N5_4_001442 | 行ってらっしゃい | いってらっしゃい | 다녀오세요 | 표현 | Y | False | WARN: no contextual scene |
| 표현 | N5_4_000530 | こんにちは | こんにちは | 안녕하세요 | 표현 | Y | False | WARN: no contextual scene |
| 표현 | N5_4_000520 | ありがとうございます | ありがとうございます | 감사합니다 | 표현 | Y | True | OK |
| 표현 | N3_000090 | おい | おい | 어이; 이봐 | 표현 | N | False | WARN: no contextual scene |
| 추상명사 | N1_000442 | 国交 | こっこう | 국교; 나라 사이의 외교 관계 | 명사 | Y | True | OK |
| 추상명사 | N1_000893 | 出来 | でき | 1. 완성 상태; 결과 2. 성질; 자질 | 명사 | Y | True | OK |
| 추상명사 | N1_000350 | 結晶 | けっしょう | 1. 결정; 크리스털 2. 결정; 성과가 응축된 결과 | 명사 | N | False | FAIL: missing 'must clearly show' enumeration |
| 추상명사 | N1_001199 | 変遷 | へんせん | 변천; 세월에 따른 변화 | 명사 | Y | True | OK |
| 추상명사 | N1_000218 | 効き目 | ききめ | 효험; 효과 | 명사 | Y | True | OK |
| 부사 | N1_002274 | 歴然と | れきぜんと | 분명히; 뚜렷하게 | 부사 | Y | False | WARN: actor present but no manner indicator |
| 부사 | N1_002133 | かねがね | かねがね | 전부터; 오래전부터 | 부사 | Y | False | WARN: actor present but no manner indicator |
| 부사 | N5_4_000449 | すぐ | すぐ | 곧, 바로; 금방 | 부사 | Y | False | WARN: actor present but no manner indicator |
| 부사 | N3_001694 | 約 | やく | 약; 대략 | 부사 | Y | False | WARN: actor present but no manner indicator |
| 부사 | N5_4_001335 | やっと | やっと | 겨우; 간신히, 드디어 | 부사 | Y | False | WARN: actor present but no manner indicator |

## Outlier Summary

| category | global_id | verdict |
|----------|-----------|---------|
| 접속사 | N2_002182 | FAIL: no split/zigzag/two-panels pattern |
| 표현 | N5_4_001442 | WARN: no contextual scene |
| 표현 | N5_4_000530 | WARN: no contextual scene |
| 표현 | N3_000090 | WARN: no contextual scene |
| 추상명사 | N1_000350 | FAIL: missing 'must clearly show' enumeration |
| 부사 | N1_002274 | WARN: actor present but no manner indicator |
| 부사 | N1_002133 | WARN: actor present but no manner indicator |
| 부사 | N5_4_000449 | WARN: actor present but no manner indicator |
| 부사 | N3_001694 | WARN: actor present but no manner indicator |
| 부사 | N5_4_001335 | WARN: actor present but no manner indicator |

## 카테고리별 통과율

- 접속사: 4/5 (80%) → **GO**
- 표현: 2/5 (40%) → **REVIEW**
- 추상명사: 4/5 (80%) → **GO**
- 부사: 0/5 (0%) → **REVIEW**

**전체: 10/20 (50%)**