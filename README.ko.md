[English](README.md) · [中文](README.zh-CN.md) · **한국어** · [Tiếng Việt](README.vi.md) · [日本語](README.ja.md) · [Français](README.fr.md) · [Español](README.es.md)

# 거래소 수수료 데이터셋

주요 암호화폐 거래소 7곳의 수수료를 구조화한 오픈 데이터셋입니다. 현물과 무기한 선물, 메이커와 테이커. 현재 VIP0을 수록하고 있으며 상위 등급은 순차적으로 추가 중입니다. 매주 수요일에 수동으로 재검증하며, 매주의 스냅샷을 `data/history/`에 그대로 보관합니다.

JSON과 CSV로 제공합니다. MIT 라이선스. API 키도, 호출 제한도, 가입도 없습니다 — 그냥 git 저장소 안의 파일입니다.

---

## 왜 만들었나

모든 거래소가 수수료표를 공개하지만, 공개하는 방식은 제각각입니다. 표로 정리한 곳도 있고, 고객센터 문서 안에 묻어둔 곳도 있고, 로그인해야 실제 등급이 보이는 곳도 있습니다. 등급 이름은 바뀌고, 이벤트 요율은 공지 없이 종료되며, 지난 숫자를 남겨두는 곳은 어디에도 없습니다.

그래서 **"바이비트 선물 테이커 수수료가 3월에는 얼마였나?"** 같은 기본적인 질문조차 지금은 확인할 방법이 없습니다.

그래서 매주 한 번, 모든 거래소를 하나의 스키마로 스냅샷해 둡니다.

---

## 현재 스냅샷

가장 최근 검증 기준, VIP0 등급:

| 거래소 | 현물 | 선물 메이커 | 선물 테이커 |
|---|---|---|---|
| Binance | 0.100% | 0.020% | 0.050% |
| Bitget | 0.100% | 0.020% | 0.060% |
| Gate.io | 0.100% | 0.020% | 0.050% |
| Bybit | 0.100% | 0.020% | 0.055% |
| OKX | 0.090% | 0.020% | 0.050% |
| Backpack | 0.090% | 0.020% | 0.050% |
| Polymarket | 0.75%–1.8% | — | — |

기준이 되는 원본은 `data/fees.json`입니다. 위 표는 거기서 생성되며 몇 시간 정도 늦을 수 있습니다.

---

## 빠른 시작

```bash
# 최신 스냅샷 전체
curl -s https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.json

# VIP0 선물 테이커 수수료만 오름차순으로
curl -s https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.json \
  | jq -r '.exchanges[] | [.id, .futures.vip0.taker] | @tsv' | sort -k2 -n
```

```python
import pandas as pd

URL = "https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.csv"
df = pd.read_csv(URL)

# VIP0 무기한 선물 테이커가 가장 싼 거래소
(df[(df.market == "futures") & (df.tier == "vip0")]
   .sort_values("taker")[["exchange_id", "maker", "taker"]])
```

```javascript
const res = await fetch(
  "https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.json"
);
const { exchanges } = await res.json();
```

---

## 구성

```
data/
├── fees.json              # 현재 스냅샷, 기준 원본
├── fees.csv               # 동일 데이터, 평탄화
└── history/
    ├── 2026-08-05.json
    ├── 2026-07-29.json
    └── ...
schema/
└── fees.schema.json       # JSON Schema (draft 2020-12)
scripts/
└── validate.py            # PR 전에 실행
```

### 스키마

```json
{
  "snapshot_date": "2026-08-05",
  "exchanges": [
    {
      "id": "binance",
      "name": "Binance",
      "source_url": "https://www.binance.com/ko/fee/schedule",
      "verified_at": "2026-08-05",
      "spot":    { "vip0": { "maker": 0.0010, "taker": 0.0010 } },
      "futures": { "vip0": { "maker": 0.0002, "taker": 0.0005 } },
      "notes": "BNB 보유 시 현물 수수료 25% 할인 적용."
    }
  ]
}
```

모든 요율은 퍼센트도 bps도 아닌 **소수**입니다. `0.0005`는 0.05%를 뜻합니다. 수수료 데이터를 다룰 때 가장 흔한 실수 지점이라 스키마에서 강제합니다.

CSV 컬럼: `snapshot_date, exchange_id, market, tier, maker, taker`.

---

## 검증 방식

매주 수요일, 각 거래소의 공개 수수료 페이지를 직접 열어 확인한 뒤 제휴 대시보드의 수치와 대조합니다. 대시보드 쪽이 공개 페이지보다 먼저 갱신되는 경우가 잦기 때문입니다. 두 값이 어긋나면 한쪽을 임의로 채택하지 않고 `notes`에 기록합니다.

전체 대조 절차 — 무엇을 하나의 등급으로 볼지, 이벤트 요율은 어떻게 처리할지, 주중에 요율이 바뀌면 어떻게 할지 — 는 [RAILSDESK 평가 기준](https://railsdesk.com/ko/#method)에 정리되어 있습니다.

크롤링은 하지 않습니다. 대부분의 거래소가 등급 정보를 클라이언트 사이드에서 렌더링하고 계정 상태에 따라 다르게 노출하기 때문에, 수수료 페이지 크롤링은 맞는 데이터보다 틀린 데이터를 더 자주 만들어 냅니다.

---

## 표시 수수료와 실효 수수료

이 데이터셋으로 거래소를 비교하려는 경우 먼저 짚어둘 점이 있습니다. **여기 있는 숫자는 표시 수수료**, 즉 어떤 할인도 적용되기 전의 정가입니다.

실제 부담액은 보통 세 가지 요인으로 달라집니다.

1. **거래량 등급** — 현재 VIP0까지 수록되어 있고, VIP1 이상은 추가 작업 중입니다.
2. **자체 토큰 할인** — 예를 들어 BNB를 보유하면 바이낸스 현물 수수료가 25% 깎입니다. 요율 필드가 아니라 `notes`에 기록합니다.
3. **레퍼럴 페이백** — 추천 관계를 통해 낸 수수료의 일부를 되돌려받는 구조입니다. 이 데이터셋에는 전혀 포함되지 않습니다. 거래소의 수수료표가 아니라 계정을 어느 링크로 개설했는지에 달린 값이기 때문입니다.

셋 중에서 금액이 가장 큰 것이 보통 세 번째이고, 공개 문서가 가장 부실한 것도 세 번째입니다. 거래소별 현행 페이백 비율은 [거래소 레퍼럴 순위](https://railsdesk.com/ko/)에서 별도로 관리하며, 정산 조건을 항목별로 비교한 내용은 [심층 분석](https://railsdesk.com/ko/articles/)에 있습니다.

비용 모델을 만든다면 이 셋을 각각 독립된 곱셈 항으로 두는 편이 좋습니다. 하나의 `fee` 필드로 뭉뚱그리는 것이 백테스트 결과가 실제보다 좋게 나오는 흔한 원인입니다.

---

## 기여

정정 제보를 환영합니다. 이 저장소를 공개해 둔 주된 이유이기도 합니다.

1. 포크 후 `data/fees.json` 수정
2. `python scripts/validate.py` 실행 — 스키마 검증과 비정상 요율 탐지를 수행합니다
3. 근거가 되는 거래소 수수료 페이지 링크를 첨부해 PR 생성

거래소 추가 요청은 수수료 페이지 URL과 함께 이슈로 남겨 주세요. 기준은 공개된 기계 판독 가능한 수수료 문서가 있고 유의미한 거래량이 있는 거래소입니다.

---

## 라이선스

코드는 MIT. 데이터는 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — 상업적 이용, 재배포, 제품화 모두 가능하며 출처 표기만 유지하면 됩니다.

---

## 고지

이것은 수수료 데이터이며 투자 조언이 아닙니다. 암호화폐 파생상품 거래는 원금 전액 손실로 이어질 수 있습니다. 요율은 변경되며 이 저장소의 스냅샷은 최대 7일까지 오래된 값일 수 있으니, 실제 판단에 쓰기 전에 거래소에서 직접 확인하시기 바랍니다.

[RAILSDESK](https://railsdesk.com/ko/)가 관리합니다. 여기 수록된 일부 거래소와 제휴 관계에 있으며, 그 수익이 데이터 작업의 재원입니다. 기록된 숫자에는 영향을 주지 않습니다 — 과거 스냅샷을 전부 공개해 두는 이유가 바로 직접 검증할 수 있게 하기 위함입니다.
