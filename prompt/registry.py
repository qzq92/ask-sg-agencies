"""Prompt registry: maps category keys to system prompts."""

from prompt import arts_culture, education, economy, environment, geospatial
from prompt import housing, health, social, transport, realtime_apis

CATEGORY_KEYS = [
    "arts_culture",
    "education",
    "economy",
    "environment",
    "geospatial",
    "housing",
    "health",
    "social",
    "transport",
    "realtime_apis",
]

_PROMPTS = {
    "arts_culture": arts_culture.ARTS_CULTURE_SYSTEM_PROMPT,
    "education": education.EDUCATION_SYSTEM_PROMPT,
    "economy": economy.ECONOMY_SYSTEM_PROMPT,
    "environment": environment.ENVIRONMENT_SYSTEM_PROMPT,
    "geospatial": geospatial.GEOSPATIAL_SYSTEM_PROMPT,
    "housing": housing.HOUSING_SYSTEM_PROMPT,
    "health": health.HEALTH_SYSTEM_PROMPT,
    "social": social.SOCIAL_SYSTEM_PROMPT,
    "transport": transport.TRANSPORT_SYSTEM_PROMPT,
    "realtime_apis": realtime_apis.REALTIME_APIS_SYSTEM_PROMPT,
}


def get_prompt(category_key: str) -> str:
    """Return the system prompt for a category."""
    if category_key not in _PROMPTS:
        raise ValueError(f"Unknown category: {category_key}")
    return _PROMPTS[category_key]
