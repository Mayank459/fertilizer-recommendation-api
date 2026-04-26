"""
Rule-based post-processing engine.
Derives application timing recommendations from agronomic logic.
"""
from typing import Dict


# ─────────────────────────────────────────────────────────────────────────────
# Stage-based base windows (in days from "now")
# ─────────────────────────────────────────────────────────────────────────────
_STAGE_WINDOWS: Dict[str, str] = {
    "Seedling":   "Apply within the next 3–5 days to support early root establishment.",
    "Vegetative": "Apply within the next 5–7 days to boost canopy and stem growth.",
    "Flowering":  "Apply within the next 2–4 days; avoid late application to prevent flower drop.",
    "Fruiting":   "Apply immediately (within 1–3 days) to maximise fruit fill and quality.",
}

# ─────────────────────────────────────────────────────────────────────────────
# Environmental adjustment messages
# ─────────────────────────────────────────────────────────────────────────────
def _weather_note(temperature: float, rainfall: float) -> str:
    notes = []
    if rainfall > 150:
        notes.append("heavy rainfall expected — split application recommended to prevent leaching")
    elif rainfall > 80:
        notes.append("moderate rainfall forecast — good conditions for fertilizer uptake")
    else:
        notes.append("low rainfall — ensure adequate irrigation before application")

    if temperature > 38:
        notes.append("high temperature — apply early morning or evening to reduce volatilisation losses")
    elif temperature < 12:
        notes.append("low temperature — nutrient uptake may be slow; consider foliar application")

    return "; ".join(notes).capitalize() + "." if notes else ""


def _irrigation_note(irrigation_type: str) -> str:
    return {
        "Drip":      "Use fertigation through the drip system for uniform nutrient distribution.",
        "Flood":     "Apply before flooding; incorporate into soil to minimise runoff.",
        "Sprinkler": "Apply just before a sprinkler cycle for even foliar distribution.",
    }.get(irrigation_type, "")


# ─────────────────────────────────────────────────────────────────────────────
# Public function
# ─────────────────────────────────────────────────────────────────────────────
def get_application_timing(
    growth_stage: str,
    temperature: float,
    rainfall: float,
    irrigation_type: str,
) -> str:
    """
    Combine stage-based window with environmental and irrigation notes.

    Returns:
        A human-readable application timing recommendation string.
    """
    base   = _STAGE_WINDOWS.get(growth_stage, "Apply as soon as possible.")
    weather  = _weather_note(temperature, rainfall)
    irr    = _irrigation_note(irrigation_type)

    parts = [base]
    if weather:
        parts.append(weather)
    if irr:
        parts.append(irr)

    return " ".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Per-nutrient deficiency risk from soil vs recommended gap
# ─────────────────────────────────────────────────────────────────────────────
def nutrient_risk(soil_val: float, recommended_val: float) -> str:
    """Classify per-nutrient deficiency risk based on gap ratio."""
    if recommended_val == 0:
        return "Low"
    gap_ratio = (recommended_val - soil_val) / recommended_val
    if gap_ratio >= 0.6:
        return "High"
    elif gap_ratio >= 0.3:
        return "Medium"
    else:
        return "Low"
