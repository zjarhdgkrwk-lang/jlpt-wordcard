# verification_full.md

## Coverage
- 전체 행: 8,042
- prompt 채워진 행: 6,894 (85.7%)
- 빈 행: 1,148

## Format
- 스타일 tail 포함 ('no text' 끝): 6,894 / 6,894 (100.0%)
- 영어만 (non-ASCII 없음): 6,872 / 6,894 (99.7%)
- 단어 수 분포: min=28, median=45, max=134, mean=52.7
- 100단어 초과: 11개

## POS Distribution

| 품사 | 행 수 | 평균 단어 수 |
|------|-------|------------|
| い형용사 | 206 | 44.7 |
| な형용사 | 308 | 43.2 |
| 동사 | 995 | 45.1 |
| 명사 | 4925 | 52.7 |
| 부사 | 326 | 79.2 |
| 연체사 | 24 | 74.1 |
| 접속사 | 34 | 86.0 |
| 표현 | 75 | 78.6 |

## Validator Stats
- failures.jsonl 항목 수: 172
  - `missing MUST directive after 2 retries`: 149건
  - `unknown`: 23건
- 'MUST still absent' 경고 (오탐으로 추정): 149건

## API Stats
- HTTP 200 응답 수 (API 호출): 225
- 예상 비용 (rough): ~$11.2
- 완료 ID 수 (progress.json): 6894
- 실패 ID 수 (progress.json): 1148