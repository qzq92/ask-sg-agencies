"""Shared types and helpers for data.gov.sg API responses."""

from __future__ import annotations

from typing import Any, TypedDict

import requests


DATA_GOV_SG_API_BASE = "https://api-production.data.gov.sg"
MAX_COLLECTION_PAGES = 200


class DataGovApiError(Exception):
    """Raised when a data.gov.sg API request or response is invalid."""


class ApiEnvelope(TypedDict, total=False):
    code: int
    data: dict[str, Any]
    errorMsg: str


class CollectionRecord(TypedDict, total=False):
    collectionId: str
    name: str
    description: str
    managedByAgencyName: str
    sources: list[str]
    childDatasets: list[str]
    createdAt: str
    lastUpdatedAt: str
    frequency: str


class DatasetRecord(TypedDict, total=False):
    datasetId: str
    name: str
    description: str
    format: str
    managedByAgencyName: str
    managedByText: str
    managedBy: str
    sources: list[str]
    lastUpdatedAt: str
    coverageStart: str
    coverageEnd: str


def api_ok(data: ApiEnvelope | dict[str, Any]) -> bool:
    """Return True when the API response indicates success."""
    code = data.get("code")
    return code in (0, 200)


def api_error(data: ApiEnvelope | dict[str, Any], fallback: str = "Request failed") -> str:
    message = data.get("errorMsg") or fallback
    return f"Error: {message}"


def agency_name(record: DatasetRecord | CollectionRecord | dict[str, Any]) -> str:
    """Extract managing agency name from a dataset or collection record."""
    return (
        record.get("managedByAgencyName")
        or record.get("managedByText")
        or record.get("managedBy")
        or "Unknown"
    )


def matches_agency(record: DatasetRecord | CollectionRecord | dict[str, Any], agency_terms: list[str]) -> bool:
    """Return True if any agency term appears in the record's agency fields."""
    sources = record.get("sources", [])
    haystack = " ".join([agency_name(record), " ".join(sources)]).lower()
    return any(term.lower() in haystack for term in agency_terms)


def request_json(
    url: str,
    params: dict[str, str | int] | None = None,
    timeout: int = 15,
) -> dict[str, Any]:
    """Perform a GET request and return parsed JSON, raising DataGovApiError on failure."""
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
    except requests.Timeout as exc:
        raise DataGovApiError(f"Request timed out after {timeout}s: {url}") from exc
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        raise DataGovApiError(f"HTTP {status} for {url}") from exc
    except requests.RequestException as exc:
        raise DataGovApiError(f"Network error for {url}: {exc}") from exc

    try:
        payload: dict[str, Any] = response.json()
    except ValueError as exc:
        raise DataGovApiError(f"Invalid JSON response from {url}") from exc

    return payload


def get_json(url: str, params: dict[str, str | int] | None = None, timeout: int = 15) -> dict[str, Any]:
    """Backward-compatible alias for request_json."""
    return request_json(url, params=params, timeout=timeout)
