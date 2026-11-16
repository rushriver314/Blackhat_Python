# Lab SCA-01: Tấn công CPA lên AES-128 bằng ChipWhisperer-Lite

| Trường | Giá trị |
|---|---|
| Phân loại | INTERNAL |
| Chủ sở hữu | `<OWNER>` |
| Phiên bản | 1.0 |
| Ngày tạo | 2026-11-16 |
| Ngày review kế tiếp | 2027-05-16 |
| Thời lượng | 3–4 giờ |
| Trình độ | Thực tập sinh / người mới học SCA |

## Authorization & Scope
- Cơ sở cho phép: bài lab học tập nội bộ, ref `<REF>`
- Thiết bị **trong phạm vi**: board target học tập ChipWhisperer (STM32F3, `CWLITEARM`) thuộc tài sản lab
- **Ngoài phạm vi**: mọi thiết bị của khách hàng hoặc sản phẩm thương mại. Muốn làm trên các thiết bị đó phải có phê duyệt riêng.

---

## 1. Mục tiêu học tập
Sau bài lab, bạn có thể:
1. Giải thích vì sao điện năng tiêu thụ của vi điều khiển làm lộ dữ liệu đang xử lý.
2. Thu được trace điện năng khi target chạy AES-128.
3. Dùng **CPA** để khôi phục toàn bộ 16 byte khóa AES.
4. Đánh giá xem cần bao nhiêu trace để tấn công thành công.

## 2. Kiến thức nền

### 2.1 Mô hình rò rỉ Hamming weight
Khi CPU ghi một giá trị lên bus hoặc thanh ghi, điện năng tiêu thụ tăng gần tỉ lệ với
**số bit bằng 1** của giá trị đó, gọi là Hamming weight (HW).
Ví dụ: `HW(0x00) = 0`, `HW(0xFF) = 8`, `HW(0x3C) = 4`.

### 2.2 Điểm tấn công: đầu ra S-box vòng 1
Ở vòng 1 của AES, với mỗi byte `b`:

```
v = SBOX[ plaintext[b] XOR key[b] ]
```

- Ta **biết** `plaintext[b]`.
- Ta **không biết** `key[b]`, nhưng nó chỉ có **256 khả năng**.
- Vì S-box là phi tuyến, khóa đoán sai cho ra giả thuyết gần như không tương quan với trace.

### 2.3 Thuật toán CPA
Với mỗi byte khóa và mỗi khóa đoán `k` (0..255):
1. Tính giả thuyết `h = HW(SBOX[pt XOR k])` cho mọi trace.
2. Tính hệ số tương quan Pearson giữa `h` và điện năng tại **từng điểm mẫu**.
3. Khóa đoán có |tương quan| lớn nhất được coi là khóa đúng.

```
          Σ (h - h̄)(t - t̄)
ρ = ───────────────────────────────
     √Σ (h - h̄)² · √Σ (t - t̄)²
```

Độ phức tạp chỉ là 16 × 256 phép thử, thay vì 2¹²⁸ nếu vét cạn.

## 3. Thiết bị & phần mềm

| Thành phần | Phiên bản / model |
|---|---|
| Capture board | ChipWhisperer-Lite (CW1173) |
| Target | CW308 / CW-Lite ARM, STM32F303 (`PLATFORM=CWLITEARM`) |
| Phần mềm | Python ≥ 3.9, `chipwhisperer` 5.x, `numpy`, `tqdm` |
| Firmware | `simpleserial-aes`, thư viện `TINYAES128C` |
| Máy tính | Linux / Windows / macOS có cổng USB |

Mã nguồn đi kèm nằm trong thư mục [`code/`](code/):

| File | Chức năng |
|---|---|
| `aes_common.py` | Bảng S-box và bảng Hamming weight |
| `simulate_traces.py` | Sinh trace giả lập để luyện tập khi chưa có phần cứng |
| `capture_traces.py` | Thu trace thật từ ChipWhisperer |
| `cpa_attack.py` | Chạy CPA, in khóa khôi phục và hạng của khóa đúng |

## 4. An toàn
- Cắm USB **trước** khi chạm vào board. Làm việc trên thảm chống tĩnh điện (ESD).
- Không cắm hoặc rút board target khi đang cấp nguồn.
- Lưu trace **ngoài repo**. `.gitignore` đã chặn sẵn `*.npy` và `traces/`.
- Khóa trong bài là **khóa thử công khai trong FIPS-197**, không phải bí mật.
  Với thiết bị thật, khóa khôi phục được xếp mức **RESTRICTED**
  (xem [`../../00-policies/data-classification.md`](../../00-policies/data-classification.md)).

## 5. Thiết lập

### 5.1 Cài phần mềm
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install chipwhisperer numpy tqdm
```

### 5.2 Build firmware
Trong thư mục cài ChipWhisperer:
```bash
cd chipwhisperer/hardware/victims/firmware/simpleserial-aes
make PLATFORM=CWLITEARM CRYPTO_TARGET=TINYAES128C SS_VER=SS_VER_2_1
# Kết quả: simpleserial-aes-CWLITEARM.hex
```

> Nếu firmware dùng SimpleSerial v1, hãy thêm cờ `--ss1` khi chạy `capture_traces.py`.

## 6. Thực hiện

### Bước 0 (khuyến nghị): luyện tập với dữ liệu giả lập
Bước này không cần phần cứng. Nó giúp bạn hiểu kết quả CPA trông như thế nào.

```bash
cd docs/20-lab-guides/sca/code
python simulate_traces.py --n 2000 --noise 2.0 --out sim
python cpa_attack.py --prefix sim --key 2b7e151628aed2a6abf7158809cf4f3c
```

Kết quả đã kiểm chứng:
```
Khóa khôi phục: 2b7e151628aed2a6abf7158809cf4f3c
Đúng 16/16 byte
```

Thử giảm số trace bằng `--n 50`: kết quả chỉ đúng khoảng 6/16 byte.
Đây là lý do cần đủ số trace.

### Bước 1: kết nối và nạp firmware, thu trace
```bash
python capture_traces.py --hex simpleserial-aes-CWLITEARM.hex --n 2000 --out lab1
```
Script sinh ra các file `lab1_traces.npy`, `lab1_textin.npy`, `lab1_textout.npy`
và `lab1_key.npy` (khóa chỉ dùng để tự kiểm tra kết quả).

### Bước 2: quan sát trace
Mở Jupyter và vẽ vài trace:
```python
import numpy as np, matplotlib.pyplot as plt
t = np.load("lab1_traces.npy")
plt.plot(t[:5].T); plt.xlabel("Mẫu"); plt.ylabel("Điện áp (tương đối)"); plt.show()
```
Hãy tìm **10 vùng lặp lại**. Đó là 10 vòng của AES-128.

### Bước 3: chạy CPA
```bash
python cpa_attack.py --prefix lab1
```
Cột `Hạng khóa đúng` cho biết khóa đúng đứng thứ mấy. Hạng `0` nghĩa là đã tìm đúng byte đó.

### Bước 4: đo số trace tối thiểu
```bash
for n in 25 50 100 200 500 1000; do
  echo "== $n trace =="; python cpa_attack.py --prefix lab1 --n $n | tail -1
done
```
Ghi lại số trace nhỏ nhất mà kết quả vẫn đúng 16/16 byte.

## 7. Kết quả mong đợi
| Tiêu chí | Giá trị tham khảo (CW-Lite + STM32F3, TinyAES) |
|---|---|
| Đỉnh tương quan của khóa đúng | ≈ 0.4 – 0.8 |
| Số trace để đúng 16/16 byte | khoảng 30 – 100 |
| Vị trí đỉnh | nằm trong vùng vòng 1, ngay sau khi nạp plaintext |

> Các con số trên chỉ để tham khảo. Hãy ghi số liệu thật của bạn vào phần báo cáo.

## 8. Xử lý lỗi thường gặp

| Hiện tượng | Nguyên nhân có thể | Cách xử lý |
|---|---|---|
| `capture_trace` trả về `None` nhiều lần | Sai phiên bản SimpleSerial | Thêm `--ss1` hoặc build lại với `SS_VER_2_1` |
| Không tìm thấy thiết bị USB | Thiếu driver hoặc quyền udev | Linux: cài udev rules của ChipWhisperer, rồi rút và cắm lại |
| Tương quan thấp ở mọi byte (< 0.1) | Trace bị lệch thời gian, hoặc số mẫu quá ít | Kiểm tra trigger, tăng `--samples`, xem lại cài đặt clock |
| Vài byte sai, các byte khác đúng | Chưa đủ trace | Tăng `--n` lên 2–5 lần |
| Lỗi khi nạp firmware | Sai `PLATFORM` hoặc sai file `.hex` | Kiểm tra lại tên platform và đường dẫn file |

## 9. Lưu trữ dữ liệu
- Trace lưu tại: `<STORAGE_PATH>/sca/lab1/` (ngoài repo)
- Mức phân loại dữ liệu: INTERNAL, vì đây là target học tập dùng khóa công khai
- Xóa dữ liệu sau khi hoàn thành báo cáo, hoặc lưu trữ theo quy định của nhóm

## 10. Câu hỏi kiểm tra
1. Vì sao tấn công vào **đầu ra S-box** thay vì vào `pt XOR key`?
2. Nếu firmware dùng **masking**, CPA bậc 1 còn hiệu quả không? Vì sao?
3. Mô hình Hamming distance khác Hamming weight như thế nào? Khi nào nên dùng mô hình nào?

## 11. Bài tập mở rộng
- Thêm **căn chỉnh trace** (cross-correlation) rồi so sánh số trace cần dùng.
- Thực hiện **TVLA** (Welch t-test, fixed so với random) để chứng minh có rò rỉ.
- Tấn công **vòng cuối** bằng ciphertext (`lab1_textout.npy`) với mô hình Hamming distance.
- Dùng EM probe thay cho đo điện năng (lab SCA-04).

## Lịch sử thay đổi
| Phiên bản | Ngày | Người sửa | Nội dung |
|---|---|---|---|
| 1.0 | 2026-11-16 | Claude | Bản đầu tiên. Script CPA đã kiểm chứng trên dữ liệu giả lập |
