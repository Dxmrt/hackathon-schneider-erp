import sqlite3

DB_FILE = "sql_queries/erp.db"


# Connect to SQLite database. Do not change this. Call this function within each of the requested functions.
def get_db_connection(db_file):
    return sqlite3.connect(db_file)


# Query 1: Top selling products
def get_top_selling_products(db_file):
    """
    Create a new table in the database schema named "TopSellingProducts" with the top 3 selling products in each category.
    Return the table with the following schema:

    |-----------------|-------------|--------------------|------------------|
    | category (text) | name (text) | total_sales (real) | sales_rank (int) |
    |-----------------|-------------|--------------------|------------------|

    """
    pass


# Query 2:  Percentage of Orders That Were Delivered Late
def get_late_deliveries(db_file):
    """
    Return the percentage of late deliveries. Consider a policy of maximuim 5 day delivery.

    """
    pass


# Query 3: Customer Sales perfomance
def get_customer_sales_performance(db_file):
    """
    Create a new table in the database schema named "CustomerSalesPerformance".
    Flag the customer as "High-Value Customer" if their individual total revenue is higher than the average customer total revenue. Otherwise as "Regular Customer"
    Add also some other stats.
    Return the table with the following schema:

    |-------------------|--------------------|----------------------|------------------------|--------------------|--------------------------|
    | customer_id (int) | total_orders (int) | total_revenue (real) | avg_order_value (real) | revenue_rank (int) | customer_category (text) |
    |-------------------|--------------------|----------------------|------------------------|--------------------|--------------------------|

    """
    pass


# Query 4: Inventory & Sales Forecast Table
def get_sales_forecast(db_file):
    """
    Create a new table in the database schema named "SalesForecast" based on the last 3 months of purchases
    Return the table with the following schema:

    |------------------|---------------------|----------------------|---------------------------|----------------------------------------|------------------|
    | product_id (int) | product_name (text) | stock_quantity (int) | sales_last_3_months (int) | estimated_months_before_stockout (int) | stock_rank (int) |
    |------------------|---------------------|----------------------|---------------------------|----------------------------------------|------------------|

    """
    pass


# Query 5: Order Profitability & Discount Analysis
def get_discount_analysis(db_file):
    """
    Create a new table in the database schema named "DiscountAnalysis" to provide a summary of the discounts applied per order and the profit obtained.
    Return the table with the following schema:

    |----------------|----------------------|-------------------|---------------|---------------------------------|----------------------------|--------------------------|
    | order_id (int) | total_revenue (real) | total_cost (real) | profit (real) | profit_margin_percentage (real) | discount_percentage (real) | profitability_rank (int) |
    |----------------|----------------------|-------------------|---------------|---------------------------------|----------------------------|--------------------------|
    """
    pass


if __name__ == "__main__":
    get_top_selling_products(DB_FILE)
    print(get_late_deliveries(DB_FILE))
    get_customer_sales_performance(DB_FILE)
    get_sales_forecast(DB_FILE)
    get_discount_analysis(DB_FILE)
