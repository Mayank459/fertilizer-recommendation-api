"""
Pydantic schemas for the KhetBuddy Fertilizer Recommendation API.
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


# ─────────────────────────────────────────────────────────────────────────────
# Valid enum values (kept as literals for clear Swagger docs)
# ─────────────────────────────────────────────────────────────────────────────
CropType        = Literal["Wheat", "Rice", "Maize", "Cotton"]
GrowthStage     = Literal["Seedling", "Vegetative", "Flowering", "Fruiting"]
IrrigationType  = Literal["Drip", "Flood", "Sprinkler"]
RiskLevel       = Literal["Low", "Medium", "High"]


# ─────────────────────────────────────────────────────────────────────────────
# Request
# ─────────────────────────────────────────────────────────────────────────────
class FertilizerRequest(BaseModel):
    """Input payload for fertilizer recommendation."""

    # Crop information
    crop_type:    CropType    = Field(..., example="Wheat", description="Type of crop being grown")
    growth_stage: GrowthStage = Field(..., example="Vegetative", description="Current growth stage of the crop")

    # Soil data
    soil_n: float = Field(..., ge=0, le=500, example=45, description="Current soil Nitrogen content (kg/ha)")
    soil_p: float = Field(..., ge=0, le=500, example=30, description="Current soil Phosphorus content (kg/ha)")
    soil_k: float = Field(..., ge=0, le=500, example=20, description="Current soil Potassium content (kg/ha)")
    soil_ph: float = Field(..., ge=0.0, le=14.0, example=6.5, description="Soil pH level (0–14)")

    # Environmental data
    temperature: float = Field(..., ge=-10, le=60, example=28, description="Current temperature in °C")
    rainfall:    float = Field(..., ge=0, le=1000, example=120, description="Recent or forecasted rainfall in mm")
    humidity:    float = Field(..., ge=0, le=100, example=65, description="Relative humidity percentage")

    # Farming practices
    irrigation_type: IrrigationType = Field(..., example="Drip", description="Irrigation method in use")

    # Optional fields
    organic_matter:    Optional[float] = Field(None, ge=0, le=100, example=2.5, description="Organic matter percentage (optional)")
    soil_health_score: Optional[float] = Field(None, ge=0, le=10, example=7.0, description="Composite soil health score 0–10 (optional)")
    previous_crop:     Optional[str]   = Field(None, example="Wheat", description="Previous crop grown in the field (optional)")

    @field_validator("crop_type", mode="before")
    @classmethod
    def normalise_crop(cls, v: str) -> str:
        return v.strip().title()

    @field_validator("growth_stage", mode="before")
    @classmethod
    def normalise_stage(cls, v: str) -> str:
        return v.strip().title()

    @field_validator("irrigation_type", mode="before")
    @classmethod
    def normalise_irrigation(cls, v: str) -> str:
        return v.strip().title()


# ─────────────────────────────────────────────────────────────────────────────
# Response
# ─────────────────────────────────────────────────────────────────────────────
class NutrientDeficiencyDetail(BaseModel):
    nitrogen:   RiskLevel
    phosphorus: RiskLevel
    potassium:  RiskLevel


class FertilizerResponse(BaseModel):
    """Fertilizer recommendation output."""

    # Primary NPK outputs
    recommended_N: float = Field(..., description="Recommended Nitrogen to apply (kg/ha)")
    recommended_P: float = Field(..., description="Recommended Phosphorus to apply (kg/ha)")
    recommended_K: float = Field(..., description="Recommended Potassium to apply (kg/ha)")

    # Risk assessment
    deficiency_risk:       RiskLevel               = Field(..., description="Overall nutrient deficiency risk level")
    nutrient_deficiency:   NutrientDeficiencyDetail = Field(..., description="Per-nutrient deficiency risk breakdown")

    # Timing recommendation
    application_time: str = Field(..., description="Recommended fertilizer application time window")

    # Metadata
    crop_type:    str = Field(..., description="Crop type used for prediction")
    growth_stage: str = Field(..., description="Growth stage used for prediction")
