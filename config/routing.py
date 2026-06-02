"""Routing configuration for multi-category supervisor handover."""

MAX_ROUTED_CATEGORIES = 3

CATEGORY_LABELS: dict[str, str] = {
    "arts_culture": "Arts & Culture",
    "education": "Education",
    "economy": "Economy",
    "environment": "Environment",
    "geospatial": "Geospatial",
    "housing": "Housing",
    "health": "Health",
    "social": "Social",
    "transport": "Transport",
    "realtime_apis": "Real-time APIs",
}
