# Lab SCA-02: TVLA — Đánh giá rò rỉ bằng t-test (fixed-vs-random)

| Trường | Giá trị |
|---|---|
| Phân loại | INTERNAL |
| Chủ sở hữu | `<OWNER>` |
| Phiên bản | 1.0 |
| Ngày tạo | 2026-11-16 |
| Ngày review kế tiếp | 2027-05-16 |
| Thời lượng | 2–3 giờ |
| Trình độ | Người đã làm xong lab SCA-01 |

## Authorization & Scope
- Cơ sở cho phép: bài lab học tập nội bộ, ref `<REF>`
- Thiết bị **trong phạm vi**: target học tập ChipWhisperer (STM32F3, `CWLITEARM`) thuộc tài sản lab
- **Ngoài phạm vi**: thiết bị khách hàng, sản phẩm thương mại — cần phê duyệt riêng

---

## 1. TVLA là gì và khác CPA chỗ nào

| | CPA (lab SCA-01) | TVLA (lab này) |
|---|---|---|
| Mục đích | **Tấn công**: khôi phục khóa | **Đánh giá**: có rò rỉ hay không |
| Cần biết khóa? | Không | Không bắt buộc |
| Kết quả | 16 byte khóa | Một con số: "có / không rò rỉ" |
| Ai dùng | Người tấn công | Người đánh giá, bên cấp chứng nhận, nhóm phòng thủ |

TVLA (Test Vector Leakage Assessment) là công cụ **phòng thủ**. Nó trả lời:
*"Thiết bị của tôi có để lộ thông tin phụ thuộc bí mật qua kênh kề không?"*
Dùng để kiểm tra một biện pháp chống SCA (ví dụ masking) có thực sự hiệu quả.

## 2. Nguyên lý: Welch's t-test

Thu hai nhóm trace:
- **Nhóm fixed**: plaintext **cố định** (một giá trị duy nhất, lặp lại).
- **Nhóm random**: plaintext **ngẫu nhiên**, đổi mỗi lần.

Khóa giữ nguyên ở cả hai nhóm. Nếu thiết bị **không** rò rỉ, điện năng của hai nhóm
về mặt thống kê là như nhau. Nếu **có** rò rỉ, trung bình hai nhóm khác nhau tại
điểm mẫu nào đó.

Tại mỗi điểm mẫu, tính thống kê t của Welch giữa hai nhóm:

```
         mean_fixed − mean_random
t = ─────────────────────────────────────
     √( var_fixed/n_fixed + var_random/n_random )
```

**Ngưỡng tiêu chuẩn: |t| > 4.5.** Nếu bất kỳ điểm mẫu nào vượt ngưỡng này thì kết luận
có rò rỉ đáng kể. Ngưỡng 4.5 tương ứng xác suất báo động giả rất nhỏ với số mẫu lớn.

> **Lưu ý quan trọng:** |t| < 4.5 **không** chứng minh thiết bị an toàn. Nó chỉ nghĩa là
> *với số trace này, chưa phát hiện được rò rỉ*. Rò rỉ nhỏ cần nhiều trace hơn mới lộ.

## 3. Hai cách làm TVLA

- **Non-specific (fixed-vs-random)** — bài này dùng. Đơn giản, phát hiện rò rỉ chung chung.
- **Specific** — so sánh theo một bit/giá trị trung gian cụ thể (ví dụ một bit của S-box).
  Nhạy hơn nhưng cần biết mô hình trung gian.

## 4. Thiết bị & phần mềm
Giống lab SCA-01. Mã nguồn trong [`code/`](code/):

| File | Chức năng |
|---|---|
| `simulate_tvla.py` | Sinh dữ liệu fixed-vs-random giả lập (có cờ `--leak 0` để mô phỏng thiết bị an toàn) |
| `tvla.py` | Tính t-test, in |t| lớn nhất và kết luận |
| `capture_traces.py` | Dùng lại từ SCA-01 để thu trace thật (xem mục 6.2) |

## 5. An toàn & dữ liệu
- Lưu trace ngoài repo (`.gitignore` đã chặn `*.npy`).
- Dùng **cùng khóa** cho cả hai nhóm, nếu không kết quả t sẽ sai.
- Với thiết bị thật, kết quả TVLA về một sản phẩm cụ thể xếp mức CONFIDENTIAL.

## 6. Thực hiện

### 6.1 Luyện tập với dữ liệu giả lập (không cần phần cứng)
```bash
cd docs/20-lab-guides/sca/code

# Thiết bị CÓ rò rỉ
python simulate_tvla.py --n 4000 --leak 1.0 --out tvla_sim
python tvla.py --prefix tvla_sim

# Thiết bị KHÔNG rò rỉ (mô phỏng masking tốt)
python simulate_tvla.py --n 4000 --leak 0 --out tvla_safe
python tvla.py --prefix tvla_safe
```

Kết quả đã kiểm chứng:
```
Thiết bị có rò rỉ   : |t| lớn nhất = 9.26  -> CÓ rò rỉ đáng kể
Thiết bị không rò rỉ: |t| lớn nhất = 3.56  -> KHÔNG phát hiện rò rỉ
```

### 6.2 Thu trace thật
TVLA cần dữ liệu đã đánh nhãn nhóm. Khi thu bằng `capture_traces.py`, với mỗi trace hãy
tung đồng xu: ~50% dùng plaintext cố định (nhóm 1), ~50% dùng plaintext ngẫu nhiên (nhóm 0),
rồi lưu nhãn vào `<prefix>_group.npy`. (Có thể bổ sung cờ cho script này như bài tập mục 9.)

Nên **xen kẽ ngẫu nhiên** hai nhóm trong lúc thu, không thu hết nhóm này rồi mới sang nhóm kia,
để tránh ảnh hưởng của trôi nhiệt độ theo thời gian.

### 6.3 Chạy đánh giá
```bash
python tvla.py --prefix lab2 --out lab2_t.npy
```

### 6.4 Vẽ đồ thị t
```python
import numpy as np, matplotlib.pyplot as plt
t = np.load("lab2_t.npy")
plt.plot(t); plt.axhline(4.5, ls="--"); plt.axhline(-4.5, ls="--")
plt.xlabel("Mẫu"); plt.ylabel("t"); plt.title("TVLA fixed-vs-random"); plt.show()
```
Đỉnh vượt đường ±4.5 là nơi thiết bị rò rỉ.

## 7. Kết quả mong đợi
| Tình huống | |t| lớn nhất điển hình |
|---|---|
| AES không bảo vệ (TinyAES trên STM32F3) | vượt xa 4.5, thường > 10 sau vài nghìn trace |
| AES có masking tốt | nằm dưới 4.5 ngay cả với nhiều trace |

## 8. Xử lý lỗi thường gặp
| Hiện tượng | Nguyên nhân | Cách xử lý |
|---|---|---|
| |t| cao ở **mọi** điểm mẫu | Hai nhóm thu ở thời điểm khác nhau (trôi nhiệt) | Xen kẽ ngẫu nhiên hai nhóm khi thu |
| |t| luôn gần 0 | Nhãn nhóm sai, hoặc hai nhóm dùng khác khóa | Kiểm tra `_group.npy` và giữ khóa cố định |
| Kết quả đổi mỗi lần chạy | Số trace quá ít | Tăng số trace, dùng chung một bộ dữ liệu |

## 9. Câu hỏi & bài tập
1. Vì sao |t| < 4.5 **không** chứng minh thiết bị an toàn?
2. Thêm cờ `--tvla` vào `capture_traces.py` để tự đánh nhãn và lưu `_group.npy`.
3. Làm **TVLA specific**: thay nhãn fixed/random bằng nhãn theo một bit của `SBOX[pt^key]`,
   so sánh độ nhạy với bản non-specific.
4. Vẽ |t| lớn nhất theo số trace (25, 50, 100, …) để thấy rò rỉ lộ dần.

## Lịch sử thay đổi
| Phiên bản | Ngày | Người sửa | Nội dung |
|---|---|---|---|
| 1.0 | 2026-11-16 | Claude | Bản đầu. Script t-test đã kiểm chứng trên dữ liệu giả lập (rò rỉ và an toàn) |
