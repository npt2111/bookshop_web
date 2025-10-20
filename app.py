from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
from werkzeug.utils import secure_filename
from flask_session import Session
from datetime import timedelta
import os, uuid
import requests
import random
from datetime import datetime

app = Flask(__name__)

# -------------------------
# 🔧 Supabase setup
# -------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# 🔧 Flask Session setup
# -------------------------
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

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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

    # 🧠 Lọc từ khóa
    if search_query:
        products = [
            p for p in products
            if search_query.lower() in (p.get("product") or "").lower()
            or search_query.lower() in (p.get("author") or "").lower()
        ]

    # 🧩 Lọc thể loại
    if filter_type:
        products = [p for p in products if p.get("type") == filter_type]

    # 💰 Lọc giá
    products = [p for p in products if price_min <= float(p.get("price") or 0) <= price_max]

    # 📄 Phân trang
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
# 🛒 Đặt hàng
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
# 👑 Trang admin
# -------------------------
@app.route("/admin")
def admin():
    res = supabase.table("inventory").select("*").order("id", desc=False).execute()
    products = res.data or []
    msg = request.args.get("msg")
    return render_template("admin.html", products=products, msg=msg)

@app.route("/admin/product")
def product():
    res = supabase.table("inventory").select("*").order("id", desc=False).execute()
    products = res.data or []
    msg = request.args.get("msg")
    return render_template("admin.html", products=products, msg=msg)
# -------------------------
# 🟠 Thêm sản phẩm
# -------------------------
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
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            with open(file_path, "rb") as f:
                supabase.storage.from_("product-images").upload(filename, f)
            image_url = f"{SUPABASE_URL}/storage/v1/object/public/product-images/{filename}"

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
    return render_template("add_product.html", types=types)


# -------------------------
# ✏️ Sửa sản phẩm
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
        file = request.files.get("image_file")
        image_url = request.form.get("old_image_url")

        if file and file.filename:
            filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            with open(path, "rb") as f:
                supabase.storage.from_("product-images").upload(filename, f)
            image_url = f"{SUPABASE_URL}/storage/v1/object/public/product-images/{filename}"

        supabase.table("inventory").update({
            "product": product,
            "price": price,
            "quantity": quantity,
            "author": author,
            "description": description,
            "type": book_type,
            "image_url": image_url
        }).eq("id", id).execute()

        return redirect(url_for("admin", msg="📝 Cập nhật sản phẩm thành công!"))

    product = supabase.table("inventory").select("*").eq("id", id).single().execute().data
    return render_template("edit_product.html", product=product, types=types)


# -------------------------
# 🗑️ Xóa sản phẩm
# -------------------------
@app.route("/admin/delete/<int:id>")
def delete_product(id):
    supabase.table("inventory").delete().eq("id", id).execute()
    return redirect(url_for("admin", msg="🗑️ Xóa sản phẩm thành công!"))


# -------------------------
# 🔍 Chi tiết sản phẩm
# -------------------------
@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = supabase.table("inventory").select("*").eq("id", product_id).single().execute().data
    return render_template("product_detail.html", product=product)


# -------------------------
# 🛒 Thêm vào giỏ hàng
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
# 🧺 Trang giỏ hàng
# -------------------------
@app.route("/cart")
def cart():
    cart = session.get("cart", [])
    total = sum(item["price"] * item["quantity"] for item in cart)
    return render_template("cart.html", cart=cart, total=total)


# -------------------------
# 🔄 Cập nhật số lượng AJAX
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
# 🧹 Xóa giỏ hàng
# -------------------------
@app.route("/clear_cart")
def clear_cart():
    session.pop("cart", None)
    return redirect(url_for("cart"))


# -------------------------
# 🧾 Thanh toán & Bulk actions
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
# ✅ Xử lý sau khi điền thông tin thanh toán
# -------------------------
import requests
from flask import jsonify

# ⚙️ Route hiển thị form thanh toán (hiển thị sản phẩm đã chọn)
@app.route("/checkout_selected", methods=["POST"])
def checkout_selected():
    selected_ids = request.form.getlist("selected_ids")
    cart = session.get("cart", [])
    selected_items = [item for item in cart if str(item["id"]) in selected_ids]

    if not selected_items:
        return redirect(url_for("cart"))

    total = sum(item["price"] * item["quantity"] for item in selected_items)

    return render_template("checkout_form.html", items=selected_items, total=total)


# ⚙️ Route xử lý form thanh toán → gửi webhook n8n
@app.route("/process_checkout", methods=["POST"])
def process_checkout():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    address = request.form.get("address")
    note = request.form.get("note")

    # Lấy giỏ hàng đã chọn lưu trong session checkout_temp
    items = session.get("checkout_items", [])
    if not items:
        return render_template("checkout_error.html", error="Không có sản phẩm nào để thanh toán!")

    total = sum(item["price"] * item["quantity"] for item in items)

    # ✅ Random order_id 4 số + kiểm tra trùng trong Supabase
    while True:
        random_num = random.randint(1000, 9999)
        order_id = f"ORD-{random_num}"
        exists = supabase.table("orders").select("order_id").eq("order_id", order_id).execute()
        if not exists.data:  # không trùng
            break

    # ✅ Lưu vào Supabase
    supabase.table("orders").insert({
        "order_id": order_id,
        "name": name,
        "email": email,
        "phone": phone,
        "address": address,
        "note": note,
        "product": items,
        "total_amount": total,
        "created_at": datetime.utcnow().isoformat(),
        "status": "pending"
    }).execute()

    # ✅ Gửi qua Webhook cho n8n
    payload = {
        "order_id": order_id,
        "customer": {
            "name": name,
            "email": email,
            "phone": phone,
            "address": address,
            "note": note
        },
        "order": {
            "items": items,
            "total": total
        }
    }

    try:
        WEBHOOK_URL = "https://n8n.nocodelowcode.id.vn/webhook-test/checkout"
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print("⚠️ Không gửi được đến n8n nhưng vẫn lưu đơn:", e)

    # ✅ Xóa giỏ tạm chỉ chứa sản phẩm được checkout
    session.pop("checkout_items", None)

    return render_template("checkout_success.html", order_id=order_id, customer=name, total=total)


# -------------------------
# 📦 Quản lý đơn hàng (Admin)
# -------------------------
@app.route("/admin/orders")
def admin_orders():
    res = supabase.table("orders").select("*").order("created_at", desc=True).execute()
    orders = res.data or []
    return render_template("admin/orders.html", orders=orders)


@app.route("/admin/orders/update_status/<order_id>")
def update_order_status(order_id):
    supabase.table("orders").update({"status": "accepted"}).eq("order_id", order_id).execute()
    return redirect(url_for("admin_orders"))
@app.route("/admin/orders/<order_id>")
def admin_order_detail(order_id):
    res = supabase.table("orders").select("*").eq("order_id", order_id).single().execute()
    order = res.data
    return render_template("admin/order_detail.html", order=order)

# -------------------------
# 🚀 Run
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
