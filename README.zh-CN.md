[English](README.md) · **中文** · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [日本語](README.ja.md) · [Français](README.fr.md) · [Español](README.es.md)

# 交易所费率数据集

7 家主流加密交易所的结构化费率数据——现货与永续合约，maker 与 taker。目前覆盖 VIP0，更高成交量档位正在陆续补充。每周三人工复核一次，每期快照都保留在 `data/history/` 里。

JSON 和 CSV 两种格式。MIT 协议。不需要 API key，没有频率限制，不用注册——就是 git 仓库里的几个文件。

---

## 为什么要做这个

每家交易所都公布费率表，但每家公布的方式都不一样。有的放在表格里，有的埋在帮助中心的文章里，有的必须登录后才显示你的真实档位。档位名称会改，活动费率会悄无声息地到期，而且没有人会把旧数字留下来。

结果是，一个再基础不过的问题——**"Bybit 三月份的合约 taker 费率是多少？"**——现在根本无处可查。

所以我们每周给所有交易所拍一次快照，统一到同一套 schema 里。

---

## 当前快照

VIP0 档，取自最近一次复核：

| 交易所 | 现货 | 合约 maker | 合约 taker |
|---|---|---|---|
| Binance | 0.100% | 0.020% | 0.050% |
| Bitget | 0.100% | 0.020% | 0.060% |
| Gate.io | 0.100% | 0.020% | 0.050% |
| Bybit | 0.100% | 0.020% | 0.055% |
| OKX | 0.090% | 0.020% | 0.050% |
| Backpack | 0.090% | 0.020% | 0.050% |
| Polymarket | 0.75%–1.8% | — | — |

以 `data/fees.json` 为准。上面这张表由它生成，可能滞后几个小时。

---

## 快速开始

```bash
# 拉取最新快照
curl -s https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.json

# 只看 VIP0 合约 taker 费率，从低到高
curl -s https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.json \
  | jq -r '.exchanges[] | [.id, .futures.vip0.taker] | @tsv' | sort -k2 -n
```

```python
import pandas as pd

URL = "https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.csv"
df = pd.read_csv(URL)

# VIP0 永续合约 taker 最便宜的是谁
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

## 目录结构

```
data/
├── fees.json              # 当前快照，以此为准
├── fees.csv               # 同一份数据，展平成表
└── history/
    ├── 2026-08-05.json
    ├── 2026-07-29.json
    └── ...
schema/
└── fees.schema.json       # JSON Schema (draft 2020-12)
scripts/
└── validate.py            # 提 PR 前先跑一遍
```

### 数据结构

```json
{
  "snapshot_date": "2026-08-05",
  "exchanges": [
    {
      "id": "binance",
      "name": "Binance",
      "source_url": "https://www.binance.com/zh-CN/fee/schedule",
      "verified_at": "2026-08-05",
      "spot":    { "vip0": { "maker": 0.0010, "taker": 0.0010 } },
      "futures": { "vip0": { "maker": 0.0002, "taker": 0.0005 } },
      "notes": "持有 BNB 可享现货手续费 25% 折扣。"
    }
  ]
}
```

所有费率都是**小数**，不是百分比，也不是基点。`0.0005` 表示 0.05%。这是处理费率数据时最常见的出错点，所以 schema 里做了强校验。

CSV 列：`snapshot_date, exchange_id, market, tier, maker, taker`。

---

## 数据怎么核的

每周三人工打开各家的公开费率页，再和联盟后台的费率对一遍——后台的数字往往比公开页更新得早。两边对不上的时候，我们记在 `notes` 字段里，不擅自取其一。

完整的核对流程——什么算一个档位、活动费率怎么处理、交易所周中改费率怎么办——写在 [RAILSDESK 评测方法](https://railsdesk.com/#method)。

我们不做爬虫。爬费率页产出错误数据的概率高于产出正确数据，因为大多数交易所的档位是客户端渲染的，而且和账户状态绑定。

---

## 名义费率 ≠ 实付费率

如果你打算用这份数据横向比较交易所，有一点必须先说清楚：**这里的数字是名义费率**，是交易所在任何折扣之前收的价。

真实成本通常被三件事改写：

1. **成交量档位**——目前收录 VIP0，VIP1 以上正在补充。
2. **平台币折扣**——比如持有 BNB，币安现货费率打 75 折。这类信息记在 `notes` 里，不体现在费率字段。
3. **返佣**——通过邀请关系把一部分手续费退回给交易者。这部分完全不在本数据集里，因为它取决于你的账户是从哪个链接注册的，不取决于交易所的费率表。

第三项通常是三者里金额最大、也最没有公开文档的一项。各家的现行返佣比例单独维护在 [交易所返佣排行](https://railsdesk.com/)，逐条结算口径的对比在 [深度与测评](https://railsdesk.com/articles/)。

做成本模型的话，建议把这三项当成三个独立的乘数。把它们压成一个 "fee" 字段，是回测结果虚高的常见原因。

---

## 参与贡献

欢迎纠错——这也是这个仓库公开的主要原因。

1. Fork，改 `data/fees.json`
2. 跑 `python scripts/validate.py`，它会校验 schema 并标出明显不合理的费率
3. 提 PR，附上交易所费率页的链接作为依据

想加新交易所：开 issue，附费率页 URL。门槛是该所有公开、可机读的费率文档，且有实际交易量。

---

## 许可

代码 MIT。数据 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)——可以商用、可以再分发、可以拿去做产品，保留署名即可。

---

## 免责声明

这是费率数据，不是投资建议。加密衍生品交易可能导致本金全部损失。费率会变，仓库里的快照最多可能滞后七天，真要用于决策前请回官网复核。

由 [RAILSDESK](https://railsdesk.com/) 维护。我们与部分列出的交易所存在联盟佣金关系，这笔收入用于支撑数据采集工作，不影响记录的数字——把历史快照全部公开，就是为了让你能自己查。
