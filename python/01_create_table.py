import pandas as pd
from sqlalchemy import create_engine, text

# --------------------------
# 1️⃣ Подключение к базе
# --------------------------
engine = create_engine('postgresql+psycopg2://nana:Ha-KI-248@localhost:5432/ecommerce_analytics')

# --------------------------
# 2️⃣ Создание таблиц (если нет)
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
    geolocation_zip_code_prefix INT,
    geolocation_lat NUMERIC,
    geolocation_lng NUMERIC,
    geolocation_city TEXT,
    geolocation_state TEXT
);
"""

with engine.begin() as conn:
    conn.execute(text(tables_sql))

print("✅ Таблицы созданы (если не существовали)")

# --------------------------
# 3️⃣ Пути к CSV
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
# 4️⃣ Функция для очистки
# --------------------------
def clean_df(df):
    # Пробелы и пустые строки → NaN
    df = df.replace(r'^\s*$', pd.NA, regex=True)
    # Для числовых колонок заменяем NaN на 0
    for col in df.select_dtypes(include='number').columns:
        df[col] = df[col].fillna(0)
    return df

# --------------------------
# 5️⃣ Импорт CSV в PostgreSQL
# --------------------------
for table, path in data_paths.items():
    print(f"Загружаем таблицу {table} ...")
    df = pd.read_csv(path)
    df = clean_df(df)
    df.to_sql(table, engine, if_exists='append', index=False)
    print(f"✅ Таблица {table} загружена: {len(df)} строк")

print("🎉 Все CSV успешно загружены и очищены!")

