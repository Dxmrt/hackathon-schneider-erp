from flask import Flask, jsonify, request
import sqlite3

# Do not change this line
DB_FILE = "sql_queries/erp.db"

# Connect to SQLite database. Do not change this. Call this function within each of the requested functions.
def get_db_connection(db_file):
    return sqlite3.connect(db_file)

# Initialize Flask app
app = Flask(__name__)

# Endpoint to get all customers
@app.route("/api/customers", methods=["GET"])
def get_customers():
    """ Retrieve all customers """

    conn = get_db_connection(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT customer_id, name, email, phone, address, country FROM Customers")
    customers = cursor.fetchall()

    customer_list = []
    for customer in customers:
        customer_list.append({
            "id": customer[0],
            "name": customer[1],
            "email": customer[2],
            "phone": customer[3],
            "address": customer[4],
            "country": customer[5]
        })

    conn.close()

    if not customer_list:
        return jsonify({"message": "No customers found."}), 404

    return jsonify({"customers": customer_list}), 200


# Endpoint to get a specific customer by ID
@app.route("/api/customers/<int:customer_id>", methods=["GET"])
def get_customer_by_id(customer_id):
    """ Retrieve customer by ID """

    conn = get_db_connection(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT customer_id, name, email, phone, address, country FROM Customers WHERE customer_id = ?", (customer_id,))
    customer = cursor.fetchone()

    conn.close()

    if customer:
        return jsonify({
            "id": customer[0],
            "name": customer[1],
            "email": customer[2],
            "phone": customer[3],
            "address": customer[4],
            "country": customer[5]
        }), 200
    else:
        return jsonify({"message": "Customer not found."}), 404


# Endpoint to get all products
@app.route("/api/products", methods=["GET"])
def get_products():
    """ Retrieve all products """

    conn = get_db_connection(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT product_id, name, price, category FROM Products")
    products = cursor.fetchall()

    product_list = []
    for product in products:
        product_list.append({
            "id": product[0],
            "name": product[1],
            "price": product[2],
            "category": product[3]
        })

    conn.close()

    if not product_list:
        return jsonify({"message": "No products found."}), 404

    return jsonify({"products": product_list}), 200


# Endpoint to create a new order
@app.route("/api/orders", methods=["POST"])
def create_order():
    """ Create a new order """

    # Get the order details from the request body
    data = request.get_json()

    customer_id = data.get("customer_id")
    products = data.get("products")  # Expected to be a list of product_ids and quantities
    order_date = data.get("order_date")
    status = data.get("status", "Pending")

    if not customer_id or not products:
        return jsonify({"error": "Customer ID and products are required."}), 400

    conn = get_db_connection(DB_FILE)
    cursor = conn.cursor()

    # Insert the order into the Orders table
    cursor.execute("INSERT INTO Orders (customer_id, order_date, status) VALUES (?, ?, ?)",
                   (customer_id, order_date, status))
    order_id = cursor.lastrowid

    # Insert the order details into the OrderDetails table
    for product in products:
        product_id = product["product_id"]
        quantity = product["quantity"]
        total_price = product["total_price"]

        cursor.execute("INSERT INTO OrderDetails (order_id, product_id, quantity, total_price) VALUES (?, ?, ?, ?)",
                       (order_id, product_id, quantity, total_price))

    conn.commit()
    conn.close()

    return jsonify({"message": "Order created successfully.", "order_id": order_id}), 201


# Endpoint to get all orders
@app.route("/api/orders", methods=["GET"])
def get_orders():
    """ Retrieve all orders """

    conn = get_db_connection(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT o.order_id, c.name, o.order_date, o.status
        FROM Orders o
        JOIN Customers c ON o.customer_id = c.customer_id
    ''')
    orders = cursor.fetchall()

    order_list = []
    for order in orders:
        order_list.append({
            "order_id": order[0],
            "customer_name": order[1],
            "order_date": order[2],
            "status": order[3]
        })

    conn.close()

    if not order_list:
        return jsonify({"message": "No orders found."}), 404

    return jsonify({"orders": order_list}), 200


# Endpoint to get order details by order ID
@app.route("/api/orders/<int:order_id>", methods=["GET"])
def get_order_details(order_id):
    """ Retrieve details of a specific order """

    conn = get_db_connection(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT od.order_detail_id, p.name, od.quantity, od.total_price
        FROM OrderDetails od
        JOIN Products p ON od.product_id = p.product_id
        WHERE od.order_id = ?
    ''', (order_id,))
    order_details = cursor.fetchall()

    conn.close()

    if order_details:
        order_detail_list = []
        for detail in order_details:
            order_detail_list.append({
                "order_detail_id": detail[0],
                "product_name": detail[1],
                "quantity": detail[2],
                "total_price": detail[3]
            })
        return jsonify({"order_details": order_detail_list}), 200
    else:
        return jsonify({"message": "Order not found."}), 404


# Start the Flask app
if __name__ == "__main__":
    app.run(debug=True)
