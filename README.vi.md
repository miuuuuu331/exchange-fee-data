[English](README.md) · [中文](README.zh-CN.md) · [한국어](README.ko.md) · **Tiếng Việt** · [日本語](README.ja.md) · [Français](README.fr.md) · [Español](README.es.md)

# Bộ dữ liệu phí giao dịch của các sàn

Dữ liệu phí giao dịch có cấu trúc của 7 sàn crypto lớn — spot và hợp đồng vĩnh cửu, maker và taker. Hiện đã có VIP0, các bậc khối lượng cao hơn đang được bổ sung. Được kiểm tra lại thủ công vào mỗi thứ Tư, và mọi ảnh chụp hằng tuần đều được giữ lại trong `data/history/`.

Định dạng JSON và CSV. Giấy phép MIT. Không cần API key, không giới hạn số lần gọi, không cần đăng ký — chỉ là mấy file trong một repo git.

---

## Vì sao có bộ dữ liệu này

Sàn nào cũng công bố biểu phí, nhưng mỗi sàn công bố một kiểu. Có sàn để dạng bảng, có sàn giấu trong một bài viết ở trung tâm trợ giúp, có sàn phải đăng nhập mới thấy đúng bậc của mình. Tên bậc thì đổi, mức phí khuyến mãi thì hết hạn mà không thông báo, và không ai giữ lại những con số cũ.

Kết quả là một câu hỏi cơ bản như **"phí taker hợp đồng của Bybit hồi tháng Ba là bao nhiêu?"** hiện không tra được ở đâu cả.

Nên chúng tôi chụp lại toàn bộ, mỗi tuần một lần, theo cùng một schema.

---

## Ảnh chụp hiện tại

Bậc VIP0, theo lần kiểm tra gần nhất:

| Sàn | Spot | Futures maker | Futures taker |
|---|---|---|---|
| Binance | 0.100% | 0.020% | 0.050% |
| Bitget | 0.100% | 0.020% | 0.060% |
| Gate.io | 0.100% | 0.020% | 0.050% |
| Bybit | 0.100% | 0.020% | 0.055% |
| OKX | 0.090% | 0.020% | 0.050% |
| Backpack | 0.090% | 0.020% | 0.050% |
| Polymarket | 0.75%–1.8% | — | — |

Bản chuẩn là `data/fees.json`. Bảng ở trên được sinh ra từ đó và có thể chậm vài giờ.

---

## Bắt đầu nhanh

```bash
# Toàn bộ ảnh chụp mới nhất
curl -s https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.json

# Chỉ lấy phí taker futures VIP0, sắp xếp tăng dần
curl -s https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.json \
  | jq -r '.exchanges[] | [.id, .futures.vip0.taker] | @tsv' | sort -k2 -n
```

```python
import pandas as pd

URL = "https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.csv"
df = pd.read_csv(URL)

# Sàn có phí taker perp VIP0 rẻ nhất
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

## Cấu trúc thư mục

```
data/
├── fees.json              # ảnh chụp hiện tại, bản chuẩn
├── fees.csv               # cùng dữ liệu, dạng phẳng
└── history/
    ├── 2026-08-05.json
    ├── 2026-07-29.json
    └── ...
schema/
└── fees.schema.json       # JSON Schema (draft 2020-12)
scripts/
└── validate.py            # chạy trước khi mở PR
```

### Schema

```json
{
  "snapshot_date": "2026-08-05",
  "exchanges": [
    {
      "id": "binance",
      "name": "Binance",
      "source_url": "https://www.binance.com/vi/fee/schedule",
      "verified_at": "2026-08-05",
      "spot":    { "vip0": { "maker": 0.0010, "taker": 0.0010 } },
      "futures": { "vip0": { "maker": 0.0002, "taker": 0.0005 } },
      "notes": "Nắm giữ BNB được giảm 25% phí spot."
    }
  ]
}
```

Mọi mức phí đều là **số thập phân**, không phải phần trăm và cũng không phải basis point. `0.0005` nghĩa là 0.05%. Đây là chỗ hay sai nhất khi làm việc với dữ liệu phí, nên schema bắt buộc theo quy ước này.

Các cột CSV: `snapshot_date, exchange_id, market, tier, maker, taker`.

---

## Cách các con số được kiểm chứng

Mỗi thứ Tư, trang biểu phí công khai của từng sàn được mở ra đọc thủ công, rồi đối chiếu với số liệu trong dashboard đối tác — vốn thường được cập nhật sớm hơn trang công khai. Khi hai bên lệch nhau, chúng tôi ghi lại vào trường `notes` thay vì tự chọn một bên.

Toàn bộ quy trình đối chiếu — thế nào thì tính là một bậc, xử lý mức phí khuyến mãi ra sao, làm gì khi sàn đổi biểu phí giữa tuần — được mô tả tại [phương pháp đánh giá của RAILSDESK](https://railsdesk.com/vi/#method).

Chúng tôi không crawl. Crawl trang biểu phí tạo ra dữ liệu sai thường xuyên hơn là dữ liệu đúng, vì phần lớn sàn render bậc phí ở phía client và hiển thị khác nhau tùy trạng thái tài khoản.

---

## Phí niêm yết khác với phí thực trả

Nếu bạn định dùng bộ dữ liệu này để so sánh giữa các sàn, cần lưu ý trước một điều: **các con số ở đây là phí niêm yết**, tức mức giá trước mọi khoản giảm trừ mà bạn có thể được hưởng.

Ba yếu tố thường xuyên làm thay đổi con số thực tế:

1. **Bậc theo khối lượng** — hiện bộ dữ liệu có VIP0, từ VIP1 trở lên đang bổ sung.
2. **Giảm giá bằng token sàn** — ví dụ giữ BNB thì phí spot Binance giảm 25%. Ghi trong `notes`, không nằm ở trường phí.
3. **Hoàn phí qua giới thiệu** — một phần phí được trả ngược lại cho trader thông qua quan hệ giới thiệu. Hoàn toàn không có trong bộ dữ liệu này, vì nó phụ thuộc vào việc tài khoản được mở qua link nào, chứ không phụ thuộc biểu phí của sàn.

Yếu tố thứ ba thường là khoản lớn nhất trong ba, đồng thời cũng là khoản ít tài liệu công khai nhất. Tỷ lệ hoàn phí hiện hành của từng sàn được theo dõi riêng tại [bảng xếp hạng hoàn phí giao dịch](https://railsdesk.com/vi/), còn phần so sánh từng điều khoản thanh toán nằm trong [chuyên mục phân tích](https://railsdesk.com/vi/articles/).

Nếu bạn đang dựng mô hình chi phí, hãy để ba yếu tố này là ba hệ số nhân độc lập. Gộp chúng thành một trường `fee` duy nhất là nguyên nhân phổ biến khiến kết quả backtest đẹp hơn thực tế.

---

## Đóng góp

Rất hoan nghênh các đính chính — đó cũng là lý do chính khiến repo này được để công khai.

1. Fork, sửa `data/fees.json`
2. Chạy `python scripts/validate.py` — script kiểm tra schema và cảnh báo các mức phí bất thường
3. Mở PR kèm link tới trang biểu phí của sàn làm bằng chứng

Muốn thêm sàn mới: mở issue kèm URL biểu phí. Tiêu chí là sàn có tài liệu phí công khai, đọc được bằng máy, và có khối lượng giao dịch đáng kể.

---

## Giấy phép

Mã nguồn theo MIT. Dữ liệu theo [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — dùng thương mại, phân phối lại, xây sản phẩm trên đó đều được; chỉ cần giữ ghi nhận nguồn.

---

## Miễn trừ trách nhiệm

Đây là dữ liệu phí, không phải lời khuyên đầu tư. Giao dịch phái sinh crypto có thể khiến bạn mất toàn bộ vốn. Mức phí thay đổi liên tục, ảnh chụp trong repo có thể cũ tới bảy ngày — hãy kiểm tra lại trên sàn trước khi dùng cho quyết định thực tế.

Được duy trì bởi [RAILSDESK](https://railsdesk.com/vi/). Chúng tôi nhận hoa hồng đối tác từ một số sàn được liệt kê ở đây; khoản đó tài trợ cho công việc thu thập dữ liệu và không tác động đến các con số được ghi lại — chính vì vậy toàn bộ lịch sử ảnh chụp được công khai để bạn tự kiểm chứng.
