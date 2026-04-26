"""
Model inference engine for the KhetBuddy Fertilizer Recommendation API.
Loads trained artefacts once at startup and exposes a single predict() call.
"""

import os
import joblib
import numpy as np
import pandas as pd
from functools import lru_cache
from typing import Dict, Any

from app.schemas import FertilizerRequest, FertilizerResponse, NutrientDeficiencyDetail
from app.rules import get_application_timing, nutrient_risk

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")


# ─────────────────────────────────────────────────────────────────────────────
# Model loader (cached — loaded only once)
# ─────────────────────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _load_models() -> Dict[str, Any]:
    preprocessor = joblib.load(os.path.join(MODELS_DIR, "preprocessor.pkl"))
    npk_model    = joblib.load(os.path.join(MODELS_DIR, "npk_regressor.pkl"))
    risk_model   = joblib.load(os.path.join(MODELS_DIR, "risk_classifier.pkl"))
    return {
        "preprocessor": preprocessor,
        "npk_model":    npk_model,
        "risk_model":   risk_model,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Feature engineering (must mirror train.py)
# ─────────────────────────────────────────────────────────────────────────────
def _build_features(req: FertilizerRequest) -> pd.DataFrame:
    sn, sp, sk = req.soil_n, req.soil_p, req.soil_k
    npk_total  = sn + sp + sk

    row = {
        # Categorical
        "crop":           req.crop_type,
        "stage":          req.growth_stage,
        "irrigation_type": req.irrigation_type,
        # Numerical
        "soil_N":         sn,
        "soil_P":         sp,
        "soil_K":         sk,
        "temperature":    req.temperature,
        "rainfall":       req.rainfall,
        "humidity":       req.humidity,
        "soil_pH":        req.soil_ph,
        # Engineered
        "np_ratio":       sn / (sp + 1e-6),
        "nk_ratio":       sn / (sk + 1e-6),
        "pk_ratio":       sp / (sk + 1e-6),
        "npk_total":      npk_total,
        "fertility_index": (sn * 0.4 + sp * 0.3 + sk * 0.3) / (npk_total + 1e-6),
    }
    return pd.DataFrame([row])


# ─────────────────────────────────────────────────────────────────────────────
# Public predict function
# ─────────────────────────────────────────────────────────────────────────────
def predict(req: FertilizerRequest) -> FertilizerResponse:
    models = _load_models()

    # Build & transform features
    X_raw = _build_features(req)
    X_t   = models["preprocessor"].transform(X_raw)

    # NPK regression
    npk_pred  = models["npk_model"].predict(X_t)[0]
    rec_n = max(0.0, round(float(npk_pred[0]), 1))
    rec_p = max(0.0, round(float(npk_pred[1]), 1))
    rec_k = max(0.0, round(float(npk_pred[2]), 1))

    # Risk classification
    risk_pred = models["risk_model"].predict(X_t)[0]          # "Low" / "Medium" / "High"

    # Per-nutrient deficiency breakdown (rule-based)
    n_risk = nutrient_risk(req.soil_n, rec_n)
    p_risk = nutrient_risk(req.soil_p, rec_p)
    k_risk = nutrient_risk(req.soil_k, rec_k)

    # Timing recommendation (rule-based)
    timing = get_application_timing(
        growth_stage=req.growth_stage,
        temperature=req.temperature,
        rainfall=req.rainfall,
        irrigation_type=req.irrigation_type,
    )

    return FertilizerResponse(
        recommended_N=rec_n,
        recommended_P=rec_p,
        recommended_K=rec_k,
        deficiency_risk=risk_pred,
        nutrient_deficiency=NutrientDeficiencyDetail(
            nitrogen=n_risk,
            phosphorus=p_risk,
            potassium=k_risk,
        ),
        application_time=timing,
        crop_type=req.crop_type,
        growth_stage=req.growth_stage,
    )
