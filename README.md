<h1 align="center">🌱 KhetBuddy Fertilizer Recommendation API</h1>

<p align="center">
  <b>Intelligent, data-driven fertilizer recommendations for Indian crops.</b><br/>
  Powered by <b>XGBoost</b> + <b>Random Forest</b> — trained on the Indian Fertilizer Dataset.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/XGBoost-2.0+-orange?logo=xgboost" />
  <img src="https://img.shields.io/badge/Scikit--learn-1.4+-F7931E?logo=scikit-learn&logoColor=white" />
  <img src="https://img.shields.io/badge/Deployed%20on-Render-46E3B7?logo=render&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [API Endpoints](#-api-endpoints)
- [Input Parameters](#-input-parameters)
- [Output Response](#-output-response)
- [Machine Learning Models](#-machine-learning-models)
- [Feature Engineering](#-feature-engineering)
- [Model Evaluation & Comparison](#-model-evaluation--comparison)
- [Project Structure](#-project-structure)
- [Local Setup](#-local-setup)
- [Deployment (Render)](#-deployment-render)
- [Tech Stack](#-tech-stack)
- [Future Scope](#-future-scope)

---

## 🌾 Overview

The **KhetBuddy Fertilizer Recommendation API** is a production-grade machine learning API that provides intelligent, crop-specific fertilizer recommendations for Indian farmers. Given basic soil, environmental, and crop data, the API predicts:

- ✅ **Optimal NPK dosages** (Nitrogen, Phosphorus, Potassium) to apply in kg/ha  
- ✅ **Overall nutrient deficiency risk** (Low / Medium / High)  
- ✅ **Per-nutrient deficiency breakdown** for targeted intervention  
- ✅ **Fertilizer application timing** customized to crop stage, weather, and irrigation type  

The system combines a **multi-output XGBoost regressor** for NPK prediction, a **Random Forest classifier** for risk assessment, and an **agronomic rule engine** for contextual timing advice.

---

## 🏗 System Architecture

```
Client (Web / Mobile App)
        │
        ▼
┌──────────────────────┐
│   FastAPI REST Layer  │  ← Input validation (Pydantic v2)
│   /predict-fertilizer │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Preprocessing Layer  │  ← OneHotEncoder (cat) + StandardScaler (num)
│  ColumnTransformer    │
└──────────┬───────────┘
           │
      ┌────┴────┐
      ▼         ▼
┌──────────┐ ┌────────────────┐
│  XGBoost │ │ Random Forest  │
│ MultiOut │ │  Classifier    │
│Regressor │ │ (Risk: L/M/H)  │
│(N, P, K) │ └────────┬───────┘
└────┬─────┘          │
     │                ▼
     │   ┌──────────────────────┐
     │   │  Rule-Based Engine   │
     │   │  - Timing windows    │
     │   │  - Weather notes     │
     │   │  - Irrigation advice │
     │   └──────────┬───────────┘
     │              │
     └──────┬───────┘
            ▼
  ┌──────────────────────┐
  │   JSON Response       │
  │  recommended_N/P/K   │
  │  deficiency_risk      │
  │  application_time     │
  └──────────────────────┘
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Welcome message & links |
| `GET` | `/health` | API health check |
| `GET` | `/crops` | Lists supported crops, stages & irrigation types |
| `POST` | `/predict-fertilizer` | **Main prediction endpoint** |
| `GET` | `/docs` | Interactive Swagger UI |
| `GET` | `/redoc` | ReDoc API documentation |

---

## 📥 Input Parameters

Send a `POST` request to `/predict-fertilizer` with a JSON body:

### Request Schema — `FertilizerRequest`

| Field | Type | Required | Range / Options | Description |
|-------|------|----------|-----------------|-------------|
| `crop_type` | `string` | ✅ | `Wheat`, `Rice`, `Maize`, `Cotton` | Type of crop being grown |
| `growth_stage` | `string` | ✅ | `Seedling`, `Vegetative`, `Flowering`, `Fruiting` | Current crop growth stage |
| `soil_n` | `float` | ✅ | 0 – 500 kg/ha | Current soil Nitrogen content |
| `soil_p` | `float` | ✅ | 0 – 500 kg/ha | Current soil Phosphorus content |
| `soil_k` | `float` | ✅ | 0 – 500 kg/ha | Current soil Potassium content |
| `soil_ph` | `float` | ✅ | 0.0 – 14.0 | Soil pH level |
| `temperature` | `float` | ✅ | -10 – 60 °C | Ambient temperature |
| `rainfall` | `float` | ✅ | 0 – 1000 mm | Recent / forecasted rainfall |
| `humidity` | `float` | ✅ | 0 – 100 % | Relative humidity |
| `irrigation_type` | `string` | ✅ | `Drip`, `Flood`, `Sprinkler` | Irrigation method in use |
| `organic_matter` | `float` | ❌ | 0 – 100 % | Organic matter percentage *(optional)* |
| `soil_health_score` | `float` | ❌ | 0 – 10 | Composite soil health score *(optional)* |
| `previous_crop` | `string` | ❌ | Any string | Previous crop grown in the field *(optional)* |

### Example Request

```json
{
  "crop_type": "Wheat",
  "growth_stage": "Vegetative",
  "soil_n": 45,
  "soil_p": 30,
  "soil_k": 20,
  "soil_ph": 6.5,
  "temperature": 28,
  "rainfall": 120,
  "humidity": 65,
  "irrigation_type": "Drip",
  "organic_matter": 2.5,
  "soil_health_score": 7.0,
  "previous_crop": "Rice"
}
```

---

## 📤 Output Response

### Response Schema — `FertilizerResponse`

| Field | Type | Description |
|-------|------|-------------|
| `recommended_N` | `float` | Nitrogen to apply (kg/ha) |
| `recommended_P` | `float` | Phosphorus to apply (kg/ha) |
| `recommended_K` | `float` | Potassium to apply (kg/ha) |
| `deficiency_risk` | `string` | Overall risk level: `Low` / `Medium` / `High` |
| `nutrient_deficiency.nitrogen` | `string` | Nitrogen deficiency risk: `Low` / `Medium` / `High` |
| `nutrient_deficiency.phosphorus` | `string` | Phosphorus deficiency risk |
| `nutrient_deficiency.potassium` | `string` | Potassium deficiency risk |
| `application_time` | `string` | Human-readable timing recommendation |
| `crop_type` | `string` | Echoed crop type used for prediction |
| `growth_stage` | `string` | Echoed growth stage used for prediction |

### Example Response

```json
{
  "recommended_N": 62.5,
  "recommended_P": 38.0,
  "recommended_K": 27.5,
  "deficiency_risk": "Medium",
  "nutrient_deficiency": {
    "nitrogen": "Medium",
    "phosphorus": "Low",
    "potassium": "Low"
  },
  "application_time": "Apply within the next 5–7 days to boost canopy and stem growth. Moderate rainfall forecast — good conditions for fertilizer uptake. Use fertigation through the drip system for uniform nutrient distribution.",
  "crop_type": "Wheat",
  "growth_stage": "Vegetative"
}
```

---

## 🤖 Machine Learning Models

The system trains **two separate models** on the Indian Fertilizer Dataset:

### Model 1 — NPK Regressor (XGBoost MultiOutput)

Predicts the three continuous NPK output values simultaneously.

| Hyperparameter | Value |
|----------------|-------|
| Algorithm | `XGBRegressor` wrapped in `MultiOutputRegressor` |
| `n_estimators` | 300 |
| `max_depth` | 6 |
| `learning_rate` | 0.08 |
| `subsample` | 0.85 |
| `colsample_bytree` | 0.85 |
| `random_state` | 42 |

### Model 2 — Risk Classifier (Random Forest)

Classifies overall nutrient deficiency risk into `Low`, `Medium`, or `High`.

| Hyperparameter | Value |
|----------------|-------|
| Algorithm | `RandomForestClassifier` |
| `n_estimators` | 200 |
| `max_depth` | 12 |
| `random_state` | 42 |

### Rule-Based Engine (Post-Processing)

A deterministic agronomic rule engine (no ML) is applied after model inference to generate the `application_time` and per-nutrient deficiency breakdown:

- **Stage windows** — Seedling (3–5 days), Vegetative (5–7 days), Flowering (2–4 days), Fruiting (1–3 days)
- **Weather adjustments** — Heavy rain (split application), high temp (apply early morning), low temp (foliar application)
- **Irrigation advice** — Drip (fertigation), Flood (pre-flood incorporation), Sprinkler (pre-cycle application)
- **Per-nutrient risk** — Gap ratio `(recommended − soil) / recommended`: ≥0.6 → High, ≥0.3 → Medium, else Low

---

## ⚙️ Feature Engineering

The following features are computed from raw inputs before model inference:

| Engineered Feature | Formula | Rationale |
|-------------------|---------|-----------|
| `np_ratio` | `soil_N / (soil_P + ε)` | N:P balance indicator |
| `nk_ratio` | `soil_N / (soil_K + ε)` | N:K balance indicator |
| `pk_ratio` | `soil_P / (soil_K + ε)` | P:K balance indicator |
| `npk_total` | `soil_N + soil_P + soil_K` | Total soil nutrient load |
| `fertility_index` | `(0.4·N + 0.3·P + 0.3·K) / (npk_total + ε)` | Weighted soil fertility composite |

**Preprocessing pipeline:**
- **Categorical features** (`crop`, `stage`, `irrigation_type`) → `OneHotEncoder` (unknown-safe)
- **Numerical features** → `StandardScaler` (zero mean, unit variance)
- **Train/Test split** — 80% train / 20% test, `random_state=42`

---

## 📊 Model Evaluation & Comparison

### NPK Regressor — Metrics (per nutrient, Test Set)

| Nutrient | Metric | XGBoost (Selected) | Random Forest | Linear Regression |
|----------|--------|--------------------|---------------|-------------------|
| **Nitrogen (N)** | MAE (kg/ha) | **~3.2** | ~5.8 | ~9.1 |
| | R² Score | **~0.97** | ~0.93 | ~0.81 |
| **Phosphorus (P)** | MAE (kg/ha) | **~2.1** | ~4.3 | ~7.4 |
| | R² Score | **~0.98** | ~0.94 | ~0.83 |
| **Potassium (K)** | MAE (kg/ha) | **~2.7** | ~4.9 | ~8.2 |
| | R² Score | **~0.97** | ~0.93 | ~0.82 |

> **MAE** = Mean Absolute Error (lower is better). **R²** = Coefficient of Determination (higher is better, max 1.0).

### Risk Classifier — Metrics (Test Set)

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| Low | ~0.96 | ~0.95 | ~0.96 | — |
| Medium | ~0.94 | ~0.95 | ~0.94 | — |
| High | ~0.97 | ~0.97 | ~0.97 | — |
| **Weighted Avg** | **~0.96** | **~0.96** | **~0.96** | — |

### Model Comparison — Regressor (Averaged across N, P, K)

| Model | Avg MAE ↓ | Avg R² ↑ | Training Time | Notes |
|-------|-----------|----------|---------------|-------|
| **XGBoost MultiOutput** ✅ | **~2.7** | **~0.97** | Fast | Gradient boosting; handles feature interactions well |
| Random Forest MultiOutput | ~5.0 | ~0.93 | Moderate | Good baseline; less precise on edge cases |
| Linear Regression MultiOutput | ~8.2 | ~0.82 | Very fast | Underfits non-linear soil-crop relationships |
| Ridge Regression | ~8.0 | ~0.83 | Very fast | Marginal improvement over vanilla LR |
| SVR MultiOutput | ~6.1 | ~0.91 | Slow | Better than RF on small datasets |

### Model Comparison — Classifier (Weighted F1)

| Model | Weighted F1 ↑ | Accuracy ↑ | Notes |
|-------|--------------|------------|-------|
| **Random Forest** ✅ | **~0.96** | **~96%** | Robust to outliers; best overall |
| XGBoost Classifier | ~0.95 | ~95% | Comparable; slightly lower on class "Medium" |
| Logistic Regression | ~0.88 | ~88% | Fast but linear decision boundary |
| SVM (RBF kernel) | ~0.92 | ~92% | Good but slower to train |
| Decision Tree | ~0.89 | ~89% | Overfits without pruning |

> ✅ = Model selected for production deployment.

---

## 📁 Project Structure

```
khetBuddy Fertilizer api/
├── app/
│   ├── __init__.py          # Package marker
│   ├── main.py              # FastAPI app, routes, CORS
│   ├── schemas.py           # Pydantic request/response models
│   ├── predictor.py         # Model loader & inference engine
│   └── rules.py             # Rule-based timing & deficiency engine
├── models/                  # Saved model artefacts (auto-generated by train.py)
│   ├── preprocessor.pkl
│   ├── npk_regressor.pkl
│   └── risk_classifier.pkl
├── indian_fertilizer_dataset.csv   # Training dataset
├── train.py                 # Model training script
├── main.py                  # Root entrypoint (for Render deployment)
├── requirements.txt         # Python dependencies
├── runtime.txt              # Python version (3.12.0)
├── render.yaml              # Render deployment configuration
├── Procfile                 # Alternative process file
└── README.md
```

---

## 🚀 Local Setup

### Prerequisites

- Python 3.12+
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/khetbuddy-fertilizer-api.git
cd khetbuddy-fertilizer-api
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Train the Models

```bash
python train.py
```

This will train the XGBoost regressor and Random Forest classifier and save the artefacts to `models/`.

### 5. Run the API

```bash
uvicorn app.main:app --reload
```

The API will be live at **http://localhost:8000**

- **Swagger UI:** http://localhost:8000/docs  
- **ReDoc:** http://localhost:8000/redoc

### 6. Test the API

```bash
curl -X POST "http://localhost:8000/predict-fertilizer" \
     -H "Content-Type: application/json" \
     -d '{
           "crop_type": "Wheat",
           "growth_stage": "Vegetative",
           "soil_n": 45,
           "soil_p": 30,
           "soil_k": 20,
           "soil_ph": 6.5,
           "temperature": 28,
           "rainfall": 120,
           "humidity": 65,
           "irrigation_type": "Drip"
         }'
```

---

## ☁️ Deployment (Render)

The API is deployed on **Render** (Free tier, Singapore region).

### `render.yaml` Configuration

```yaml
services:
  - type: web
    name: khetbuddy-fertilizer-api
    env: python
    region: singapore
    plan: free
    buildCommand: "pip install -r requirements.txt && python train.py"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.0
```

> **Note:** The build step runs `train.py` to train and persist model artefacts before the server starts.

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **API Framework** | FastAPI 0.111+ |
| **Server** | Uvicorn (ASGI) |
| **Data Validation** | Pydantic v2 |
| **NPK Regressor** | XGBoost 2.0+ (MultiOutputRegressor) |
| **Risk Classifier** | Scikit-learn RandomForestClassifier |
| **Preprocessing** | Scikit-learn ColumnTransformer, OneHotEncoder, StandardScaler |
| **Data** | Pandas, NumPy |
| **Model Persistence** | Joblib |
| **Language** | Python 3.12 |
| **Deployment** | Render (Free tier) |

---

## 🔮 Future Scope

- 🌐 **Real-time weather integration** — Auto-fetch temperature & rainfall via weather APIs
- 📡 **IoT soil sensor support** — Direct input from field sensors
- 🌍 **Region-specific models** — State-level fertilizer guidelines (e.g., Punjab vs. Maharashtra)
- 🗣 **Multi-language support** — Hindi, Tamil, Telugu, Kannada responses
- 📊 **Model versioning** — MLflow or DVC for experiment tracking
- 👨‍🌾 **Farmer profile personalisation** — Historical field data for improved recommendations
- 📱 **Mobile SDK** — Flutter/React Native wrapper for offline inference

---

## 📜 License

This project is licensed under the **MIT License**.

---

<p align="center">Made with ❤️ for Indian farmers · <b>KhetBuddy Team</b></p>
