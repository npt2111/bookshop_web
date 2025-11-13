# 🎉 Hướng Dẫn Sử Dụng MoMo Sandbox Payment

## 📝 Mô Tả Chức Năng

Đã tích hợp giao diện thanh toán MoMo **SANDBOX** (ảo) vào ứng dụng bookshop. Đây là phương thức test không kết nối với hệ thống MoMo thực tế.

## 🚀 Các Tính Năng

### 1. **Chọn Phương Thức Thanh Toán**
- Khi người dùng click "Tiếp tục thanh toán" từ giỏ hàng, họ sẽ đến trang **checkout_form.html**
- Trang này có 3 phương thức thanh toán:
  - 📱 **MoMo** (Sandbox)
  - 💵 **Thanh Toán Khi Nhận Hàng (COD)**
  - 🏦 **Chuyển Khoản Ngân Hàng**

### 2. **Giao Diện Thanh Toán MoMo**
Khi chọn **MoMo**, người dùng sẽ thấy một giao diện chuyên dụng với:

#### Bên Trái - Mã QR:
- 📱 QR Code được tạo ngẫu nhiên (chỉ mục đích hiển thị)
- ⏱️ Đồng hồ đếm ngược 5 phút
- 📌 Ghi chú: "Quét mã QR bằng ứng dụng MoMo"

#### Bên Phải - Thông Tin:
- **Tài Khoản MoMo Ảo:**
  - Số điện thoại: `0866123456`
  - Tên tài khoản: `Nguyễn Bán Hàng`
  - Số dư: `50.000.000 VND`
  - ⚠️ Cảnh báo: Đây chỉ là tài khoản ảo dùng test

- **Thông Tin Đơn Hàng:**
  - Mã đơn hàng (MOMO-XXXXXX)
  - Tên khách hàng
  - Số điện thoại khách hàng
  - Số lượng sản phẩm
  - **Tổng tiền** (hiển thị nổi bật)

#### Nút Hành Động:
- ✅ **Thanh Toán Thành Công** - Hoàn tất đơn hàng (ảo)
- 🔄 **Đổi Phương Thức Thanh Toán** - Quay lại chọn phương thức khác
- ❌ **Hủy Thanh Toán** - Hủy đơn hàng

### 3. **Quy Trình Hoạt Động**

```
Giỏ Hàng → Checkout Form (Chọn Phương Thức)
   ↓
   └─→ Chọn MoMo → Giao Diện MoMo Sandbox
       ├─ Thanh Toán Thành Công → Lưu Đơn & Redirect Success
       ├─ Đổi Phương Thức → Quay Lại Checkout Form
       └─ Hủy Thanh Toán → Error Page
```

### 4. **Dữ Liệu Lưu Trữ**

Khi người dùng click "Thanh Toán Thành Công":
1. ✅ Đơn hàng được lưu vào Supabase với:
   - `status = 'pending'` (chờ xác nhận)
   - `payment_method = 'momo'`
   - `order_id = MOMO-XXXXXX`

2. 🔔 Gửi webhook tới n8n (nếu được cấu hình)

3. 🛒 Xóa sản phẩm khỏi giỏ hàng

4. 📄 Hiển thị trang **checkout_success.html** với thông tin đơn hàng

## 📁 File Tạo/Sửa

### ✨ File Mới Tạo:
- `templates/momo_payment.html` - Giao diện thanh toán MoMo

### ✏️ File Đã Sửa:
- `templates/checkout_form.html` - Thêm lựa chọn phương thức thanh toán
- `app.py` - Thêm 3 route mới:
  - `/momo_payment` (POST) - Hiển thị giao diện MoMo
  - `/momo_success/<order_id>` (GET) - Xử lý khi thanh toán thành công
  - `/momo_cancel` (GET) - Xử lý khi hủy thanh toán

## 🔧 Route Chi Tiết

### 1. `/momo_payment` (POST)
```
Input: name, email, phone, address, note (từ form)
Output: Render momo_payment.html với order_id, thông tin khách hàng
```

### 2. `/momo_success/<order_id>` (GET)
```
- Lưu đơn hàng vào Supabase
- Xóa checkout_items khỏi session
- Redirect tới checkout_success.html
```

### 3. `/momo_cancel` (GET)
```
- Xóa session MoMo
- Redirect tới checkout_error.html
```

## 🎨 Giao Diện MoMo Sandbox

### Màu Sắc:
- 🎀 **Primary:** `#a4136f` (MoMo Pink)
- 💜 **Gradient:** `#667eea → #764ba2`
- ✅ **Success:** `#4CAF50` (Green)
- ❌ **Danger:** `#dc3545` (Red)

### Responsive Design:
- Desktop: 2 cột (QR + Info)
- Mobile: 1 cột (QR trên, Info dưới)

## 🧪 Test MoMo

### Bước 1: Thêm Sản Phẩm Vào Giỏ
- Truy cập trang chủ
- Click "Mua ngay" hoặc thêm vào giỏ

### Bước 2: Thanh Toán
- Click "Thanh toán" → Checkout Form
- Nhập thông tin khách hàng
- Chọn "MoMo" → Click "Tiếp tục thanh toán"

### Bước 3: Xem Giao Diện MoMo
- Thấy QR Code, thông tin tài khoản ảo, thông tin đơn hàng
- Thấy đồng hồ đếm ngược 5 phút
- Thử các nút:
  - ✅ Thanh toán thành công
  - 🔄 Đổi phương thức
  - ❌ Hủy thanh toán

### Bước 4: Kiểm Tra Dữ Liệu
- Vào admin → Xem đơn hàng trong Supabase
- Kiểm tra `payment_method = 'momo'`

## ⚙️ Tùy Chỉnh

### Thay Đổi Tài Khoản Ảo:
File: `templates/momo_payment.html`
```html
<p><strong>Số điện thoại:</strong> 0866123456</p>
<p><strong>Tên tài khoản:</strong> Nguyễn Bán Hàng</p>
<p><strong>Số dư:</strong> 50.000.000 VND</p>
```

### Thay Đổi Thời Gian Đếm Ngược:
File: `templates/momo_payment.html` (JavaScript)
```javascript
let timeLeft = 5 * 60; // Thay 5 thành số phút khác
```

### Thêm Xác Thực Thực Tế MoMo:
Sau này, có thể thay `momo_success()` bằng gọi API thực MoMo thay vì route redirect.

## 📱 Các Biến Trong Giao Diện MoMo

| Biến | Giá Trị | Nguồn |
|------|--------|-------|
| `{{ order_id }}` | MOMO-123456 | Tạo ngẫu nhiên |
| `{{ customer_name }}` | Tên KH | Form nhập |
| `{{ customer_phone }}` | Số ĐT | Form nhập |
| `{{ amount }}` | Tổng tiền | Tính từ items |
| `{{ items_count }}` | Số SP | Từ checkout_items |

## 🛡️ Bảo Mật

- ✅ Dữ liệu được lưu vào session
- ✅ Kiểm tra order_id trước khi xử lý
- ✅ Không lưu thông tin thẻ (sandbox)
- ⚠️ Nhớ enable HTTPS khi production

## 📞 Support

Nếu có vấn đề:
1. Kiểm tra console browser (F12) xem lỗi JS
2. Kiểm tra terminal Flask xem error
3. Kiểm tra session có lưu `momo_payment_info` không
4. Kiểm tra Supabase orders table

---

**Chúc bạn sử dụng vui vẻ! 🎉**
