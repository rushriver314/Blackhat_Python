# Mục lục tài liệu nội bộ

> **Phân loại: INTERNAL**

| Thư mục | Nội dung |
|---|---|
| [`00-policies/`](00-policies/) | Quy định: phân loại dữ liệu, phạm vi được phép |
| [`10-onboarding/`](10-onboarding/) | Tài liệu cho thành viên mới, lộ trình học |
| [`20-lab-guides/sca/`](20-lab-guides/sca/) | Hướng dẫn lab phân tích kênh kề (power/EM, CPA, TVLA) |
| [`20-lab-guides/fi/`](20-lab-guides/fi/) | Hướng dẫn lab gây lỗi (voltage/clock/EM glitching) |
| [`30-runbooks/`](30-runbooks/) | Xử lý sự cố trong lab |
| [`templates/`](templates/) | Mẫu tài liệu và báo cáo |

## Quy ước bắt buộc cho mọi tài liệu

1. **Header metadata** ở đầu file (xem `templates/`):
   `Phân loại`, `Chủ sở hữu`, `Phiên bản`, `Ngày review kế tiếp`.
2. **Không đưa bí mật vào tài liệu.** Dùng placeholder:
   `<TARGET_IP>`, `<CLIENT_A>`, `<AES_KEY>`, `<SERIAL_PORT>`.
3. **Tài liệu offensive** phải có mục *Authorization & Scope*
   (xem [`00-policies/authorization-scope.md`](00-policies/authorization-scope.md)).
4. **Dữ liệu lớn/nhạy cảm** (trace, firmware dump) không commit vào repo;
   `.gitignore` đã chặn sẵn các định dạng phổ biến.
5. **Đặt tên file**: chữ thường, gạch ngang, không dấu — ví dụ `cpa-aes128-cwlite.md`.
6. **Review định kỳ**: mỗi tài liệu được review ít nhất 6 tháng/lần.

## Mức phân loại

| Mức | Ý nghĩa | Ví dụ |
|---|---|---|
| PUBLIC | Có thể công bố | Bài blog, slide hội thảo đã duyệt |
| INTERNAL | Chỉ nội bộ | Lab guide, template, onboarding |
| CONFIDENTIAL | Giới hạn theo dự án | Báo cáo khách hàng, kết quả tấn công trên sản phẩm thật |
| RESTRICTED | Tối mật, cần phê duyệt | Khóa, lỗ hổng chưa công bố (0-day), thông tin hợp đồng |

Chi tiết: [`00-policies/data-classification.md`](00-policies/data-classification.md)
