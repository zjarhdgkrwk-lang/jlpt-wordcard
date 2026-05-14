# verification_full.md

## Coverage
- 전체 행: 8,042
- prompt 채워진 행: 8,042 (100.0%)
- 빈 행: 0

## Format
- 스타일 tail 포함 ('no text' 끝): 8,042 / 8,042 (100.0%)
- 영어만 (non-ASCII 없음): 8,018 / 8,042 (99.7%)
- 단어 수 분포: min=28, median=45, max=134, mean=52.8
- 100단어 초과: 16개

## POS Distribution

| 품사 | 행 수 | 평균 단어 수 |
|------|-------|------------|
| い형용사 | 276 | 44.5 |
| な형용사 | 541 | 44.1 |
| 동사 | 1419 | 45.5 |
| 명사 | 5133 | 52.7 |
| 부사 | 528 | 79.5 |
| 연체사 | 27 | 74.2 |
| 접속사 | 40 | 86.0 |
| 표현 | 77 | 78.9 |

## Validator Stats
- failures.jsonl 항목 수: 182
  - `missing MUST directive after 2 retries`: 159건
  - `unknown`: 23건
- 'MUST still absent' 경고 (오탐으로 추정): 159건

## API Stats
- HTTP 200 응답 수 (API 호출): 254
- 예상 비용 (rough): ~$12.7
- 완료 ID 수 (progress.json): 8042
- 실패 ID 수 (progress.json): 0