# ============================================================
# STEP 1: Import Libraries
# ============================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# ============================================================
# STEP 2: Load Data
# ============================================================
df = pd.read_csv("netflix_cleaned.csv")

# ============================================================
# STEP 3: Prepare Data for Modeling
# ============================================================
# عدد المحتوى المضاف كل سنة
yearly = df.groupby('year_added')['show_id'].count().reset_index()
yearly.columns = ['year', 'total_content']
yearly = yearly.dropna()
yearly = yearly[yearly['year'] > 2000]  # بعد 2000 بس

print(yearly)

# ============================================================
# STEP 4: Define X and y
# ============================================================
X = yearly[['year']]        # Feature
y = yearly['total_content'] # Target

# ============================================================
# STEP 5: Split Data
# ============================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ============================================================
# STEP 6: Train Model
# ============================================================
model = LinearRegression()
model.fit(X_train, y_train)

print(f"\n✅ Model trained!")
print(f"Coefficient : {model.coef_[0]:.2f}")
print(f"Intercept   : {model.intercept_:.2f}")

# ============================================================
# STEP 7: Evaluate Model
# ============================================================
y_pred = model.predict(X_test)

print(f"\n📊 Model Performance:")
print(f"R² Score : {r2_score(y_test, y_pred):.2f}")
print(f"MSE      : {mean_squared_error(y_test, y_pred):.2f}")

# ============================================================
# STEP 8: Predict Future Years
# ============================================================
future_years = pd.DataFrame({'year': [2023, 2024, 2025]})
predictions = model.predict(future_years)

print(f"\n🔮 Predictions:")
for year, pred in zip(future_years['year'], predictions):
    print(f"  {year}: {int(pred)} titles expected")

# ============================================================
# STEP 9: Plot
# ============================================================
plt.figure(figsize=(10, 6))

# Actual data
plt.scatter(X, y, color='red', label='Actual Data', zorder=5)

# Regression line
X_line = np.linspace(X['year'].min(), 2025, 100).reshape(-1, 1)
y_line = model.predict(X_line)
plt.plot(X_line, y_line, color='blue', linewidth=2, label='Regression Line')

# Future predictions
plt.scatter(future_years, predictions, color='green', 
            marker='*', s=200, label='Future Predictions', zorder=5)

plt.title('Netflix Content Growth — Linear Regression', fontsize=14)
plt.xlabel('Year')
plt.ylabel('Total Content Added')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('netflix_regression.png')
plt.show()

print("\n✅ Plot saved → netflix_regression.png")