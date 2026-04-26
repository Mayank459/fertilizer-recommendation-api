"""
KhetBuddy Fertilizer Recommendation API
FastAPI application entry point.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.schemas import FertilizerRequest, FertilizerResponse
from app.predictor import predict

# ─────────────────────────────────────────────────────────────────────────────
# App initialisation
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="🌱 KhetBuddy Fertilizer Recommendation API",
    description=(
        "Intelligent, data-driven fertilizer recommendations for Indian crops. "
        "Predicts optimal N, P, K values, nutrient deficiency risks, and application timing "
        "using machine learning trained on the Indian Fertilizer Dataset."
    ),
    version="1.0.0",
    contact={
        "name":  "KhetBuddy Team",
        "email": "support@khetbuddy.in",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS — allow all origins for easy integration with web/mobile apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────────────────────────────────────
@app.get(
    "/health",
    tags=["System"],
    summary="API health check",
    response_description="Returns API status and version",
)
def health_check():
    return {"status": "healthy", "version": "1.0.0", "service": "KhetBuddy Fertilizer API"}


# ─────────────────────────────────────────────────────────────────────────────
# Metadata endpoints
# ─────────────────────────────────────────────────────────────────────────────
@app.get(
    "/crops",
    tags=["Metadata"],
    summary="List supported crop types",
)
def list_crops():
    return {
        "crops": ["Wheat", "Rice", "Maize", "Cotton"],
        "growth_stages": ["Seedling", "Vegetative", "Flowering", "Fruiting"],
        "irrigation_types": ["Drip", "Flood", "Sprinkler"],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Core prediction endpoint
# ─────────────────────────────────────────────────────────────────────────────
@app.post(
    "/predict-fertilizer",
    response_model=FertilizerResponse,
    tags=["Prediction"],
    summary="Get fertilizer recommendation",
    response_description="Recommended NPK values, deficiency risk, and application timing",
)
def predict_fertilizer(request: FertilizerRequest) -> FertilizerResponse:
    """
    ### Fertilizer Recommendation

    Provide crop, soil, and environmental details to receive:

    - **Recommended N / P / K** values to apply (kg/ha)
    - **Overall deficiency risk** (Low / Medium / High)
    - **Per-nutrient deficiency breakdown** (Nitrogen, Phosphorus, Potassium)
    - **Application timing window** with irrigation-specific advice

    ---

    **Supported crops:** Wheat, Rice, Maize, Cotton

    **Supported growth stages:** Seedling, Vegetative, Flowering, Fruiting

    **Supported irrigation types:** Drip, Flood, Sprinkler
    """
    try:
        result = predict(request)
        return result
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Model artefacts not found. "
                "Please run 'python train.py' to train and save the models first. "
                f"Detail: {exc}"
            ),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# Root redirect to docs
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    return JSONResponse(
        content={
            "message": "Welcome to the KhetBuddy Fertilizer Recommendation API 🌱",
            "docs":    "http://localhost:8000/docs",
            "health":  "http://localhost:8000/health",
        }
    )
