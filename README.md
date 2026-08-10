**English** · [中文](README.zh-CN.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [日本語](README.ja.md) · [Français](README.fr.md) · [Español](README.es.md)

# Exchange Fee Data

Structured, versioned trading-fee data for 7 major crypto venues — spot and perpetual futures, maker and taker. VIP0 is covered today; higher volume tiers are being added. Re-verified every Wednesday, with every weekly snapshot kept in `data/history/`.

JSON and CSV. MIT licensed. No API key, no rate limit, no signup — these are just files in a git repo.

---

## Why this exists

Every exchange publishes a fee schedule, and every exchange publishes it differently. Some use a table, some bury it in a help-center article, some only show your real tier after you log in. Tiers get renamed. Promotional rates expire without an announcement. And nobody keeps the old numbers around.

Which means a question as basic as *"what was Bybit's futures taker fee in March?"* currently has nowhere to be answered.

So we snapshot all of them, once a week, into one schema.

---

## Current snapshot

VIP0, as of the most recent verification pass:

| Exchange | Spot | Futures maker | Futures taker |
|---|---|---|---|
| Binance | 0.100% | 0.020% | 0.050% |
| Bitget | 0.100% | 0.020% | 0.060% |
| Gate.io | 0.100% | 0.020% | 0.050% |
| Bybit | 0.100% | 0.020% | 0.055% |
| OKX | 0.090% | 0.020% | 0.050% |
| Backpack | 0.090% | 0.020% | 0.050% |
| Polymarket | 0.75%–1.8% | — | — |

The authoritative version of this table is `data/fees.json`. The table above is regenerated from it and may lag by a few hours.

---

## Quick start

```bash
# Latest snapshot, all venues
curl -s https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.json

# Just the VIP0 futures taker fees, sorted
curl -s https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.json \
  | jq -r '.exchanges[] | [.id, .futures.vip0.taker] | @tsv' | sort -k2 -n
```

```python
import pandas as pd

URL = "https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.csv"
df = pd.read_csv(URL)

# Cheapest VIP0 taker on perps
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

## Layout

```
data/
├── fees.json              # current snapshot, canonical
├── fees.csv               # same data, flattened
└── history/
    ├── 2026-08-05.json
    ├── 2026-07-29.json
    └── ...
schema/
└── fees.schema.json       # JSON Schema (draft 2020-12)
scripts/
└── validate.py            # run before opening a PR
```

### Schema

```json
{
  "snapshot_date": "2026-08-05",
  "exchanges": [
    {
      "id": "binance",
      "name": "Binance",
      "source_url": "https://www.binance.com/en/fee/schedule",
      "verified_at": "2026-08-05",
      "spot":    { "vip0": { "maker": 0.0010, "taker": 0.0010 } },
      "futures": { "vip0": { "maker": 0.0002, "taker": 0.0005 } },
      "notes": "Holding BNB applies a 25% discount to spot fees."
    }
  ]
}
```

All rates are **decimal fractions**, not percentages and not basis points. `0.0005` means 0.05%. This is the single most common source of error when working with fee data, so the schema enforces it.

`csv` columns: `snapshot_date, exchange_id, market, tier, maker, taker`.

---

## How the numbers are verified

Every Wednesday, each venue's public fee page is read by hand and reconciled against its affiliate dashboard, which is often more current than the public page. Discrepancies are recorded in `notes` rather than silently resolved.

The full reconciliation procedure — what counts as a tier, how promotional rates are treated, what happens when a venue changes its schedule mid-week — is documented at [RAILSDESK methodology](https://railsdesk.com/en/#method).

We do not scrape. Scraping fee pages produces stale and wrong data more often than it produces correct data, because most venues render tiers client-side and gate them behind account state.

---

## Sticker fee vs. effective fee

An important caveat if you're using this dataset to compare venues: **the numbers here are sticker fees.** They are what the exchange charges before any discount you may be entitled to.

Three things routinely move the real number:

1. **Volume tiers** — VIP0 is in the dataset today; VIP1+ is in progress.
2. **Token discounts** — e.g. holding BNB cuts Binance spot fees by 25%. Flagged in `notes`, not in the rate fields.
3. **Affiliate rebates** — a share of the fee routed back to the trader through a referral relationship. Not in this dataset at all, because it depends on which link the account was opened under, not on the exchange's schedule.

That third one is usually the largest of the three and the least documented. Current per-venue rebate rates are tracked separately at [crypto exchange fee rebates](https://railsdesk.com/en/), with the term-by-term comparison in [the analysis section](https://railsdesk.com/en/articles/).

If you're building a cost model, treat these three as separate multipliers. Collapsing them into one "fee" field is how backtests end up optimistic.

---

## Contributing

Corrections are welcome and are the main reason this repo is public.

1. Fork, edit `data/fees.json`
2. Run `python scripts/validate.py` — it checks the schema and flags implausible rates
3. Open a PR with a link to the venue's fee page as evidence

Requests for additional venues: open an issue with the fee schedule URL. The bar is a venue with public, machine-readable fee documentation and meaningful volume.

---

## License

MIT for the code. [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) for the data — use it commercially, redistribute it, build products on it; just keep the attribution.

---

## Disclaimer

This is fee data, not investment advice. Crypto derivatives can lose you your entire deposit. Rates change; the snapshot in this repo may be up to seven days stale. Verify against the venue before it matters to you.

Maintained by [RAILSDESK](https://railsdesk.com/en/), which earns affiliate commission from some of the venues listed here. That relationship funds the data work and does not affect the recorded numbers — the whole point of publishing the history is that you can check.
