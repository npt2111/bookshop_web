from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
from werkzeug.utils import secure_filename

from flask_session import Session
from datetime import timedelta
import os, uuid
import requests
import random
from datetime import datetime
import json
app = Flask(__name__)

# -------------------------
# Supabase setup
# -------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
#  Flask Session setup
# ------------------------
SESSION_DIR = os.path.join(os.getcwd(), ".flask_session")
os.makedirs(SESSION_DIR, exist_ok=True)

app.secret_key = "supersecretkey"
app.config.update(
    SESSION_TYPE="filesystem",
    SESSION_FILE_DIR=SESSION_DIR,
    SESSION_PERMANENT=True,
    SESSION_USE_SIGNER=True,
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False
)
Session(app)

# -------------------------
# Trang chủ
# -------------------------
@app.route("/")
def index():
    search_query = request.args.get("search", "").strip()
    filter_type = request.args.get("type", "")
    price_min = float(request.args.get("min", 0) or 0)
    price_max = float(request.args.get("max", 999999999) or 999999999)
    page = int(request.args.get("page", 1))

    # Lấy dữ liệu từ Supabase
    res = supabase.table("inventory").select("*").execute()
    products = res.data or []
    types = supabase.table("type_book").select("*").execute().data or []

    #  Lọc từ khóa
    if search_query:
        products = [
            p for p in products
            if search_query.lower() in (p.get("product") or "").lower()
            or search_query.lower() in (p.get("author") or "").lower()
        ]

    #  Lọc thể loại
    if filter_type:
        products = [p for p in products if p.get("type") == filter_type]

    # Lọc giá
    products = [p for p in products if price_min <= float(p.get("price") or 0) <= price_max]

    # Phân trang
    per_page = 9
    total_pages = max(1, (len(products) + per_page - 1) // per_page)
    start = (page - 1) * per_page
    end = start + per_page
    products_paginated = products[start:end]

    return render_template(
        "index.html",
        products=products_paginated,
        types=types,
        search_query=search_query,
        filter_type=filter_type,
        price_min=price_min,
        price_max=price_max,
        page=page,
        total_pages=total_pages,
    )


# -------------------------
#  Đặt hàng
# -------------------------
@app.route("/order/<int:product_id>", methods=["GET", "POST"])
def order(product_id):
    product = supabase.table("inventory").select("*").eq("id", product_id).single().execute().data

    if request.method == "POST":
        customer_name = request.form.get("customer_name")
        quantity = int(request.form.get("quantity", 1))
        supabase.table("orders").insert({
            "product_id": product_id,
            "customer_name": customer_name,
            "quantity": quantity
        }).execute()
        return redirect(url_for("index", msg="✅ Đặt hàng thành công!"))

    return render_template("order.html", product=product)


# -------------------------
# Trang admin
# -------------------------
@app.route("/admin")
def admin():
    res = supabase.table("inventory").select("*").order("id", desc=False).execute()
    products = res.data or []
    msg = request.args.get("msg")
    return render_template("admin/product.html", products=products, msg=msg)

@app.route("/admin/product")
def product():
    search = request.args.get("search", "").strip().lower()
    res = supabase.table("inventory").select("*").order("id", desc=False).execute()
    products = res.data or []

    if search:
        products = [
            p for p in products
            if search in (p.get("product") or "").lower()
            or search in (p.get("author") or "").lower()
        ]

    msg = request.args.get("msg")
    return render_template("admin/product.html", products=products, msg=msg)
# -------------------------
#  Thêm sản phẩm
# -------------------------
import time
import os
from werkzeug.utils import secure_filename



@app.route("/admin/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        product = request.form["name"]
        price = request.form["price"]
        quantity = request.form["quantity"]
        author = request.form["author"]
        type_name = request.form["type"]
        description = request.form["description"]
        file = request.files["image_file"]

        image_url = ""
        if file:
            filename = str(int(time.time())) + "_" + secure_filename(file.filename)
            try:
                # ✅ Đọc file thành bytes trước khi upload
                file_bytes = file.read()
                supabase.storage.from_("product-images").upload(filename, file_bytes)

                # ✅ Link ảnh public
                image_url = f"{SUPABASE_URL}/storage/v1/object/public/product-images/{filename}"

            except Exception as e:
                print("❌ Lỗi khi upload ảnh:", e)
                return "Lỗi khi upload ảnh sản phẩm!"

        # ✅ Lưu vào Supabase
        supabase.table("inventory").insert({
            "product": product,
            "price": price,
            "quantity": quantity,
            "author": author,
            "type": type_name,
            "description": description,
            "image_url": image_url
        }).execute()

        return redirect(url_for("admin", msg="✅ Thêm sản phẩm thành công!"))

    types = supabase.table("type_book").select("*").execute().data or []
    return render_template("admin/add_product.html", types=types)

# -------------------------
#  Sửa sản phẩm
# -------------------------

@app.route("/admin/edit/<int:id>", methods=["GET", "POST"])
def edit_product(id):
    types = supabase.table("type_book").select("*").execute().data or []

    if request.method == "POST":
        product = request.form["product"]
        price = request.form["price"]
        quantity = request.form["quantity"]
        author = request.form.get("author")
        description = request.form.get("description")
        book_type = request.form.get("type")
        image_url = request.form.get("old_image_url")  # giữ ảnh cũ nếu không đổi

        file = request.files.get("image_file")
        if file and file.filename:
            # ✅ Tạo tên file unique
            filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"

            # ✅ Upload trực tiếp lên Supabase Storage
            try:
                supabase.storage.from_("product-images").upload(
                    filename, file.read()
                )
                image_url = f"{SUPABASE_URL}/storage/v1/object/public/product-images/{filename}"
            except Exception as e:
                print("❌ Upload ảnh thất bại:", e)
                return "Lỗi upload ảnh!", 500

        # ✅ Cập nhật sản phẩm
        supabase.table("inventory").update({
            "product": product,
            "price": price,
            "quantity": quantity,
            "author": author,
            "description": description,
            "type": book_type,
            "image_url": image_url
        }).eq("id", id).execute()

        return redirect(url_for("admin", msg="✅ Cập nhật sản phẩm thành công!"))

    product = supabase.table("inventory").select("*").eq("id", id).single().execute().data
    return render_template("admin/edit_product.html", product=product, types=types)


# -------------------------
#  Xóa sản phẩm
# -------------------------
@app.route("/admin/delete/<int:id>")
def delete_product(id):
    supabase.table("inventory").delete().eq("id", id).execute()
    return redirect(url_for("admin", msg="🗑️ Xóa sản phẩm thành công!"))


# -------------------------
# Chi tiết sản phẩm
# -------------------------
@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = supabase.table("inventory").select("*").eq("id", product_id).single().execute().data
    return render_template("product_detail.html", product=product)


# -------------------------
# Thêm vào giỏ hàng
# -------------------------
@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    product = supabase.table("inventory").select("*").eq("id", product_id).single().execute().data
    if not product:
        return redirect(url_for("index"))

    session.permanent = True
    cart = session.get("cart", [])

    for item in cart:
        if item["id"] == product_id:
            item["quantity"] += 1
            break
    else:
        cart.append({
            "id": product_id,
            "name": product.get("product"),
            "price": float(product.get("price") or 0),
            "quantity": 1,
            "image_url": product.get("image_url") or "https://via.placeholder.com/120x160?text=No+Image"
        })

    session["cart"] = cart
    session.modified = True
    return redirect(url_for("cart"))


# -------------------------
#  Trang giỏ hàng
# -------------------------
@app.route("/cart")
def cart():
    cart = session.get("cart", [])
    total = sum(item["price"] * item["quantity"] for item in cart)
    return render_template("cart.html", cart=cart, total=total)


# -------------------------
# Cập nhật số lượng AJAX
# -------------------------
@app.route("/update_cart_ajax/<int:product_id>")
def update_cart_ajax(product_id):
    try:
        qty = int(request.args.get("qty", 1))
    except ValueError:
        qty = 1

    if qty < 1:
        qty = 1

    cart = session.get("cart", [])
    for item in cart:
        if item["id"] == product_id:
            item["quantity"] = qty
            break

    session["cart"] = cart
    session.modified = True
    return ("", 204)


# -------------------------
#  Xóa giỏ hàng
# -------------------------
@app.route("/clear_cart")
def clear_cart():
    session.pop("cart", None)
    return redirect(url_for("cart"))


# -------------------------
#  Thanh toán & Bulk actions
# -------------------------
@app.route("/cart_bulk_action", methods=["POST"])
def cart_bulk_action():
    selected_ids = request.form.getlist("selected_ids")
    action = request.form.get("action")
    cart = session.get("cart", [])

    if not selected_ids:
        return redirect(url_for("cart"))

    selected_ids = [int(x) for x in selected_ids]

    if action == "delete":
        cart = [item for item in cart if item["id"] not in selected_ids]
        session["cart"] = cart
        session.modified = True

    elif action == "checkout":
        paid_items = [item for item in cart if item["id"] in selected_ids]
        total_paid = sum(i["price"] * i["quantity"] for i in paid_items)
        cart = [item for item in cart if item["id"] not in selected_ids]
        session["cart"] = cart
        session.modified = True
        return render_template("checkout_success.html", total=total_paid)

    return redirect(url_for("cart"))


# @app.route("/checkout")
# def checkout():
#     session.pop("cart", None)
#     return render_template("checkout_success.html")


# -------------------------
#  Xử lý sau khi điền thông tin thanh toán
# -------------------------

# Chọn sản phẩm để thanh toán
@app.route("/checkout_selected", methods=["POST"])
def checkout_selected():
    selected_ids = request.form.getlist("selected_ids")
    cart = session.get("cart", [])
    selected_items = [item for item in cart if str(item["id"]) in selected_ids]

    if not selected_items:
        return redirect(url_for("cart"))

    #  Lưu tạm sản phẩm được chọn vào session
    session["checkout_items"] = selected_items
    session.modified = True

    total = sum(item["price"] * item["quantity"] for item in selected_items)
    return render_template("checkout_form.html", items=selected_items, total=total)

# Xử lý thanh toán
@app.route("/process_checkout", methods=["POST"])
def process_checkout():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    address = request.form.get("address")
    note = request.form.get("note")

    items = session.get("checkout_items", [])
    if not items:
        return render_template("checkout_error.html", error="Không có sản phẩm nào để thanh toán!")

    total = sum(item["price"] * item["quantity"] for item in items)

    # Tạo order_id ngẫu nhiên 4 số duy nhất
    while True:
        order_id = f"ORD-{random.randint(1000,9999)}"
        exists = supabase.table("orders").select("order_id").eq("order_id", order_id).execute()
        if not exists.data:
            break

    # # Trừ số lượng tồn kho
    # for item in items:
    #     current = supabase.table("inventory").select("quantity").eq("id", item["id"]).single().execute()
    #     new_qty = max(0, current.data["quantity"] - item["quantity"])
    #     supabase.table("inventory").update({"quantity": new_qty}).eq("id", item["id"]).execute()

    # Lưu đơn hàng vào Supabase (cột product phải là JSONB)
    supabase.table("orders").insert({
        "order_id": order_id,
        "name": name,
        "email": email,
        "phone": phone,
        "address": address,
        "note": note,
        "product": items,  # JSON
        "total_amount": total,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    # Gửi webhook về n8n
    try:
        WEBHOOK_URL = "https://n8n.nocodelowcode.id.vn/webhook-test/checkout"
        requests.post(WEBHOOK_URL, json={"order_id": order_id, "customer": {
            "name": name, "email": email, "phone": phone, "address": address, "note": note
        }, "order": {"items": items, "total": total}}, timeout=10)
    except:
        print("⚠️ Gửi webhook thất bại nhưng đơn đã lưu vào Supabase.")

    # Xóa sản phẩm đã checkout ra khỏi giỏ hàng
    cart = session.get("cart", [])
    remaining_cart = [item for item in cart if item not in items]
    session["cart"] = remaining_cart
    session.modified = True
    # Xóa giỏ hàng tạm
    session.pop("checkout_items", None)

    return render_template("checkout_success.html", order_id=order_id, customer=name, total=total)


# -------------------------
#  Quản lý đơn hàng (Admin)
# -------------------------
@app.route("/admin/orders")
def admin_orders():
    res = supabase.table("orders").select("*").order("id", desc=True).execute()
    orders = res.data or []
    return render_template("admin/orders.html", orders=orders)



@app.route("/admin/orders/<order_id>")
def admin_order_detail(order_id):
    res = supabase.table("orders").select("*").eq("order_id", order_id).single().execute()
    order = res.data

    if order and isinstance(order.get("product"), str):
        order["product"] = json.loads(order["product"])  # chuyển từ string JSON sang list

    return render_template("admin/order_detail.html", order=order)


@app.route("/admin/orders/update_status/<order_id>")
def update_order_status(order_id):
    # Lấy order từ Supabase
    res = supabase.table("orders").select("*").eq("order_id", order_id).single().execute()
    order = res.data

    if not order:
        return "Order not found", 404

    # Parse product JSON nếu cần
    products = order.get("product")
    if isinstance(products, str):
        products = json.loads(products)

    # Trừ số lượng trong inventory
    for item in products:
        product_id = item.get("id")
        qty_ordered = item.get("quantity", 0)
        # Lấy tồn kho hiện tại
        res_inv = supabase.table("inventory").select("quantity").eq("id", product_id).single().execute()
        if res_inv.data:
            current_qty = res_inv.data.get("quantity", 0)
            new_qty = max(0, current_qty - qty_ordered)
            supabase.table("inventory").update({"quantity": new_qty}).eq("id", product_id).execute()

    # Cập nhật trạng thái order
    supabase.table("orders").update({"status": "accept"}).eq("order_id", order_id).execute()

    return redirect(url_for("admin_orders"))
# -------------------------
#  Quản lý thể loại
# -------------------------
@app.route("/admin/type")
def admin_type():
    res = supabase.table("type_book").select("*").order("id", desc=False).execute()
    types = res.data or []
    msg = request.args.get("msg")
    return render_template("admin/type.html", types=types, msg=msg)
@app.route("/admin/type/add", methods=["POST"])
def add_type():
    name = request.form.get("name")
    if name:
        supabase.table("type_book").insert({"name": name}).execute()
        return redirect(url_for("admin_type", msg="✅ Thêm thể loại thành công!"))
    return redirect(url_for("admin_type", msg="⚠️ Tên thể loại không được để trống!"))

@app.route("/admin/type/edit/<int:id>", methods=["GET", "POST"])
def edit_type(id):
    # Nếu form được gửi lên
    if request.method == "POST":
        new_name = request.form.get("name")
        if new_name:
            supabase.table("type_book").update({"name": new_name}).eq("id", id).execute()
            return redirect(url_for("admin_type", msg="📝 Cập nhật thể loại thành công!"))
        return redirect(url_for("admin_type", msg="⚠️ Tên thể loại không được để trống!"))

    # Lấy dữ liệu cũ để hiển thị trong form sửa
    t = supabase.table("type_book").select("*").eq("id", id).single().execute().data
    return render_template("admin/edit_type.html", type_item=t)


@app.route("/admin/type/delete/<int:id>")
def delete_type(id):
    supabase.table("type_book").delete().eq("id", id).execute()
    return redirect(url_for("admin_type", msg="🗑️ Xóa thể loại thành công!"))

@app.route("/admin/stats")
def admin_stats():
    # Tổng sản phẩm
    total_products = len(supabase.table("inventory").select("id").execute().data or [])

    # Tổng đơn hàng
    total_orders = len(supabase.table("orders").select("id").execute().data or [])

    # Tổng doanh thu từ đơn hàng đã duyệt
    accepted_orders = supabase.table("orders").select("total_amount").eq("status", "accept").execute().data or []
    total_revenue = sum(o.get("total_amount", 0) for o in accepted_orders)

    # Top 5 sản phẩm bán chạy
    all_orders = supabase.table("orders").select("product").eq("status", "accept").execute().data or []
    sales_count = {}
    for order in all_orders:
        products = order.get("product")
        if isinstance(products, str):
            products = json.loads(products)
        for p in products:
            name = p.get("name")
            qty = p.get("quantity", 0)
            sales_count[name] = sales_count.get(name, 0) + qty

    top_selling = sorted(sales_count.items(), key=lambda x: x[1], reverse=True)[:5]

    return render_template("admin/stats.html",
                           total_products=total_products,
                           total_orders=total_orders,
                           total_revenue=total_revenue,
                           top_selling=top_selling)

# -------------------------
#  Run
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
