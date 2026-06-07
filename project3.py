import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL
# Load environment variables from .env file
load_dotenv()

# =====================================================
# CONFIGURATION
# =====================================================

EXCEL_FILE = "Dataset_for_Data_Analytics3.xlsx"

MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
TABLE_NAME = "orders"
DATABASE_NAME = "ecommerce_analysis"

connection_url = URL.create(
    drivername="mysql+pymysql",
    username=MYSQL_USER,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    database=DATABASE_NAME
)

# =====================================================
# CREATE MYSQL CONNECTION
# =====================================================
engine_no_db = create_engine(connection_url)

with engine_no_db.connect() as conn:
    conn.exec_driver_sql(
        f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"
    )

db_url = URL.create(
    drivername="mysql+pymysql",
    username=MYSQL_USER,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    database=DATABASE_NAME
)

engine = create_engine(db_url)

# =====================================================
# LOAD EXCEL
# =====================================================

print("Loading Excel file...")

df = pd.read_excel(EXCEL_FILE)

print("\nDataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

# =====================================================
# UPLOAD TO MYSQL
# =====================================================

print("\nUploading data to MySQL...")

df.to_sql(
    TABLE_NAME,
    con=engine,
    if_exists="replace",
    index=False
)

print("Data uploaded successfully!")

# =====================================================
# OUTPUT DIRECTORY
# =====================================================

os.makedirs("outputs", exist_ok=True)

# =====================================================
# HELPER FUNCTION
# =====================================================

def run_query(name, query):
    print(f"\n{name}")
    print("-" * 50)

    result = pd.read_sql(query, engine)

    print(result.head())

    result.to_csv(
        f"outputs/{name}.csv",
        index=False
    )

    return result

# =====================================================
# PROJECT QUERIES
# =====================================================

queries = {

    "01_total_orders":
    """
    SELECT COUNT(*) AS TotalOrders
    FROM orders
    """,

    "02_total_customers":
    """
    SELECT COUNT(DISTINCT CustomerID) AS TotalCustomers
    FROM orders
    """,

    "03_total_products":
    """
    SELECT COUNT(DISTINCT Product) AS TotalProducts
    FROM orders
    """,

    "04_total_revenue":
    """
    SELECT SUM(TotalPrice) AS TotalRevenue
    FROM orders
    """,

    "05_average_order_value":
    """
    SELECT AVG(TotalPrice) AS AverageOrderValue
    FROM orders
    """,

    "06_high_value_orders":
    """
    SELECT *
    FROM orders
    WHERE TotalPrice > 2000
    """,

    "07_delivered_orders":
    """
    SELECT *
    FROM orders
    WHERE OrderStatus='Delivered'
    """,

    "08_orders_by_payment":
    """
    SELECT
        PaymentMethod,
        COUNT(*) AS Orders
    FROM orders
    GROUP BY PaymentMethod
    ORDER BY Orders DESC
    """,

    "09_revenue_by_payment":
    """
    SELECT
        PaymentMethod,
        SUM(TotalPrice) AS Revenue
    FROM orders
    GROUP BY PaymentMethod
    ORDER BY Revenue DESC
    """,

    "10_orders_by_status":
    """
    SELECT
        OrderStatus,
        COUNT(*) AS Orders
    FROM orders
    GROUP BY OrderStatus
    ORDER BY Orders DESC
    """,

    "11_product_order_count":
    """
    SELECT
        Product,
        COUNT(*) AS OrderCount
    FROM orders
    GROUP BY Product
    ORDER BY OrderCount DESC
    """,

    "12_product_revenue":
    """
    SELECT
        Product,
        SUM(TotalPrice) AS Revenue
    FROM orders
    GROUP BY Product
    ORDER BY Revenue DESC
    """,

    "13_average_product_price":
    """
    SELECT
        Product,
        AVG(UnitPrice) AS AveragePrice
    FROM orders
    GROUP BY Product
    ORDER BY AveragePrice DESC
    """,

    "14_top_5_products":
    """
    SELECT
        Product,
        SUM(TotalPrice) AS Revenue
    FROM orders
    GROUP BY Product
    ORDER BY Revenue DESC
    LIMIT 5
    """,

    "15_repeat_customers":
    """
    SELECT
        CustomerID,
        COUNT(*) AS OrdersPlaced
    FROM orders
    GROUP BY CustomerID
    HAVING COUNT(*) > 1
    ORDER BY OrdersPlaced DESC
    """,

    "16_referral_analysis":
    """
    SELECT
        ReferralSource,
        COUNT(*) AS Orders,
        SUM(TotalPrice) AS Revenue
    FROM orders
    GROUP BY ReferralSource
    ORDER BY Revenue DESC
    """,

    "17_coupon_usage":
    """
    SELECT
        CouponCode,
        COUNT(*) AS UsageCount
    FROM orders
    GROUP BY CouponCode
    ORDER BY UsageCount DESC
    """,

    "18_average_cart_size":
    """
    SELECT
        AVG(ItemsInCart) AS AverageCartSize
    FROM orders
    """,

    "19_top_10_orders":
    """
    SELECT
        OrderID,
        Product,
        CustomerID,
        TotalPrice
    FROM orders
    ORDER BY TotalPrice DESC
    LIMIT 10
    """,

    "20_monthly_sales":
    """
    SELECT
        YEAR(Date) AS Year,
        MONTH(Date) AS Month,
        COUNT(*) AS Orders,
        SUM(TotalPrice) AS Revenue
    FROM orders
    GROUP BY YEAR(Date), MONTH(Date)
    ORDER BY Year, Month
    """
}

# =====================================================
# EXECUTE ALL QUERIES
# =====================================================

for name, query in queries.items():
    run_query(name, query)

print("\nAll analysis completed.")
print("Results saved in outputs/ folder.")