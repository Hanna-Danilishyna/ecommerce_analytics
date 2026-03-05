# import pandas as pd
# from sqlalchemy import create_engine, text

# # --------------------------
# # Connect to the db
# # --------------------------
# engine = create_engine('postgresql+psycopg2://nana:Ha-KI-248@localhost:5432/ecommerce_analytics')

# # --------------------------
# # Create tables (if doesn't exist)
# # --------------------------
# tables_sql = """
# CREATE TABLE IF NOT EXISTS customers (
#     customer_id TEXT PRIMARY KEY,
#     customer_unique_id TEXT,
#     customer_zip_code_prefix INT,
#     customer_city TEXT,
#     customer_state TEXT
# );

# CREATE TABLE IF NOT EXISTS sellers (
#     seller_id TEXT PRIMARY KEY,
#     seller_zip_code_prefix INT,
#     seller_city TEXT,
#     seller_state TEXT
# );

# CREATE TABLE IF NOT EXISTS products (
#     product_id TEXT PRIMARY KEY,
#     product_category_name TEXT,
#     product_name_lenght INT,
#     product_description_lenght INT,
#     product_photos_qty INT,
#     product_weight_g INT,
#     product_length_cm INT,
#     product_height_cm INT,
#     product_width_cm INT
# );

# CREATE TABLE IF NOT EXISTS orders (
#     order_id TEXT PRIMARY KEY,
#     customer_id TEXT REFERENCES customers(customer_id),
#     order_status TEXT,
#     order_purchase_timestamp TIMESTAMP,
#     order_approved_at TIMESTAMP,
#     order_delivered_carrier_date TIMESTAMP,
#     order_delivered_customer_date TIMESTAMP,
#     order_estimated_delivery_date TIMESTAMP
# );

# CREATE TABLE IF NOT EXISTS order_items (
#     order_id TEXT REFERENCES orders(order_id),
#     order_item_id INT,
#     product_id TEXT REFERENCES products(product_id),
#     seller_id TEXT REFERENCES sellers(seller_id),
#     shipping_limit_date TIMESTAMP,
#     price NUMERIC,
#     freight_value NUMERIC,
#     PRIMARY KEY(order_id, order_item_id)
# );

# CREATE TABLE IF NOT EXISTS payments (
#     order_id TEXT REFERENCES orders(order_id),
#     payment_sequential INT,
#     payment_type TEXT,
#     payment_installments INT,
#     payment_value NUMERIC,
#     PRIMARY KEY(order_id, payment_sequential)
# );

# CREATE TABLE IF NOT EXISTS geolocation (
#     geolocation_zip_code_prefix INT,
#     geolocation_lat NUMERIC,
#     geolocation_lng NUMERIC,
#     geolocation_city TEXT,
#     geolocation_state TEXT
# );
# """

# with engine.begin() as conn:
#     conn.execute(text(tables_sql))

# print("Tables are created (if didn't exist)")

# # --------------------------
# # CSV paths
# # --------------------------
# data_paths = {
#     "customers": "/Users/ankapdf/Desktop/ecommerce_analytics/data/raw/olist_customers_dataset.csv",
#     "sellers": "/Users/ankapdf/Desktop/ecommerce_analytics/data/raw/olist_sellers_dataset.csv",
#     "products": "/Users/ankapdf/Desktop/ecommerce_analytics/data/raw/olist_products_dataset.csv",
#     "orders": "/Users/ankapdf/Desktop/ecommerce_analytics/data/raw/olist_orders_dataset.csv",
#     "order_items": "/Users/ankapdf/Desktop/ecommerce_analytics/data/raw/olist_order_items_dataset.csv",
#     "payments": "/Users/ankapdf/Desktop/ecommerce_analytics/data/raw/olist_order_payments_dataset.csv",
#     "geolocation": "/Users/ankapdf/Desktop/ecommerce_analytics/data/raw/olist_geolocation_dataset.csv"
# }

# # --------------------------
# # Cleaning function
# # --------------------------
# def clean_df(df):
#     # Spaces and empty rows → NaN
#     df = df.replace(r'^\s*$', pd.NA, regex=True)
#     # For numbers changing NaN to 0
#     for col in df.select_dtypes(include='number').columns:
#         df[col] = df[col].fillna(0)
#     return df

# # --------------------------
# # Import CSV to PostgreSQL
# # --------------------------
# for table, path in data_paths.items():
#     print(f"Loading table {table} ...")
#     df = pd.read_csv(path)
#     df = clean_df(df)
#     df.drop_duplicates(subset=['customer_id'])
#     df.to_sql(table, engine, if_exists='append', index=False)
#     print(f"Table {table} uploaded: {len(df)} rows")

# print("All CSV successfully uploaded and cleaned")

# # --------------------------
# # KPI product report
# # --------------------------
# with engine.connect() as conn:
#     # Unique customers
#     unique_customers = conn.execute("SELECT COUNT(DISTINCT customer_id) FROM customers").scalar()
#     # Amount of orders
#     total_orders = conn.execute("SELECT COUNT(*) FROM orders").scalar()
#     # Average Order Value
#     avg_order_value = conn.execute("""
#         SELECT ROUND(AVG(oi.price),2)
#         FROM order_items oi
#     """).scalar()
#     # VIP customers (past 90 days)
#     vip_count = conn.execute("""
#         WITH customer_rfm AS (
#             SELECT 
#                 o.customer_id,
#                 MAX(o.order_purchase_timestamp) AS last_purchase,
#                 COUNT(o.order_id) AS frequency,
#                 SUM(oi.price) AS monetary
#             FROM orders o
#             JOIN order_items oi ON o.order_id = oi.order_id
#             GROUP BY o.customer_id
#         )
#         SELECT COUNT(*) 
#         FROM customer_rfm
#         WHERE monetary > 1000 AND frequency > 5 AND last_purchase > CURRENT_DATE - INTERVAL '90 days';
#     """).scalar()

# # --------------------------
# # Create customer_rfm table for segmentation
# # --------------------------
# with engine.begin() as conn:
#     conn.execute(text("""
#         CREATE TABLE IF NOT EXISTS customer_rfm AS
#         WITH customer_orders AS (
#             SELECT 
#                 o.customer_id,
#                 MAX(o.order_purchase_timestamp) AS last_purchase,
#                 COUNT(o.order_id) AS frequency,
#                 SUM(oi.price) AS monetary
#             FROM orders o
#             JOIN order_items oi ON o.order_id = oi.order_id
#             GROUP BY o.customer_id
#         )
#         SELECT 
#             customer_id,
#             last_purchase,
#             frequency,
#             monetary,
#             CASE 
#                 WHEN monetary > 1000 AND frequency > 5 AND last_purchase > CURRENT_DATE - INTERVAL '90 days'
#                     THEN 'VIP'
#                 WHEN monetary > 500
#                     THEN 'High Potential'
#                 ELSE 'Regular'
#             END AS segment
#         FROM customer_orders;
#     """))
#     print("Table customer_rfm created (with segments)")


# print(f"Unique Customers: {unique_customers}")
# print(f"Total Orders: {total_orders}")
# print(f"Average Order Value: ${avg_order_value}")
# print(f"VIP Customers (last 90 days): {vip_count}")


import pandas as pd
from sqlalchemy import create_engine, text

# --------------------------
# Connect to the db
# --------------------------
engine = create_engine('postgresql+psycopg2://nana:Ha-KI-248@localhost:5432/ecommerce_analytics')

# --------------------------
# Create tables (if doesn't exist)
# --------------------------
tables_sql = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_unique_id TEXT,
    customer_zip_code_prefix INT,
    customer_city TEXT,
    customer_state TEXT
);

CREATE TABLE IF NOT EXISTS sellers (
    seller_id TEXT PRIMARY KEY,
    seller_zip_code_prefix INT,
    seller_city TEXT,
    seller_state TEXT
);

CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_category_name TEXT,
    product_name_lenght INT,
    product_description_lenght INT,
    product_photos_qty INT,
    product_weight_g INT,
    product_length_cm INT,
    product_height_cm INT,
    product_width_cm INT
);

CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT REFERENCES customers(customer_id),
    order_status TEXT,
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    order_id TEXT REFERENCES orders(order_id),
    order_item_id INT,
    product_id TEXT REFERENCES products(product_id),
    seller_id TEXT REFERENCES sellers(seller_id),
    shipping_limit_date TIMESTAMP,
    price NUMERIC,
    freight_value NUMERIC,
    PRIMARY KEY(order_id, order_item_id)
);

CREATE TABLE IF NOT EXISTS payments (
    order_id TEXT REFERENCES orders(order_id),
    payment_sequential INT,
    payment_type TEXT,
    payment_installments INT,
    payment_value NUMERIC,
    PRIMARY KEY(order_id, payment_sequential)
);

CREATE TABLE IF NOT EXISTS geolocation (
    geolocation_zip_code_prefix INT PRIMARY KEY,
    geolocation_lat NUMERIC,
    geolocation_lng NUMERIC,
    geolocation_city TEXT,
    geolocation_state TEXT
);
"""

with engine.begin() as conn:
    conn.execute(text(tables_sql))

print("Tables are created (if didn't exist)")

# --------------------------
# CSV paths
# --------------------------
data_paths = {
    "customers": "/Users/ankapdf/Desktop/ecommerce_analytics/data/raw/olist_customers_dataset.csv",
    "sellers": "/Users/ankapdf/Desktop/ecommerce_analytics/data/raw/olist_sellers_dataset.csv",
    "products": "/Users/ankapdf/Desktop/ecommerce_analytics/data/raw/olist_products_dataset.csv",
    "orders": "/Users/ankapdf/Desktop/ecommerce_analytics/data/raw/olist_orders_dataset.csv",
    "order_items": "/Users/ankapdf/Desktop/ecommerce_analytics/data/raw/olist_order_items_dataset.csv",
    "payments": "/Users/ankapdf/Desktop/ecommerce_analytics/data/raw/olist_order_payments_dataset.csv",
    "geolocation": "/Users/ankapdf/Desktop/ecommerce_analytics/data/raw/olist_geolocation_dataset.csv"
}

# --------------------------
# Cleaning function
# --------------------------
def clean_df(df):
    df = df.replace(r'^\s*$', pd.NA, regex=True)
    for col in df.select_dtypes(include='number').columns:
        df[col] = df[col].fillna(0)
    return df

# --------------------------
# Primary keys for tables
# --------------------------
primary_keys = {
    "customers": ["customer_id"],
    "sellers": ["seller_id"],
    "products": ["product_id"],
    "orders": ["order_id"],
    "order_items": ["order_id", "order_item_id"],
    "payments": ["order_id", "payment_sequential"],
    "geolocation": ["geolocation_zip_code_prefix"]
}

# --------------------------
# Import CSV to PostgreSQL (safe for duplicates)
# --------------------------
for table, path in data_paths.items():
    print(f"Loading table {table} ...")
    df = pd.read_csv(path)
    df = clean_df(df)

    if table in primary_keys:
        df = df.drop_duplicates(subset=primary_keys[table])

        # Select only new rows that are not in the database
        existing_df = pd.read_sql(f"SELECT {', '.join(primary_keys[table])} FROM {table}", engine)
        if len(primary_keys[table]) == 1:
            df = df[~df[primary_keys[table][0]].isin(existing_df[primary_keys[table][0]])]
        else:
            df = df.merge(existing_df, on=primary_keys[table], how='left', indicator=True)
            df = df[df['_merge'] == 'left_only'].drop(columns=['_merge'])

    if not df.empty:
        df.to_sql(table, engine, if_exists='append', index=False)
        print(f"Table {table} uploaded: {len(df)} rows")
    else:
        print(f"No new rows to insert into {table}")

print("All CSV successfully uploaded and cleaned")

# --------------------------
# KPI product report
# --------------------------
with engine.connect() as conn:
    unique_customers = conn.execute("SELECT COUNT(DISTINCT customer_id) FROM customers").scalar()
    total_orders = conn.execute("SELECT COUNT(*) FROM orders").scalar()
    avg_order_value = conn.execute("SELECT ROUND(AVG(price),2) FROM order_items").scalar()

print(f"Unique Customers: {unique_customers}")
print(f"Total Orders: {total_orders}")
print(f"Average Order Value: ${avg_order_value}")

# --------------------------
# Create customer_rfm table for segmentation (VIP / High Potential / Regular)
# --------------------------
with engine.begin() as conn:
    conn.execute(text("""
        DROP TABLE IF EXISTS customer_rfm;
        CREATE TABLE customer_rfm AS
        WITH customer_orders AS (
            SELECT 
                o.customer_id,
                MAX(o.order_purchase_timestamp) AS last_purchase,
                COUNT(o.order_id) AS frequency,
                SUM(oi.price) AS monetary
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY o.customer_id
        )
        SELECT 
            customer_id,
            last_purchase,
            frequency,
            monetary,
            CASE 
                WHEN monetary > 1000 AND frequency > 5 AND last_purchase > CURRENT_DATE - INTERVAL '90 days'
                    THEN 'VIP'
                WHEN monetary > 500
                    THEN 'High Potential'
                ELSE 'Regular'
            END AS segment
        FROM customer_orders;
    """))
    print("Table customer_rfm created (with segments)")