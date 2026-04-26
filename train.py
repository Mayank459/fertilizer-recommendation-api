"""
Training script for the KhetBuddy Fertilizer Recommendation API.

Models trained:
  1. XGBoost MultiOutput Regressor  → recommended_N, recommended_P, recommended_K
  2. Random Forest Classifier        → risk (Low / Medium / High)

Artefacts saved to: models/
  - preprocessor.pkl
  - npk_regressor.pkl
  - risk_classifier.pkl
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    classification_report,
)
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_PATH   = os.path.join(BASE_DIR, "indian_fertilizer_dataset.csv")
MODELS_DIR  = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Load data
# ─────────────────────────────────────────────────────────────────────────────
print("[INFO] Loading dataset ...")
df = pd.read_csv(DATA_PATH)
print(f"    Shape: {df.shape}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Feature engineering
# ─────────────────────────────────────────────────────────────────────────────
print("[INFO] Engineering features ...")

# NPK ratios
df["np_ratio"]  = df["soil_N"] / (df["soil_P"] + 1e-6)
df["nk_ratio"]  = df["soil_N"] / (df["soil_K"] + 1e-6)
df["pk_ratio"]  = df["soil_P"] / (df["soil_K"] + 1e-6)
df["npk_total"] = df["soil_N"] + df["soil_P"] + df["soil_K"]

# Soil fertility index (simple composite)
df["fertility_index"] = (
    df["soil_N"] * 0.4 + df["soil_P"] * 0.3 + df["soil_K"] * 0.3
) / (df["npk_total"] + 1e-6)

# ─────────────────────────────────────────────────────────────────────────────
# 3. Define feature columns
# ─────────────────────────────────────────────────────────────────────────────
CAT_FEATURES = ["crop", "stage", "irrigation_type"]
NUM_FEATURES = [
    "soil_N", "soil_P", "soil_K", "temperature",
    "rainfall", "humidity", "soil_pH",
    "np_ratio", "nk_ratio", "pk_ratio", "npk_total", "fertility_index",
]

FEATURES = CAT_FEATURES + NUM_FEATURES
TARGETS_REG   = ["recommended_N", "recommended_P", "recommended_K"]
TARGET_CLS    = "risk"

X = df[FEATURES]
y_reg = df[TARGETS_REG]
y_cls = df[TARGET_CLS]

# ─────────────────────────────────────────────────────────────────────────────
# 4. Preprocessing pipeline
# ─────────────────────────────────────────────────────────────────────────────
print("[INFO] Building preprocessing pipeline ...")
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT_FEATURES),
        ("num", StandardScaler(), NUM_FEATURES),
    ]
)

# ─────────────────────────────────────────────────────────────────────────────
# 5. Train / test split
# ─────────────────────────────────────────────────────────────────────────────
X_train, X_test, yr_train, yr_test, yc_train, yc_test = train_test_split(
    X, y_reg, y_cls, test_size=0.2, random_state=42
)

X_train_t = preprocessor.fit_transform(X_train)
X_test_t  = preprocessor.transform(X_test)

# ─────────────────────────────────────────────────────────────────────────────
# 6. Train NPK Regressor (XGBoost multi-output)
# ─────────────────────────────────────────────────────────────────────────────
print("[INFO] Training XGBoost NPK Regressor ...")
base_xgb = XGBRegressor(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.08,
    subsample=0.85,
    colsample_bytree=0.85,
    random_state=42,
    n_jobs=-1,
    verbosity=0,
)
npk_model = MultiOutputRegressor(base_xgb)
npk_model.fit(X_train_t, yr_train)

yr_pred = npk_model.predict(X_test_t)
for i, nutrient in enumerate(TARGETS_REG):
    mae = mean_absolute_error(yr_test.iloc[:, i], yr_pred[:, i])
    r2  = r2_score(yr_test.iloc[:, i], yr_pred[:, i])
    print(f"    {nutrient:15s}  MAE={mae:.2f}  R²={r2:.4f}")

# ─────────────────────────────────────────────────────────────────────────────
# 7. Train Risk Classifier (Random Forest)
# ─────────────────────────────────────────────────────────────────────────────
print("[INFO] Training Random Forest Risk Classifier ...")
risk_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    random_state=42,
    n_jobs=-1,
)
risk_model.fit(X_train_t, yc_train)
yc_pred = risk_model.predict(X_test_t)
print(classification_report(yc_test, yc_pred))

# ─────────────────────────────────────────────────────────────────────────────
# 8. Save artefacts
# ─────────────────────────────────────────────────────────────────────────────
print("[INFO] Saving model artefacts ...")
joblib.dump(preprocessor, os.path.join(MODELS_DIR, "preprocessor.pkl"))
joblib.dump(npk_model,    os.path.join(MODELS_DIR, "npk_regressor.pkl"))
joblib.dump(risk_model,   os.path.join(MODELS_DIR, "risk_classifier.pkl"))
print("[DONE] Training complete. Models saved to:", MODELS_DIR)
