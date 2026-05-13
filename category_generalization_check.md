# category_generalization_check.md

few-shot 예시에 없는 단어 중 카테고리별 5개 샘플을 추출해
Sonnet이 카테고리 룰을 일반화했는지 검증한다.

| category | global_id | word | reading | meaning | pos | has_MUST | follows_rule | verdict |
|----------|-----------|------|---------|---------|-----|----------|--------------|---------|
| 접속사 | N2_002119 | なぜなら | なぜなら | 왜냐하면 | 접속사 | Y | True | OK |
| 접속사 | N2_002182 | さて | さて | 그런데, 자 | 접속사 | Y | False | FAIL: no split/zigzag/two-panels pattern |
| 접속사 | N2_002190 | それどころか | それどころか | 그것은커녕, 오히려 | 접속사 | Y | True | OK |
| 접속사 | N2_002189 | それでも | それでも | 그럼에도, 그래도 | 접속사 | Y | True | OK |
| 접속사 | N5_4_001345 | それでは | それでは | 그럼; 그러면 | 접속사 | Y | True | OK |
| 표현 | N5_4_000524 | お願いします | おねがいします | 부탁합니다; 부탁드려요 | 표현 | Y | True | OK |
| 표현 | N2_001839 | やむを得ない | やむをえない | 어쩔 수 없다, 불가피하다 | 표현 | Y | False | WARN: no contextual scene |
| 표현 | N5_4_000530 | こんにちは | こんにちは | 안녕하세요 | 표현 | Y | False | WARN: no contextual scene |
| 표현 | N5_4_000520 | ありがとうございます | ありがとうございます | 감사합니다 | 표현 | Y | True | OK |
| 표현 | N5_4_001442 | 行ってらっしゃい | いってらっしゃい | 다녀오세요 | 표현 | Y | False | WARN: no contextual scene |
| 추상명사 | N1_000442 | 国交 | こっこう | 국교; 나라 사이의 외교 관계 | 명사 | Y | True | OK |
| 추상명사 | N1_000893 | 出来 | でき | 1. 완성 상태; 결과 2. 성질; 자질 | 명사 | Y | True | OK |
| 추상명사 | N1_000350 | 結晶 | けっしょう | 1. 결정; 크리스털 2. 결정; 성과가 응축된 결과 | 명사 | N | False | FAIL: missing 'must clearly show' enumeration |
| 추상명사 | N1_001199 | 変遷 | へんせん | 변천; 세월에 따른 변화 | 명사 | Y | True | OK |
| 추상명사 | N1_000218 | 効き目 | ききめ | 효험; 효과 | 명사 | Y | True | OK |
| 부사 | N2_002014 | 依然 | いぜん | 여전히, 변함없이 | 부사 | Y | False | WARN: actor present but no manner indicator |
| 부사 | N3_001675 | なるべく | なるべく | 가급적; 되도록 | 부사 | Y | False | WARN: actor present but no manner indicator |
| 부사 | N2_002040 | ぎりぎり | ぎりぎり | 아슬아슬하게, 가까스로 | 부사 | Y | False | WARN: actor present but no manner indicator |
| 부사 | N5_4_000452 | 大変 | たいへん | 1. 매우, 몹시 2. 힘들게; 큰일로 | 부사 | Y | False | WARN: actor present but no manner indicator |
| 부사 | N3_001647 | 少なくとも | すくなくとも | 적어도; 최소한 | 부사 | Y | False | WARN: actor present but no manner indicator |

## Outlier Summary

| category | global_id | verdict |
|----------|-----------|---------|
| 접속사 | N2_002182 | FAIL: no split/zigzag/two-panels pattern |
| 표현 | N2_001839 | WARN: no contextual scene |
| 표현 | N5_4_000530 | WARN: no contextual scene |
| 표현 | N5_4_001442 | WARN: no contextual scene |
| 추상명사 | N1_000350 | FAIL: missing 'must clearly show' enumeration |
| 부사 | N2_002014 | WARN: actor present but no manner indicator |
| 부사 | N3_001675 | WARN: actor present but no manner indicator |
| 부사 | N2_002040 | WARN: actor present but no manner indicator |
| 부사 | N5_4_000452 | WARN: actor present but no manner indicator |
| 부사 | N3_001647 | WARN: actor present but no manner indicator |

## 카테고리별 통과율

- 접속사: 4/5 (80%) → **GO**
- 표현: 2/5 (40%) → **REVIEW**
- 추상명사: 4/5 (80%) → **GO**
- 부사: 0/5 (0%) → **REVIEW**

**전체: 10/20 (50%)**