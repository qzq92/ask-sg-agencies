"""Dataset metadata and search tools for data.gov.sg."""

from __future__ import annotations

from langchain_core.tools import tool

from config.agency_mapping import get_agency_search_terms
from tools.collection import load_all_collections, rank_collections
from tools.datagov_api import (
    DATA_GOV_SG_API_BASE,
    DataGovApiError,
    agency_name,
    api_error,
    api_ok,
    matches_agency,
    request_json,
)


@tool
def get_dataset_metadata(dataset_id: str) -> str:
    """Fetch column-level metadata for a dataset from data.gov.sg.

    Use this when you need schema details (column names, data types, coverage period)
    for a specific dataset. The dataset_id is typically in the format d_xxxxxxxx.

    Args:
        dataset_id: The unique identifier of the dataset (e.g. d_8b84c4ee58e3cfc0ece0d773c8ca6abc)
    """
    url = f"{DATA_GOV_SG_API_BASE}/v2/public/api/datasets/{dataset_id}/metadata"
    try:
        data = request_json(url, timeout=10)
        if not api_ok(data) or "data" not in data:
            return api_error(data, "Unknown error")
        meta = data["data"]
        parts = [
            f"Dataset: {meta.get('name', 'N/A')}",
            f"Format: {meta.get('format', 'N/A')}",
            f"Last updated: {meta.get('lastUpdatedAt', 'N/A')}",
            f"Coverage: {meta.get('coverageStart', 'N/A')} to {meta.get('coverageEnd', 'N/A')}",
        ]
        column_metadata = meta.get("columnMetadata")
        if column_metadata and column_metadata.get("order"):
            parts.append("Columns: " + ", ".join(column_metadata["order"]))
        return "\n".join(parts)
    except DataGovApiError as exc:
        return f"Failed to fetch metadata: {exc}"


@tool
def search_datasets(query: str, agency: str = "", limit: int = 10) -> str:
    """Search for datasets on data.gov.sg by keywords and optionally filter by agency.

    Use this to discover relevant datasets based on search terms. Optionally filter
    by the managing agency (e.g., HDB, LTA, MOH).

    Args:
        query: Search keywords to find relevant datasets
        agency: Optional agency name/acronym to filter results (e.g., "HDB", "LTA", "MOH")
        limit: Maximum number of results to return (default 10)
    """
    url = f"{DATA_GOV_SG_API_BASE}/v2/public/api/datasets"
    params = {
        "query": query,
        "resultSize": min(limit, 20),
    }

    try:
        data = request_json(url, params=params, timeout=15)
        if not api_ok(data):
            return api_error(data, "Search failed")

        datasets = data.get("data", {}).get("datasets", [])

        if agency:
            agency_terms = get_agency_search_terms(agency)
            datasets = [ds for ds in datasets if matches_agency(ds, agency_terms)]

        if not datasets:
            filter_msg = f" from {agency}" if agency else ""
            return f"No datasets found{filter_msg} matching '{query}'"

        results = []
        for ds in datasets[:limit]:
            ds_id = ds.get("datasetId", "N/A")
            name = ds.get("name", "Untitled")
            managed_by = agency_name(ds)
            description = ds.get("description", "")[:150]
            if len(ds.get("description", "")) > 150:
                description += "..."

            link = f"https://data.gov.sg/datasets/{ds_id}/view"
            results.append(
                f"- **{name}**\n"
                f"  ID: {ds_id}\n"
                f"  Agency: {managed_by}\n"
                f"  Description: {description}\n"
                f"  Link: {link}"
            )

        header = f"Found {len(datasets)} dataset(s)"
        if agency:
            header += f" from {agency}"
        header += f" matching '{query}':\n\n"

        return header + "\n\n".join(results)

    except DataGovApiError as exc:
        return f"Failed to search datasets: {exc}"


@tool
def list_datasets_by_agency(agency: str, limit: int = 15) -> str:
    """List all datasets managed by a specific Singapore government agency.

    Use this to browse all available datasets from a particular agency like HDB, LTA, MOH, etc.

    Args:
        agency: Agency name or acronym (e.g., "HDB", "LTA", "MOH", "NEA")
        limit: Maximum number of results to return (default 15)
    """
    url = f"{DATA_GOV_SG_API_BASE}/v2/public/api/datasets"
    params = {
        "query": agency,
        "resultSize": 50,
    }

    try:
        data = request_json(url, params=params, timeout=15)
        if not api_ok(data):
            return api_error(data, "Search failed")

        datasets = data.get("data", {}).get("datasets", [])
        agency_terms = get_agency_search_terms(agency)
        filtered = [ds for ds in datasets if matches_agency(ds, agency_terms)]

        if not filtered:
            collections = load_all_collections()
            matched = rank_collections(agency, collections)
            if matched:
                results = []
                for _, col in matched[:limit]:
                    collection_id = col.get("collectionId", "N/A")
                    name = col.get("name", "Untitled")
                    collection_link = f"https://data.gov.sg/collections/{collection_id}/view"
                    child_ids = col.get("childDatasets", [])
                    child_links = ", ".join(
                        f"https://data.gov.sg/datasets/{ds_id}/view"
                        for ds_id in child_ids[:3]
                    )
                    suffix = f" (+{len(child_ids) - 3} more datasets)" if len(child_ids) > 3 else ""
                    results.append(
                        f"- [{name}]({collection_link}) - "
                        f"Collection ID: {collection_id}"
                        + (f" | Datasets: {child_links}{suffix}" if child_links else "")
                    )
                return (
                    f"Collections from {agency} on data.gov.sg ({len(matched)} matched):\n\n"
                    + "\n".join(results)
                )

            return f"No datasets found managed by {agency}"

        results = []
        for ds in filtered[:limit]:
            ds_id = ds.get("datasetId", "N/A")
            name = ds.get("name", "Untitled")
            format_type = ds.get("format", "Unknown")
            link = f"https://data.gov.sg/datasets/{ds_id}/view"

            results.append(f"- [{name}]({link}) ({format_type}) - ID: {ds_id}")

        return f"Datasets from {agency} ({len(filtered)} found):\n\n" + "\n".join(results)

    except DataGovApiError as exc:
        return f"Failed to list datasets: {exc}"
