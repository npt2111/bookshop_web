# 🚀 Quick Start - MoMo Sandbox Payment

## 📋 Tóm Tắt Nhanh

Đã tích hợp **MoMo Sandbox Payment** - một giao diện thanh toán ảo hoàn toàn cho mục đích test.

## ✅ Những Gì Đã Thêm

### 1️⃣ File Mới
- `templates/momo_payment.html` - Giao diện thanh toán MoMo đẹp, tương thích mobile

### 2️⃣ File Đã Sửa
- `templates/checkout_form.html` - Thêm lựa chọn 3 phương thức thanh toán (MoMo, COD, Transfer)
- `app.py` - Thêm 3 route xử lý MoMo

### 3️⃣ File Hỗ Trợ
- `MOMO_SANDBOX_GUIDE.md` - Hướng dẫn chi tiết
- `test_momo.py` - Script test

## 🎯 Cách Sử Dụng

### Bước 1: Thêm Sản Phẩm Vào Giỏ
```
Trang Chủ → Chọn Sản Phẩm → Mua Ngay (hoặc Thêm Vào Giỏ)
```

### Bước 2: Thanh Toán
```
Giỏ Hàng → Thanh Toán
```

### Bước 3: Chọn Phương Thức Thanh Toán
```
Nhập Thông Tin Khách Hàng → Chọn "MoMo" → Tiếp Tục
```

### Bước 4: Giao Diện MoMo Sandbox
Sẽ thấy:
- 📱 QR Code (để test, không thực)
- ⏱️ Đồng hồ 5 phút đếm ngược
- 💳 Tài khoản MoMo ảo: `0866123456`
- 📋 Thông tin đơn hàng
- 3 nút hành động:
  - ✅ Thanh Toán Thành Công
  - 🔄 Đổi Phương Thức
  - ❌ Hủy Thanh Toán

### Bước 5: Hoàn Tất
```
Click "Thanh Toán Thành Công" → Thấy trang success
```

## 🧪 Test

### Chạy Test File
```bash
python test_momo.py
```

Kết quả: ✅ Tất cả checks passed!

## 📊 Quy Trình Hoạt Động

```
┌─────────────────┐
│  Giỏ Hàng       │
└────────┬────────┘
         │ Thanh Toán
         ▼
┌─────────────────────────────────┐
│ Checkout Form (Chọn PP TT)      │
│ - MoMo (New!)                   │
│ - COD                           │
│ - Transfer                      │
└────────┬────────────────────────┘
         │ Chọn MoMo
         ▼
┌─────────────────────────────────┐
│ MoMo Sandbox Payment (New!)     │
│ - QR Code                       │
│ - Tài Khoản Ảo                  │
│ - Thông Tin Đơn Hàng            │
│ - 3 Nút Hành Động               │
└────────┬────────────────────────┘
         │ Thanh Toán Thành Công
         ▼
┌─────────────────────────────────┐
│ Success Page                    │
│ - Lưu vào DB                    │
│ - Xóa checkout_items session    │
│ - Gửi webhook (nếu có)          │
└─────────────────────────────────┘
```

## 🔐 Tài Khoản MoMo Ảo (Test)

```
Số điện thoại: 0866123456
Tên tài khoản: Nguyễn Bán Hàng
Số dư: 50.000.000 VND
⚠️ Chỉ là ảo, không thực tế
```

## 🎨 Đặc Điểm Giao Diện

✨ **Responsive Design** - Tự động responsive cho mobile/tablet/desktop
🎀 **MoMo Pink Theme** - Màu sắc chính thức MoMo
⏰ **Live Timer** - Đồng hồ đếm ngược 5 phút
📱 **QR Code** - QR code động (ảo)
🎉 **Toast Notifications** - Thông báo hiệu ứng
♿ **Accessible** - Hỗ trợ keyboard navigation

## 🔧 Routes Đã Thêm

| Route | Method | Mô Tả |
|-------|--------|-------|
| `/momo_payment` | POST | Hiển thị giao diện MoMo sandbox |
| `/momo_success/<order_id>` | GET | Xử lý thanh toán thành công |
| `/momo_cancel` | GET | Xử lý hủy thanh toán |

## 💾 Dữ Liệu Lưu Trữ

Khi thanh toán thành công:

```python
{
    "order_id": "MOMO-123456",
    "name": "Khách Hàng",
    "email": "email@example.com",
    "phone": "0123456789",
    "address": "Địa chỉ giao hàng",
    "note": "Ghi chú",
    "product": [...],
    "total_amount": 150000,
    "status": "pending",
    "payment_method": "momo",  # ← Mới
    "customer_id": "xxx",
    "created_at": "2024-01-01T00:00:00"
}
```

## 🎓 Mở Rộng

### Muốn Thêm Xác Thực Thực MoMo?

1. Tạo tài khoản MoMo Sandbox
2. Lấy API Key từ MoMo
3. Sửa `momo_payment_page()` để call API MoMo
4. Sửa `momo_success()` để verify transaction

### Muốn Thay Đổi Thông Tin Tài Khoản Ảo?

Edit `templates/momo_payment.html` line 151-154:
```html
<p><strong>Số điện thoại:</strong> 0866123456</p>
<p><strong>Tên tài khoản:</strong> Nguyễn Bán Hàng</p>
<p><strong>Số dư:</strong> 50.000.000 VND</p>
```

## ⚠️ Lưu Ý

- ✅ Đây là **sandbox** - **không có giao dịch thực tế**
- ✅ Dữ liệu MoMo (số điện thoại, tài khoản) là **tùy chọn**
- ✅ QR Code được **tạo ngẫu nhiên** - chỉ để hiển thị
- ✅ Tất cả đều **ảo** - dùng cho **test/demo**

## 📞 Cần Giúp?

1. Check `MOMO_SANDBOX_GUIDE.md` để hướng dẫn chi tiết
2. Check browser console (F12) nếu có lỗi JS
3. Check Flask terminal nếu có lỗi server
4. Check database (Supabase) để xem order có được lưu không

---

**✅ Setup hoàn tất! Bắt đầu test ngay!** 🎉
