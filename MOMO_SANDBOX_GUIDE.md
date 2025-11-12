# Hướng Dẫn Sử Dụng Momo Sandbox

## 1. Đăng Ký Tài Khoản Momo Sandbox
- Truy cập: [https://sandbox.momo.vn/](https://sandbox.momo.vn/) hoặc [https://dashboard.momo.vn/](https://dashboard.momo.vn/)
- Đăng ký tài khoản Momo Business và xác thực email
- Vào phần **Sandbox** để tạo application sandbox
- Tạo application sandbox để lấy các thông tin cần thiết

## 2. Lấy Thông Tin Cần Thiết
Sau khi tạo application, bạn sẽ nhận được:
- **Partner Code**: MOMO
- **Access Key**: F8BBA842ECF85
- **Secret Key**: K951B6PE1waDMi640xX08PDJvg6EkV1z
- **Endpoint**: https://test-payment.momo.vn/v2/gateway/api/create

## 3. Cấu Hình Trong App
Thêm vào `app.py` hoặc file config:

```python
from momo_payment import MomoPayment

# Khởi tạo Momo Sandbox
momo = MomoPayment(
    partner_code="MOMO",                           # Partner Code
    access_key="F8BBA842ECF85",                   # Access Key
    secret_key="K951B6PE1waDMi640xX08PDJvg6EkV1z" # Secret Key
)
```

## 4. Sử Dụng Tạo Link Thanh Toán

```python
# Tạo link thanh toán
response = momo.create_payment(
    order_id="123456",                          # ID đơn hàng
    amount=50000,                               # Số tiền (VND)
    order_info="Mua sách tại TVT BookShop",    # Mô tả đơn hàng
    customer_name="Nguyễn Văn A",              # Tên khách hàng
    customer_phone="0987654321",               # Số điện thoại
    return_url="http://localhost:5000/checkout_success",  # URL sau khi thanh toán
    notify_url="http://localhost:5000/momo_notify"       # Webhook URL
)

# Response sẽ trả về link thanh toán
print(response)
```

## 5. Kiểm Tra Trạng Thái Giao Dịch

```python
# Kiểm tra trạng thái
status = momo.check_transaction(order_id="123456")
print(status)
```

## 6. Test Thanh Toán Trên Sandbox
- Sử dụng tài khoản test Momo Sandbox
- **Số điện thoại test**: 0987654321
- **Mật khẩu test**: 123456 (hoặc theo hướng dẫn từ Momo)
- Quét QR code hoặc click link thanh toán để test

## 7. Response Codes Thường Gặp
| Code | Ý Nghĩa |
|------|---------|
| 0 | Thành công |
| 1 | Lỗi không xác định |
| 1000 | Yêu cầu không hợp lệ |
| 1001 | Token không hợp lệ |
| 1002 | Partner bị khóa |
| 9000 | Giao dịch đang xử lý |
| 9001 | Giao dịch thất bại |

## 8. Chuyển Sang Production
Khi sẵn sàng, thay đổi endpoint từ:
```python
# Sandbox (dev)
self.endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"

# Production (live)
self.endpoint = "https://api.momo.vn/v2/gateway/api/create"
```

## 9. Lưu Ý Quan Trọng
- ⚠️ **Không bao giờ** commit Secret Key lên GitHub
- Sử dụng environment variables để lưu trữ thông tin nhạy cảm
- Sandbox có giới hạn số lần test, nên test hợp lý
- Kiểm tra thường xuyên webhook để đảm bảo nhận được thông báo từ Momo

## 10. Sử Dụng Environment Variables (Khuyến Nghị)

Tạo file `.env`:
```
MOMO_PARTNER_CODE=MOMO
MOMO_ACCESS_KEY=F8BBA842ECF85
MOMO_SECRET_KEY=K951B6PE1waDMi640xX08PDJvg6EkV1z
```

Trong app:
```python
import os
from dotenv import load_dotenv

load_dotenv()

momo = MomoPayment(
    partner_code=os.getenv("MOMO_PARTNER_CODE"),
    access_key=os.getenv("MOMO_ACCESS_KEY"),
    secret_key=os.getenv("MOMO_SECRET_KEY")
)
```
