"""Agency-to-category mapping for Singapore government agencies.

Maps agency acronyms and full names to their primary data.gov.sg categories.
Used by the supervisor to improve routing when users mention specific agencies.
"""

AGENCY_TO_CATEGORY: dict[str, str] = {
    # Housing
    "HDB": "housing",
    "Housing & Development Board": "housing",
    "Housing and Development Board": "housing",
    "URA": "housing",
    "Urban Redevelopment Authority": "housing",
    "SLA": "housing",
    "Singapore Land Authority": "housing",
    
    # Transport
    "LTA": "transport",
    "Land Transport Authority": "transport",
    "SMRT": "transport",
    "SBS Transit": "transport",
    "ComfortDelGro": "transport",
    
    # Health
    "MOH": "health",
    "Ministry of Health": "health",
    "HPB": "health",
    "Health Promotion Board": "health",
    "HSA": "health",
    "Health Sciences Authority": "health",
    
    # Environment
    "NEA": "environment",
    "National Environment Agency": "environment",
    "PUB": "environment",
    "NParks": "environment",
    "National Parks Board": "environment",
    "MSS": "environment",
    "Meteorological Service Singapore": "environment",
    
    # Education
    "MOE": "education",
    "Ministry of Education": "education",
    "SkillsFuture": "education",
    "SkillsFuture Singapore": "education",
    "SSG": "education",
    "ITE": "education",
    "Institute of Technical Education": "education",
    
    # Economy
    "ACRA": "economy",
    "Accounting and Corporate Regulatory Authority": "economy",
    "EDB": "economy",
    "Economic Development Board": "economy",
    "ESG": "economy",
    "Enterprise Singapore": "economy",
    "MAS": "economy",
    "Monetary Authority of Singapore": "economy",
    "IRAS": "economy",
    "Inland Revenue Authority of Singapore": "economy",
    "MTI": "economy",
    "Ministry of Trade and Industry": "economy",
    "STB": "economy",
    "Singapore Tourism Board": "economy",
    
    # Manpower (maps to economy as closest match)
    "MOM": "economy",
    "Ministry of Manpower": "economy",
    "CPF": "economy",
    "Central Provident Fund": "economy",
    "CPF Board": "economy",
    
    # Social
    "MSF": "social",
    "Ministry of Social and Family Development": "social",
    "NCSS": "social",
    "National Council of Social Service": "social",
    
    # Arts & Culture
    "MCCY": "arts_culture",
    "Ministry of Culture, Community and Youth": "arts_culture",
    "NAC": "arts_culture",
    "National Arts Council": "arts_culture",
    "NHB": "arts_culture",
    "National Heritage Board": "arts_culture",
    "NLB": "arts_culture",
    "National Library Board": "arts_culture",
    
    # Technology / Digital (maps to realtime_apis as closest match for data)
    "GovTech": "realtime_apis",
    "Government Technology Agency": "realtime_apis",
    "IMDA": "realtime_apis",
    "Infocomm Media Development Authority": "realtime_apis",
    
    # Geospatial (Note: SLA also appears under housing - primary mapping is housing)
    "OneMap": "geospatial",
}

CATEGORY_ALIASES: dict[str, str] = {
    "property": "housing",
    "real estate": "housing",
    "flat": "housing",
    "bto": "housing",
    "resale": "housing",
    
    "traffic": "transport",
    "bus": "transport",
    "mrt": "transport",
    "taxi": "transport",
    "parking": "transport",
    
    "hospital": "health",
    "clinic": "health",
    "disease": "health",
    "covid": "health",
    "medical": "health",
    
    "weather": "environment",
    "air quality": "environment",
    "psi": "environment",
    "climate": "environment",
    "water": "environment",
    
    "school": "education",
    "university": "education",
    "polytechnic": "education",
    "exam": "education",
    "student": "education",
    
    "business": "economy",
    "company": "economy",
    "trade": "economy",
    "gdp": "economy",
    "employment": "economy",
    "job": "economy",
    "tax": "economy",
    
    "population": "social",
    "demographic": "social",
    "family": "social",
    "elderly": "social",
    "community": "social",
    
    "museum": "arts_culture",
    "heritage": "arts_culture",
    "library": "arts_culture",
    
    "map": "geospatial",
    "location": "geospatial",
    "coordinates": "geospatial",
    "boundary": "geospatial",
    
    "api": "realtime_apis",
    "real-time": "realtime_apis",
    "live": "realtime_apis",
}


def get_categories_for_agencies(text: str) -> list[str]:
    """Extract categories based on agency mentions in text.
    
    Args:
        text: User query or input text to scan for agency mentions.
        
    Returns:
        List of unique category keys found, or empty list if none.
    """
    text_upper = text.upper()
    text_lower = text.lower()
    found_categories = set()
    
    for agency, category in AGENCY_TO_CATEGORY.items():
        if agency.upper() in text_upper or agency in text:
            found_categories.add(category)
    
    for alias, category in CATEGORY_ALIASES.items():
        if alias in text_lower:
            found_categories.add(category)
    
    return list(found_categories)


def get_all_agencies() -> list[str]:
    """Return list of all known agency acronyms."""
    acronyms = set()
    for agency in AGENCY_TO_CATEGORY.keys():
        if agency.isupper() or len(agency) <= 5:
            acronyms.add(agency)
    return sorted(acronyms)
