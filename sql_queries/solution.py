import sqlite3
from contextlib import closing

DB_FILE = "sql_queries/erp.db"

def get_db_connection(db_file):
    return sqlite3.connect(db_file)

def execute_query(db_file, query, params=()):
    """Executes a given SQL query within a database connection."""
    with closing(get_db_connection(db_file)) as conn, closing(conn.cursor()) as cursor:
        cursor.execute(query, params)
        conn.commit()

def fetch_one(db_file, query, params=()):
    """Fetches a single result from a SQL query."""
    with closing(get_db_connection(db_file)) as conn, closing(conn.cursor()) as cursor:
        cursor.execute(query, params)
        return cursor.fetchone()[0]

def get_top_selling_products(db_file):
    execute_query(db_file, "DROP TABLE IF EXISTS TopSellingProducts")
    execute_query(db_file, """
        CREATE TABLE TopSellingProducts (
            category TEXT,
            name TEXT,
            total_sales REAL,
            sales_rank INTEGER
        )
    """)
    execute_query(db_file, """
        WITH ProductSales AS (
            SELECT p.category, p.name, SUM(od.quantity) AS total_quantity,
                RANK() OVER (PARTITION BY p.category ORDER BY SUM(od.quantity) DESC) AS sales_rank
            FROM Products p
            JOIN OrderDetails od ON p.product_id = od.product_id
            GROUP BY p.category, p.name
        )
        INSERT INTO TopSellingProducts (category, name, total_sales, sales_rank)
        SELECT category, name, ROUND(total_quantity, 2), sales_rank
        FROM ProductSales WHERE sales_rank <= 3
    """)

def get_late_deliveries(db_file):
    return fetch_one(db_file, """
        SELECT ROUND(
            CASE WHEN COUNT(*) > 0 THEN
                (SUM(CASE WHEN JULIANDAY(delivery_date) - JULIANDAY(order_date) > 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(*))
            ELSE 0 END, 2)
        FROM Orders WHERE status = 'Delivered' AND delivery_date IS NOT NULL
    """) or 0.0

def get_customer_sales_performance(db_file):
    execute_query(db_file, "DROP TABLE IF EXISTS CustomerSalesPerformance")
    execute_query(db_file, """
        CREATE TABLE CustomerSalesPerformance (
            customer_id INTEGER,
            total_orders INTEGER,
            total_revenue REAL,
            avg_order_value REAL,
            revenue_rank INTEGER,
            customer_category TEXT
        )
    """)
    execute_query(db_file, """
        WITH CustomerRevenue AS (
            SELECT c.customer_id, COUNT(o.order_id) AS total_orders, COALESCE(SUM(od.total_price), 0) AS total_revenue
            FROM Customers c
            LEFT JOIN Orders o ON c.customer_id = o.customer_id
            LEFT JOIN OrderDetails od ON o.order_id = od.order_id
            GROUP BY c.customer_id HAVING total_orders > 0
        ),
        RevenueStats AS (SELECT AVG(total_revenue) AS avg_revenue FROM CustomerRevenue),
        CustomerMetrics AS (
            SELECT cr.customer_id, cr.total_orders, ROUND(cr.total_revenue, 2) AS total_revenue,
                ROUND(CASE WHEN cr.total_orders > 0 THEN cr.total_revenue / cr.total_orders ELSE 0 END, 2) AS avg_order_value,
                RANK() OVER (ORDER BY cr.total_revenue DESC) AS revenue_rank,
                CASE WHEN cr.total_revenue > (SELECT avg_revenue FROM RevenueStats) THEN 'High-Value Customer' ELSE 'Regular Customer' END AS customer_category
            FROM CustomerRevenue cr
        )
        INSERT INTO CustomerSalesPerformance SELECT * FROM CustomerMetrics
    """)

def get_sales_forecast(db_file):
    execute_query(db_file, "DROP TABLE IF EXISTS SalesForecast")
    execute_query(db_file, """
        CREATE TABLE SalesForecast (
            product_id INTEGER,
            product_name TEXT,
            stock_quantity INTEGER,
            sales_last_3_months INTEGER,
            estimated_months_before_stockout INTEGER,
            stock_rank INTEGER
        )
    """)
    current_date = fetch_one(db_file, "SELECT date('now')")
    execute_query(db_file, f"""
        WITH ProductStock AS (
            SELECT p.product_id, p.name AS product_name, SUM(i.stock_quantity) AS stock_quantity
            FROM Products p JOIN Inventory i ON p.product_id = i.product_id
            GROUP BY p.product_id
        ),
        ProductSales AS (
            SELECT p.product_id, SUM(od.quantity) AS sales_quantity
            FROM Products p
            JOIN OrderDetails od ON p.product_id = od.product_id
            JOIN Orders o ON od.order_id = o.order_id
            WHERE o.order_date >= date('{current_date}', '-3 months')
            GROUP BY p.product_id
        ),
        StockForecast AS (
            SELECT ps.product_id, ps.product_name, ps.stock_quantity,
                COALESCE(psa.sales_quantity, 0) AS sales_last_3_months,
                CASE WHEN COALESCE(psa.sales_quantity, 0) > 0
                    THEN CAST(ROUND(ps.stock_quantity / (psa.sales_quantity / 3.0)) AS INTEGER) ELSE NULL END AS estimated_months_before_stockout
            FROM ProductStock ps LEFT JOIN ProductSales psa ON ps.product_id = psa.product_id
        )
        INSERT INTO SalesForecast
        SELECT sf.*, RANK() OVER (ORDER BY sf.stock_quantity DESC) AS stock_rank FROM StockForecast sf
    """)

def get_discount_analysis(db_file):
    execute_query(db_file, "DROP TABLE IF EXISTS DiscountAnalysis")
    execute_query(db_file, """
        CREATE TABLE DiscountAnalysis (
            order_id INTEGER,
            total_revenue REAL,
            total_cost REAL,
            profit REAL,
            profit_margin_percentage REAL,
            discount_percentage REAL,
            profitability_rank INTEGER
        )
    """)
    execute_query(db_file, """
        WITH OrderMetrics AS (
            SELECT od.order_id, SUM(od.total_price) AS actual_price,
                SUM(p.price * od.quantity) AS list_price,
                SUM(p.price * od.quantity * 0.7) AS cost_price
            FROM OrderDetails od
            JOIN Products p ON od.product_id = p.product_id
            GROUP BY od.order_id
        ),
        OrderAnalysis AS (
            SELECT order_id, ROUND(actual_price, 2) AS total_revenue,
                ROUND(cost_price, 2) AS total_cost,
                ROUND(actual_price - cost_price, 2) AS profit,
                ROUND(CASE WHEN actual_price > 0 THEN ((actual_price - cost_price) / actual_price) * 100 ELSE 0 END, 2) AS profit_margin_percentage,
                ROUND(CASE WHEN list_price > 0 THEN ((list_price - actual_price) / list_price) * 100 ELSE 0 END, 2) AS discount_percentage
            FROM OrderMetrics
        )
        INSERT INTO DiscountAnalysis
        SELECT *, RANK() OVER (ORDER BY profit DESC) AS profitability_rank FROM OrderAnalysis
    """)
