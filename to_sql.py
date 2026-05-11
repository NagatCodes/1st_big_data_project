import pandas as pd
from sqlalchemy import create_engine, text
import io

DB_USER     = "postgres"
DB_PASSWORD = "1234"  
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "netflix_db"

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
print("✅ Engine created.")

df = pd.read_csv("netflix_cleaned.csv")
print(f"✅ Dataset loaded — {df.shape[0]} rows, {df.shape[1]} columns")

# تنظيف الـ newlines
df = df.apply(lambda col: col.str.replace('\n', ' ', regex=False)
              .str.replace('\r', ' ', regex=False)
              if col.dtype == 'object' else col)

# مسح الجدول القديم
with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS netflix_titles"))
    print("✅ Old table dropped.")

# إنشاء الجدول ورفع الداتا
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

print("✅ Data uploaded successfully!")

# Verify
with engine.connect() as conn:
    count = conn.execute(text("SELECT COUNT(*) FROM netflix_titles")).scalar()
    print(f"✅ Rows in database: {count}")

    sample = conn.execute(text(
        "SELECT show_id, title, type, release_year FROM netflix_titles LIMIT 3"
    ))
    print("\n📋 Sample from DB:")
    for row in sample:
        print(row)