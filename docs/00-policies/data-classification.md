# Quy định phân loại & xử lý dữ liệu

| Trường | Giá trị |
|---|---|
| Phân loại | INTERNAL |
| Chủ sở hữu | `<OWNER>` |
| Phiên bản | 0.1 (bản nháp) |
| Ngày review kế tiếp | `<YYYY-MM-DD>` |

## 1. Mục đích
Đảm bảo tài liệu, dữ liệu thí nghiệm và thông tin khách hàng được lưu trữ,
chia sẻ và hủy đúng mức độ nhạy cảm.

## 2. Bảng xử lý theo mức

| Hành động | INTERNAL | CONFIDENTIAL | RESTRICTED |
|---|---|---|---|
| Lưu trong repo private | ✅ | ✅ (thư mục dự án riêng) | ❌ — chỉ kho mã hóa riêng |
| Gửi qua chat/email nội bộ | ✅ | ⚠️ Chỉ người trong dự án | ❌ |
| Đưa lên dịch vụ bên ngoài / AI | ⚠️ Đã loại thông tin nhạy cảm | ❌ | ❌ |
| In ấn | ✅ | ⚠️ Thu hồi sau khi dùng | ❌ |
| Hủy | Xóa thường | Xóa an toàn | Xóa an toàn + ghi biên bản |

## 3. Dữ liệu đặc thù SCA/FI
- **Trace** (power/EM): lưu ngoài repo, đặt tên theo `<PROJECT>_<DATE>_<SETUP>`;
  nếu thu trên thiết bị khách hàng → CONFIDENTIAL.
- **Khóa đã khôi phục** (ví dụ khóa AES từ CPA) → RESTRICTED; trong báo cáo chỉ ghi
  vài byte đầu hoặc mã băm để chứng minh.
- **Firmware dump** → CONFIDENTIAL trở lên; không commit (đã chặn trong `.gitignore`).
- **Tham số glitch thành công** trên sản phẩm thật → CONFIDENTIAL cho tới khi công bố có phối hợp.

## 4. Vi phạm
Phát hiện rò rỉ → báo ngay `<SECURITY_CONTACT>` và làm theo
[`../30-runbooks/`](../30-runbooks/) (runbook rò rỉ dữ liệu — sẽ bổ sung).
