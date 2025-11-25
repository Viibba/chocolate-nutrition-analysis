# =========================================================
# CHOCOLATE PRODUCTS → CLEANING → FEATURES → MYSQL INSERT
# =========================================================

import requests
import pandas as pd
import time
import os
import mysql.connector

# =========================================================
# STEP 1: FETCH RAW DATA (ONLY ONCE)
# =========================================================

BASE_URL = "https://world.openfoodfacts.org/api/v2/search"
params = {
    "categories": "chocolates",
    "fields": "code,product_name,brands,nutriments",
    "page_size": 100
}

all_products = []
max_pages = 120   # ~12,000 records

RAW_FILE = "chocolate_products_raw.csv"

if not os.path.exists(RAW_FILE):
    print("Fetching API data...")
    for page in range(1, max_pages + 1):
        params["page"] = page
        response = requests.get(BASE_URL, params=params)

        if response.status_code != 200:
            print(f"Error at page {page}")
            break

        products = response.json().get("products", [])
        if not products:
            print("No more data.")
            break

        for prod in products:
            all_products.append({
                "product_code": prod.get("code"),
                "product_name": prod.get("product_name"),
                "brand": prod.get("brands"),
                "nutriments": prod.get("nutriments")
            })

        print(f"Page {page} fetched.")

        time.sleep(0.4)

    df = pd.DataFrame(all_products)
    df.to_csv(RAW_FILE, index=False)
    print("Saved raw data!")
else:
    df = pd.read_csv(RAW_FILE)
    print("Loaded raw CSV.")

# =========================================================
# STEP 2: CLEANING & NUTRIMENT FLATTENING
# =========================================================

if "nutriments" in df.columns:
    nutriments_df = df["nutriments"].apply(pd.Series)
    df = pd.concat([df.drop("nutriments", axis=1), nutriments_df], axis=1)

# Drop columns with >50% missing
null_pct = (df.isnull().sum() / len(df)) * 100
drop_cols = null_pct[null_pct > 50].index
df.drop(columns=drop_cols, inplace=True)

# Fill missing categorical values
cat_cols = df.select_dtypes(include="object").columns
df[cat_cols] = df[cat_cols].fillna("Unknown")

# Fill missing numeric values
num_cols = df.select_dtypes(include="number").columns
df[num_cols] = df[num_cols].fillna(df[num_cols].median())

# =========================================================
# STEP 3: FEATURE ENGINEERING
# =========================================================

df["sugar_to_carb_ratio"] = df["sugars_value"] / df["carbohydrates_value"]

def calorie_category(kcal):
    if kcal < 250: return "Low"
    elif kcal < 400: return "Moderate"
    return "High"

df["calorie_category"] = df["energy-kcal_value"].apply(calorie_category)

def sugar_category(s):
    if s < 10: return "Low Sugar"
    elif s < 20: return "Moderate Sugar"
    return "High Sugar"

df["sugar_category"] = df["sugars_value"].apply(sugar_category)

df["is_ultra_processed"] = df["nova-group"].apply(
    lambda x: "Yes" if x == 4 else "No"
)

df.to_csv("chocolate_products_features.csv", index=False)
print("Saved feature engineered dataset.")

# =========================================================
# STEP 4: MYSQL DATABASE INSERT
# =========================================================

# ---- 4.1 Modify these with YOUR MySQL credentials ------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vikram@3ms",
    database="food_db"
)

cursor = db.cursor()

# ---- 4.2 Create tables if not exist ---------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS product_info (
    product_code VARCHAR(50) PRIMARY KEY,
    product_name TEXT,
    brand TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS nutrient_info (
    product_code VARCHAR(50),
    energy_kcal FLOAT,
    carbohydrates FLOAT,
    sugars FLOAT,
    proteins FLOAT,
    fat FLOAT,
    fiber FLOAT,
    salt FLOAT,
    PRIMARY KEY(product_code)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS derived_metrics (
    product_code VARCHAR(50),
    sugar_to_carb_ratio FLOAT,
    calorie_category VARCHAR(20),
    sugar_category VARCHAR(20),
    is_ultra_processed VARCHAR(5),
    PRIMARY KEY(product_code)
);
""")

db.commit()


# ---- 4.3 INSERT DATA -------------------------------------

for _, row in df.iterrows():

    # Insert product info
    cursor.execute("""
        REPLACE INTO product_info (product_code, product_name, brand)
        VALUES (%s, %s, %s)
    """, (
        row["product_code"],
        row["product_name"],
        row["brand"]
    ))

    # Insert nutrient info
    cursor.execute("""
        REPLACE INTO nutrient_info 
        (product_code, energy_kcal, carbohydrates, sugars, proteins, fat, fiber, salt)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row["product_code"],
        row.get("energy-kcal_value"),
        row.get("carbohydrates_value"),
        row.get("sugars_value"),
        row.get("proteins_value"),
        row.get("fat_value"),
        row.get("fiber_value"),
        row.get("salt_value")
    ))

    # Insert derived metrics
    cursor.execute("""
        REPLACE INTO derived_metrics
        (product_code, sugar_to_carb_ratio, calorie_category, sugar_category, is_ultra_processed)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        row["product_code"],
        row["sugar_to_carb_ratio"],
        row["calorie_category"],
        row["sugar_category"],
        row["is_ultra_processed"]
    ))

db.commit()
cursor.close()
db.close()

print("🎉 ALL DONE — DATA INSERTED INTO MYSQL!")
