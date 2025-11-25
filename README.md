🍫 Chocolate Data Pipeline & Analysis Project

End-to-End Data Engineering + Data Cleaning + SQL + Analysis

This project extracts real-world chocolate product data from the OpenFoodFacts API, cleans and processes it using Python, loads it into a database, and performs exploratory data analysis.

📌 Project Overview

The goal of this project is to build a complete data pipeline:

Extract chocolate product data (12,000+ records) from the OpenFoodFacts REST API using pagination

Transform & Clean the dataset

Load the cleaned data into an SQL database

Analyze the dataset using Python / SQL

(Optional) Visualize the results in a dashboard

The dataset includes:

Product code

Product name

Brand

Nutritional information (calories, sugars, fats, etc.)

🛠️ Technologies Used

Python 3

Pandas

Requests

NumPy

MySQL / SQLite

Jupyter Notebook

Matplotlib / Seaborn (optional for visuals)

📂 Project Structure
/chocolate-analysis-project
    |
    ├── 01_extract_chocolate_data.py         # Extracts 12k records via pagination
    ├── 02_clean_chocolate_data.py           # Cleans & preprocesses data
    ├── 03_load_to_sql.py                    # Loads cleaned data into SQL database
    |
    ├── /data
    │       ├── raw_chocolate_data.csv       # Raw data from API
    │       └── cleaned_chocolate_data.csv   # Cleaned dataset
    |
    ├── Chocolate_Data_Analysis.ipynb        # Jupyter-based EDA & visualizations
    |
    ├── database_schema.sql                  # SQL schema & table structure
    ├── requirements.txt                     # Python dependencies
    ├── architecture.png                     # Optional pipeline diagram
    └── README.md                            # Project documentation

🚀 1. Data Extraction Process

Data is fetched using the OpenFoodFacts API endpoint:

https://world.openfoodfacts.org/api/v2/search


Parameters used:

categories = chocolates

fields = code, product_name, brands, nutriments

page_size = 100

Pagination across 120+ pages to reach ~12,000 records

📌 Output File:

✔ data/raw_chocolate_data.csv

🧹 2. Data Cleaning

Performed using pandas:

✔ Flattening nested JSON

The nutriments column is expanded into individual columns:

nutriments_df = df["nutriments"].apply(pd.Series)
df = pd.concat([df.drop("nutriments", axis=1), nutriments_df], axis=1)

✔ Handling Missing Values

Identify null-heavy columns

Drop unnecessary / unusable features

Impute missing numeric values (mean/median)

Clean text fields (trim spaces, remove empty strings)

✔ Final Output:

data/cleaned_chocolate_data.csv

🗄️ 3. Loading to SQL

The cleaned dataset is loaded into a MySQL or SQLite database.

Includes:

Creating table schema

Inserting cleaned rows

Ensuring correct datatypes

Example commands:

python 03_load_to_sql.py

📊 4. Exploratory Data Analysis

Performed in Chocolate_Data_Analysis.ipynb

Example insights:

Average sugar & fat content across brands

Top chocolate brands with highest calorie products

Correlation between nutritional values

Identifying healthier chocolate options

Includes:

Histograms

Bar charts

Correlation heatmaps

📝 5. Requirements

Install dependencies:

pip install -r requirements.txt


Main libraries:

pandas
requests
mysql-connector-python
numpy

▶️ 6. How to Run the Project
Step 1 — Extract raw data
python 01_extract_chocolate_data.py

Step 2 — Clean data
python 02_clean_chocolate_data.py

Step 3 — Load into SQL
python 03_load_to_sql.py

Step 4 — Run analysis

Open the Jupyter notebook:

jupyter notebook Chocolate_Data_Analysis.ipynb

📈 7. Future Improvements

Build a Power BI/Tableau Dashboard

Add automated logging

Schedule extraction using Airflow or Cron

Store data in a cloud warehouse (BigQuery/Snowflake)

🤝 Contributions

Feel free to fork the repo and submit pull requests for improvements.