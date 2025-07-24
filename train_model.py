# train_model.py (NEW & IMPROVED)
# This version uses a Gradient Boosting Regressor, a powerful model
# that is much better suited for this type of data.

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
import joblib
import os

print("--- Starting AI Model Training Script (Gradient Boosting) ---")

# --- 1. Load Data ---
print("Step 1: Loading data...")
try:
    data = pd.read_csv('prices.csv')
except FileNotFoundError:
    print("\nError: 'prices.csv' not found.")
    exit()

TARGET_COLUMN = 'Modal Price'
if TARGET_COLUMN not in data.columns:
    print(f"\nError: Target column '{TARGET_COLUMN}' not found in prices.csv.")
    exit()

data.dropna(subset=[TARGET_COLUMN], inplace=True)
data = data.fillna('Unknown')

FEATURES = ['State', 'District', 'Commodity']
X = data[FEATURES]
y = data[TARGET_COLUMN]
print("Data loaded successfully.")

# --- 2. Define Preprocessing and Model Pipeline ---
print("Step 2: Defining the model pipeline...")

# Define the preprocessor for categorical features
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), FEATURES)
    ],
    remainder='passthrough'
)

# Define the model
# n_estimators=100 means it will build 100 decision trees.
# learning_rate=0.1 is a good default.
# max_depth=5 prevents the trees from getting too complex.
model = GradientBoostingRegressor(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    random_state=42,
    verbose=1 # This will print progress during training
)

# Create the full pipeline
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', model)
])
print("Pipeline created.")

# --- 3. Split and Train ---
print("Step 3: Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print("Data split. Starting model training...")

# Train the entire pipeline
pipeline.fit(X_train, y_train)
print("\nTraining finished.")

# --- 4. Evaluate ---
print("Step 4: Evaluating model performance...")
score = pipeline.score(X_test, y_test)
print(f'Model R^2 Score (Accuracy): {score:.4f}')
print("(An R^2 score close to 1.0 is very good)")

# --- 5. Save the Pipeline ---
print("Step 5: Saving the trained model pipeline...")
output_dir = 'model_files'
os.makedirs(output_dir, exist_ok=True)

# We save the entire pipeline, which includes the preprocessor and the model
joblib.dump(pipeline, os.path.join(output_dir, 'gradient_boosting_model.joblib'))

print(f"Model saved in '{output_dir}' directory.")
print("\n--- Script finished successfully! ---")