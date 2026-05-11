# ============================================================
# Netflix Data Pipeline — Full Script
# ============================================================
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import logging
import io
from datetime import datetime

# ============================================================
# SETUP LOGGING
# ============================================================
logging.basicConfig(
    filename='pipeline_log.txt',
    level=logging.INFO,
    format='%(asctime)s — %(levelname)s — %(message)s'
)

def log(msg):
    print(msg)
    logging.info(msg)

# ============================================================
# STEP 1: Load Data
# ============================================================
def load_data():
    log("📥 Loading data...")
    df = pd.read_csv("netflix_titles.csv")
    log(f"✅ Loaded {len(df)} rows")
    return df

# ============================================================
# STEP 2: Clean Data
# ============================================================
def clean_data(df):
    log("🧹 Cleaning data...")

    before = len(df)
    duplicates = df.duplicated().sum()

    df.drop_duplicates(inplace=True)
    df['director'].fillna('Unknown', inplace=True)
    df['cast'].fillna('Unknown', inplace=True)
    df['country'].fillna(df['country'].mode()[0], inplace=True)
    df['date_added'].fillna('Unknown', inplace=True)
    df['rating'].fillna(df['rating'].mode()[0], inplace=True)
    df.dropna(subset=['duration'], inplace=True)

    df = df.apply(lambda col: col.str.replace('\n', ' ', regex=False)
                  .str.replace('\r', ' ', regex=False)
                  if col.dtype == 'object' else col)

    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['year_added'] = df['date_added'].dt.year
    df['month_added'] = df['date_added'].dt.month

    log(f"✅ Duplicates removed : {duplicates}")
    log(f"✅ Rows after cleaning: {len(df)}")

    df.to_csv("netflix_cleaned.csv", index=False)
    log("✅ Saved → netflix_cleaned.csv")
    return df

# ============================================================
# STEP 3: Upload to PostgreSQL
# ============================================================
def upload_to_db(df):
    log("🗄️ Uploading to PostgreSQL...")

    DB_USER     = "postgres"
    DB_PASSWORD = "1234"  
    DB_HOST     = "localhost"
    DB_PORT     = "5432"
    DB_NAME     = "netflix_db"

    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS netflix_titles"))

    raw_conn = engine.raw_connection()
    cursor = raw_conn.cursor()

    cursor.execute("""
        CREATE TABLE netflix_titles (
            show_id       VARCHAR(20),
            type          VARCHAR(20),
            title         VARCHAR(300),
            director      VARCHAR(300),
            "cast"        TEXT,
            country       VARCHAR(200),
            date_added    VARCHAR(50),
            release_year  INTEGER,
            rating        VARCHAR(20),
            duration      VARCHAR(50),
            listed_in     VARCHAR(300),
            description   TEXT,
            year_added    FLOAT,
            month_added   FLOAT
        )
    """)

    output = io.StringIO()
    df.to_csv(output, index=False, header=False)
    output.seek(0)

    cursor.copy_expert(
        "COPY netflix_titles FROM STDIN WITH (FORMAT CSV, NULL '')",
        output
    )

    raw_conn.commit()
    cursor.close()
    raw_conn.close()

    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM netflix_titles")).scalar()
        log(f"✅ Rows in database: {count}")

# ============================================================
# STEP 4: Run Modeling
# ============================================================
def run_modeling(df):
    log("🤖 Running Linear Regression...")

    yearly = df.groupby('year_added')['show_id'].count().reset_index()
    yearly.columns = ['year', 'total_content']
    yearly = yearly.dropna()
    yearly = yearly[yearly['year'] > 2000]

    X = yearly[['year']]
    y = yearly['total_content']

    model = LinearRegression()
    model.fit(X, y)

    future_years = pd.DataFrame({'year': [2023, 2024, 2025]})
    predictions = model.predict(future_years)

    log(f"✅ R² Score: {model.score(X, y):.2f}")
    for year, pred in zip(future_years['year'], predictions):
        log(f"  {year}: {int(pred)} titles expected")

    plt.figure(figsize=(10, 6))
    plt.scatter(X, y, color='red', label='Actual')
    X_line = np.linspace(X['year'].min(), 2025, 100).reshape(-1, 1)
    plt.plot(X_line, model.predict(X_line), color='blue', label='Regression')
    plt.scatter(future_years, predictions, color='green', marker='*', s=200, label='Predictions')
    plt.title('Netflix Content Growth — Linear Regression')
    plt.xlabel('Year')
    plt.ylabel('Total Content')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('netflix_regression.png')
    plt.close()
    log("✅ Plot saved → netflix_regression.png")

# ============================================================
# MAIN
# ============================================================
def main():
    log("=" * 50)
    log(f"🚀 Pipeline started: {datetime.now()}")
    log("=" * 50)

    df = load_data()
    df = clean_data(df)
    upload_to_db(df)
    run_modeling(df)

    log("=" * 50)
    log(f"✅ Pipeline finished: {datetime.now()}")
    log("=" * 50)

if __name__ == "__main__":
    main()