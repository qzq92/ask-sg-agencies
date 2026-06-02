"""Shared helpers for data.gov.sg API responses."""

import requests

DATA_GOV_SG_API_BASE = "https://api-production.data.gov.sg"


def api_ok(data: dict) -> bool:
    """Return True when the API response indicates success."""
    code = data.get("code")
    return code in (0, 200)


def api_error(data: dict, fallback: str = "Request failed") -> str:
    return f"Error: {data.get('errorMsg') or fallback}"


def agency_name(record: dict) -> str:
    """Extract managing agency name from a dataset or collection record."""
    return (
        record.get("managedByAgencyName")
        or record.get("managedByText")
        or record.get("managedBy")
        or "Unknown"
    )


def matches_agency(record: dict, agency_terms: list[str]) -> bool:
    """Return True if any agency term appears in the record's agency fields."""
    haystack = " ".join(
        [
            agency_name(record),
            " ".join(record.get("sources", [])),
        ]
    ).lower()
    return any(term.lower() in haystack for term in agency_terms)


def get_json(url: str, params: dict | None = None, timeout: int = 15) -> dict:
    resp = requests.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()
