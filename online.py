from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor


app = Flask(__name__)
app.secret_key = "secret123"
app.config.from_object(Config)

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template("index.html")

# Registration

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = generate_password_hash(request.form["password"])

        cur = mysql.connection.cursor(DictCursor)
        cur.execute("SELECT id FROM users WHERE email=%s",
                    (email,))
        existing_user = cur.fetchone()
        
        if existing_user:
            cur.close()
            flash("Email already registered.")
            return redirect(url_for("register"))
        
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, password),)
        mysql.connection.commit()
        cur.close()

        flash("Registration successful!")
        return redirect(url_for("login"))
    
    return render_template("register.html")

# Login

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        cur = mysql.connection.cursor(DictCursor)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()

        print("User from DB:", user)

        if user:
            print("Stored Password:", user["password"])
            print("Entered Password:", password)
            print("Password Match:", check_password_hash(user["password"], password))

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            flash("Login successful!")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password")

    return render_template("login.html")

# Dashboard

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))
    
    return render_template("dashboard.html", username=session["username"])

# Logout

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("index"))

#Profile Section

@app.route("/profile")
def profile():

    if "user_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()

    cur.execute("SELECT username, email, phone, address FROM users WHERE id=%s", (session["user_id"],))

    user = cur.fetchone()

    cur.close()

    return render_template("profile.html", user=user)

# Update Profile Route

@app.route("/update_profile", methods=["GET","POST"])
def update_profile():

    if "user_id" not in session:
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()

    if request.method == "POST":

        username = request.form["username"]
        phone = request.form["phone"]
        address = request.form["address"]

        cur.execute("UPDATE users SET username=%s, phone=%s, address=%s WHERE id=%s",
                    (username, phone, address, session["user_id"]))
        
        mysql.connection.commit()

        session["username"] = username

        flash("Profile updated successfully!")

        cur.close()

        return redirect(url_for("profile"))
    
    cur.execute("SELECT username, email, phone, address FROM users WHERE id=%s",
                (session["user_id"],))
    user = cur.fetchone()
    cur.close()

    return render_template("update_profile.html", user=user)

# Change Password

@app.route("/change_password", methods=["GET","POST"])
def change_password():

    if "user_id" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        cur = mysql.connection.cursor()

        cur.execute("SELECT password FROM users WHERE id=%s",
                    (session["user_id"],))
        
        user = cur.fetchone()

        if not check_password_hash(user["password"], current_password):
            flash("Current Password is incorrect.")
            cur.close()
            return redirect(url_for("change_password"))
        
        if new_password != confirm_password:
            flash("Passwords don not match.")
            cur.close()
            return redirect(url_for("change_password"))
        
        hashed = generate_password_hash(new_password)

        cur.execute("UPDATE users SET password=%s WHERE id=%s",
                    (hashed, session["user_id"]))
        
        mysql.connection.commit()

        cur.close()

        flash("Password changed successfully.")

        return redirect(url_for("profile"))
    
    return render_template("change_password.html")

# Admin Section

@app.route("/admin")
def admin_dashboard():

    if "user_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))
    
    if session.get("role") != "admin":
        flash("Access denied.")
        return redirect(url_for("dashboard"))
    
    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders")
    total_orders = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM products")
    total_products = cur.fetchone()[0]

    cur.execute("SELECT IFNULL(SUM(total),0) FROM orders")
    total_sales = cur.fetchone()[0]
    cur.close()

    return render_template("admin_dashboard.html", total_users=total_users,total_products=total_products,total_orders=total_orders,total_sales=total_sales)

# Category Management

@app.route("/categories")
def categories():

    if "user_id" not in session:
        return redirect(url_for("login"))
    
    if session.get("role") != "admin":
        flash("Access denied")
        return redirect(url_for("dashboard"))
    
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM categories")

    categories = cur.fetchall()
    cur.close()

    return render_template("categories.html",categories=categories)

# Add Category

@app.route("/add_category", methods=["GET","POST"])
def add_category():

    if "user_id" not in session:
        return redirect(url_for("login"))
    
    if session.get("role") != "admin":
        flash("Access Denied.")
        return redirect(url_for("dashboard"))
    
    if request.method == "POST":
        category = request.form["category"]

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO categories(category_name) VALUES(%s)",
                    (category,))
        mysql.connection.commit()
        cur.close()

        flash("Category added successfully.")

        return redirect(url_for("categories"))
    
    return render_template("add_category.html")

# Edit Category

@app.route("/edit_category/<int:id>", methods=["GET","POST"])
def edit_category(id):

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))
    
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM categories WHERE id=%s",
                (id,))
    
    category = cur.fetchone()

    if request.method == "POST":
        new_name = request.form["category"]

        cur.execute("UPDATE categories SET category_name=%s WHERE id=%s",
                    (new_name, id))
        
        mysql.connection.commit()

        cur.close()

        flash("Category updated.")

        return redirect(url_for("categories"))
    
    cur.close()

    return render_template("edit_category.html", category=category)

# Delete Category

@app.route("/delete_category/<int:id>")
def delete_category(id):

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))
    
    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM categories WHERE id=%s",
                (id,))
    
    mysql.connection.commit()

    cur.close()

    flash("Category deleted.")

    return redirect(url_for("categories"))


# Add Product

@app.route("/add_product", methods=["GET", "POST"])
def add_product():

    if "user_id" not in session:
        flash("please login first.")
        return redirect(url_for("login"))
    
    if request.method == "POST":

        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]
        stock = request.form["stock"]

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO products (name, description, price, stock) VALUES (%s, %s, %s, %s)",
                (name, description, price, stock))
        
        mysql.connection.commit()

        cur.close()

        flash("Product added successfully!")
        return redirect(url_for("shop"))
    
    return render_template("add_product.html")

# Read Products

@app.route("/products")
def products():

    if "user_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()

    return render_template("read_product.html", products=products)

# Update Product

@app.route("/edit_product/<int:id>", methods=["GET", "POST"])
def edit_product(id):

    if "user_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM products WHERE id=%s", (id,))
    product = cur.fetchone()

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]
        stock = request.form["stock"]

        cur.execute("UPDATE products SET name=%s, description=%s, price=%s, stock=%s WHERE id=%s",
                    (name, description, price, stock, id))
        
        mysql.connection.commit()
        cur.close()

        flash("Product updated successfully!")
        return redirect(url_for("products"))
    
    cur.close()
    return render_template("edit_product.html", product=product)

# Delete Product

@app.route("/delete_product/<int:id>")
def delete_product(id):

    if "user_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM products WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    flash("Product deleted successfully!")
    return redirect(url_for("products"))

# Admin Order Management

@app.route("/admin/orders")
def admin_orders():

    if session.get("role") != "admin":
        flash("Access denied.")
        return redirect(url_for("dashboard"))
    
    cur = mysql.connection.cursor()

    cur.execute("SELECT orders.id, users.username, orders.total, orders.status, orders.payment_method, orders.created_at FROM orders JOIN users ON users.id=orders.user_id ORDER BY orders.created_at DESC")

    orders = cur.fetchall()

    cur.close()

    return render_template("admin_orders.html", orders=orders)

# View Order Section

@app.route("/admin/order/<int:id>")
def admin_order_details(id):

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))
    
    cur = mysql.connection.cursor()

    cur.execute("SELECT products.name, order_items.quantity, order_items.price FROM order_items JOIN products ON products.id = order_items.product_id WHERE order_items.order_id=%s", (id,))

    items = cur.fetchall()

    cur.close()

    return render_template("admin_order_details.html", items=items, order_id=id)

# Order Status Update

@app.route("/admin/update_order/<int:id>", methods=["GET","POST"])
def update_order(id):

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))
    
    cur = mysql.connection.cursor()

    if request.method == "POST":

        status = request.form["status"]

        cur.execute("UPDATE orders SET status=%s WHERE id=%s",
                    (status,id))
        
        mysql.connection.commit()

        cur.close()

        flash("Order status updated.")

        return redirect(url_for("admin_orders"))
    
    cur.execute("SELECT * FROM orders WHERE id=%s", (id,))

    order = cur.fetchone()

    cur.close()
    return render_template("update_order.html", order=order)


# Shopping section

@app.route("/shop")
def shop():

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()

    return render_template("shop.html", products=products)

# Product Details

@app.route("/products/<int:id>")
def product_detail(id):

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM products WHERE id=%s", (id,))
    product = cur.fetchone()
    cur.close()

    return render_template("product_details.html", product=product)

# Add to Wishlist

@app.route("/add_wishlist/<int:id>")
def add_wishlist(id):

    if "user_id" not in session:
        flash("Please login")
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM wishlist WHERE user_id=%s AND product_id=%s",
                (session["user_id"], id))
    
    existing = cur.fetchone()

    if existing:
        flash("Product already in wishlist.")
    else:
        cur.execute("INSERT INTO wishlist(user_id, product_id) VALUES(%s,%s)",
                    (session["user_id"], id))
        
        mysql.connection.commit()
        flash("Added to wishlist.")

    cur.close()

    return redirect(url_for("shop"))
    
# Show Wishlist

@app.route("/wishlist")
def wishlist():

    if "user_id" not in session:
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()

    cur.execute("SELECT wishlist.id, products.id As product_id, products.name, products.price, products.image FROM wishlist JOIN products ON wishlist.product_id=products.id WHERE wishlist.user_id=%s",
                (session["user_id"],))
    
    products = cur.fetchall()

    cur.close()

    return render_template("wishlist.html", products=products)

# Remove Wishlist

@app.route("/remove_wishlist/<int:id>")
def remove_wishlist(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM wishlist WHERE user_id=%s AND product_id=%s",
                (session["user_id"], id))
    
    mysql.connection.commit()

    cur.close()

    flash("Removed successfully!")

    return redirect(url_for("wishlist"))

# Move to cart section

@app.route("/move_to_cart/<int:id>")
def move_to_cart(id):

    if "user_id" not in session:
        return redirect(url_for("login"))
    
    if "cart" not in session:
        session["cart"] = []

    if id not in session["cart"]:
        session["cart"].append(id)

    session.modified = True

    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM wishlist WHERE user_id=%s AND product_id=%s", (session["user_id"], id))

    mysql.connection.commit()

    cur.close()

    flash("Moved to cart.")

    return redirect(url_for("wishlist"))


# Cart System

@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):

    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(id)
    session.modified = True

    flash("Added to cart!")

    return redirect(url_for("shop"))

# View Cart

@app.route("/cart")
def cart():
    cart_ids = session.get("cart", [])

    cur = mysql.connection.cursor()

    if cart_ids:
        format_strings = ','.join(['%s'] * len(cart_ids))

        cur.execute(f"SELECT * FROM products WHERE id IN ({format_strings})", tuple(cart_ids))
        products = cur.fetchall()
    else:
        products = []

    cur.close()

    return render_template("cart.html", products=products)

# Remove prouct

@app.route("/remove_product/<int:id>")
def remove_product(id):

    cart = session.get("cart", [])

    if id in cart:
        cart.remove(id)

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("cart"))

# Checkout System
 
@app.route("/checkout")
def checkout():
     if "user_id" not in session:
         return redirect (url_for("login"))
     
     session["cart"] = []
     flash("Order placed successfully!")
     return redirect(url_for("shop"))

# My Order section

@app.route("/my_orders")
def my_orders():

    if "user_id" not in session:
        flash("Please login")
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()

    cur.execute("SELECT id, total, status, payment_method, created_at FROM orders WHERE user_id=%s ORDER BY created_at DESC",
                (session["user_id"],))
    
    orders = cur.fetchall()

    cur.close()

    return render_template("my_orders.html", orders=orders)

# Order Details

@app.route("/order_details/<int:id>")
def order_details(id):

    if "user_id" not in session:
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()

    cur.execute("SELECT products.name, order_items.quantity, order_items.price FROM order_items"
    "JOIN products ON products.id=order_items.product_id WHERE order_items.order_id=%s", (id,))

    items = cur.fetchall()

    cur.close()

    return render_template("order_details.html", items=items)

# Order Confirmation

@app.route("/order_confirmation/<int:order_id>")
def order_confirmation(order_id):

    if "user_id" not in session:
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()

    cur.execute("SELECT id, total, shipping_charges, phone, payment_method, created_at FROM orders WHERE id=%s AND user_id=%s",
                (order_id, session["user_id"]))
    
    order = cur.fetchone()
    
    # Products in the order:
    cur.execute("SELECT products.name, order_items.quantity, order_items.price FROM order_items " \
    "JOIN products ON products.id=order_items.product_id WHERE order_items.order_id=%s",
    (order_id,))

    items = cur.fetchall()
    cur.close()

    return render_template("order_confirmation.html", order=order, items=items)

# Search Products

@app.route("/search")
def search():

    keyword = request.args.get("q")

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM products WHERE name LIKE %s",
                ("%" + keyword + "%",))
    products = cur.fetchall()

    cur.close()

    return render_template("shop.html", products=products)


if __name__ == "__main__":
    app.run(debug=True)
