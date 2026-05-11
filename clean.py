import pandas as pd
import numpy as np

df = pd.read_csv('netflix_titles.csv')

print("Shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nFirst 3 rows:")
df.head(3)

df.describe()

report_before = pd.DataFrame({
    'Column': df.columns,
    'Missing_Count': df.isnull().sum().values,
    'Missing_%': (df.isnull().sum().values / len(df) * 100).round(2),
    'Dtype': df.dtypes.values
})

duplicates_count = df.duplicated().sum()

print("=" * 50)
print(" CLEANING REPORT — BEFORE")
print("=" * 50)
print(f"\n Total Rows     : {len(df)}")
print(f" Total Columns  : {df.shape[1]}")
print(f" Total Duplicates: {duplicates_count}")
print(f"\n Missing Values per Column:")
print(report_before[report_before['Missing_Count'] > 0].to_string(index=False))

df.drop_duplicates(inplace=True)
print(f" Duplicates removed. Rows after: {len(df)}")


df['director'].fillna('Unknown', inplace=True)

df['cast'].fillna('Unknown', inplace=True)

df['date_added'].fillna('Unknown', inplace=True)

# country,rating fill with mode(more repetirive)
df['country'].fillna(df['country'].mode()[0], inplace=True)
df['rating'].fillna(df['rating'].mode()[0], inplace=True)

# duration — drop because few 
df.dropna(subset=['duration'], inplace=True)

print(" Missing values handled.")


# date_added --> datetime
df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')

# year ,month columns
df['year_added'] = df['date_added'].dt.year
df['month_added'] = df['date_added'].dt.month

print(" Data types fixed.")
print(df[['date_added', 'year_added', 'month_added']].head(3))


#last cleaning report
report_after = pd.DataFrame({
    'Column': df.columns,
    'Missing_Count': df.isnull().sum().values,
    'Missing_%': (df.isnull().sum().values / len(df) * 100).round(2),
})

# Summary Report
summary = pd.DataFrame({
    'Metric': [
        'Rows (Original)',
        'Rows (After Cleaning)',
        'Duplicates Found',
        'Duplicates Removed',
        'Missing: director',
        'Missing: cast',
        'Missing: country',
        'Missing: date_added',
        'Missing: rating',
        'Action: director/cast/date_added/rating',
        'Action: country',
        'Action: duration',
    ],
    'Value': [
        8807,
        len(df),
        duplicates_count,
        duplicates_count,
        'filled → Unknown',
        'filled → Unknown',
        'filled → mode',
        'filled → Unknown',
        'filled → mode',
        'fillna()',
        'fillna(mode)',
        'dropna()',
    ]
})

print("=" * 50)
print(" CLEANING REPORT — AFTER")
print("=" * 50)
print(summary.to_string(index=False))



# ============================================================
# STEP 8: Export Clean Dataset
# ============================================================
df.to_csv('netflix_cleaned.csv', index=False)
print(" Clean dataset saved → netflix_cleaned.csv")
print(f"Final shape: {df.shape}")
