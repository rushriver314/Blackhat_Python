# Quy định phạm vi được phép (Authorization & Scope)

| Trường | Giá trị |
|---|---|
| Phân loại | INTERNAL |
| Chủ sở hữu | `<OWNER>` |
| Phiên bản | 0.1 (bản nháp) |
| Ngày review kế tiếp | `<YYYY-MM-DD>` |

## Nguyên tắc
Mọi hoạt động tấn công (pentest, SCA, FI, reverse engineering) **chỉ** được thực hiện khi:

1. Có **văn bản cho phép** (hợp đồng, Rules of Engagement, hoặc phê duyệt nội bộ).
2. Mục tiêu nằm **trong phạm vi đã ghi** (thiết bị, serial, dải IP, thời gian).
3. Thiết bị là **tài sản của tổ chức**, board học tập (ví dụ ChipWhisperer target),
   hoặc của khách hàng đã đồng ý bằng văn bản.

## Checklist trước khi bắt đầu
- [ ] Đã có văn bản cho phép — số tham chiếu: `<REF>`
- [ ] Đã xác định phạm vi và ngoài phạm vi
- [ ] Đã đánh giá rủi ro thiết bị (FI có thể làm hỏng phần cứng vĩnh viễn)
- [ ] Đã có người liên hệ khẩn cấp phía chủ thiết bị
- [ ] Đã xác định mức phân loại cho dữ liệu sẽ thu được

## Mẫu mục cần chèn vào mọi tài liệu offensive
```markdown
## Authorization & Scope
- Cơ sở cho phép: <REF>
- Trong phạm vi: <TARGETS>
- Ngoài phạm vi: <EXCLUSIONS>
- Thời gian: <START> → <END>
```
