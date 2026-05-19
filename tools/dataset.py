"""Dataset metadata and search tools for data.gov.sg."""

import requests
from langchain_core.tools import tool

DATA_GOV_SG_API_BASE = "https://api-production.data.gov.sg"
DATA_GOV_SG_SEARCH_BASE = "https://data.gov.sg/api/action"


@tool
def get_dataset_metadata(dataset_id: str) -> str:
    """Fetch column-level metadata for a dataset from data.gov.sg.

    Use this when you need schema details (column names, data types, coverage period)
    for a specific dataset. The dataset_id is typically in the format d_xxxxxxxx.

    Args:
        dataset_id: The unique identifier of the dataset (e.g. d_8b84c4ee58e3cfc0ece0d773c8ca6abc)
    """

    # Example: https://api-production.data.gov.sg/v2/public/api/datasets/d_9e7de44094f876f6804b8b5bcee45c81/metadata
    url = f"{DATA_GOV_SG_API_BASE}/v2/public/api/datasets/{dataset_id}/metadata"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 200 or "data" not in data:
            return f"Error: {data.get('errorMsg', 'Unknown error')}"
        meta = data["data"]
        parts = [
            f"Dataset: {meta.get('name', 'N/A')}",
            f"Format: {meta.get('format', 'N/A')}",
            f"Last updated: {meta.get('lastUpdatedAt', 'N/A')}",
            f"Coverage: {meta.get('coverageStart', 'N/A')} to {meta.get('coverageEnd', 'N/A')}",
        ]
        if "columnMetadata" in meta and meta["columnMetadata"]:
            cm = meta["columnMetadata"]
            if "order" in cm:
                parts.append("Columns: " + ", ".join(cm["order"]))
        return "\n".join(parts)
    except requests.RequestException as e:
        return f"Failed to fetch metadata: {e}"


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
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("code") != 200:
            return f"Error: {data.get('errorMsg', 'Search failed')}"
        
        datasets = data.get("data", {}).get("datasets", [])
        
        if agency:
            agency_lower = agency.lower()
            datasets = [
                ds for ds in datasets
                if agency_lower in ds.get("managedBy", "").lower()
                or agency_lower in ds.get("managedByText", "").lower()
            ]
        
        if not datasets:
            filter_msg = f" from {agency}" if agency else ""
            return f"No datasets found{filter_msg} matching '{query}'"
        
        results = []
        for ds in datasets[:limit]:
            ds_id = ds.get("datasetId", "N/A")
            name = ds.get("name", "Untitled")
            managed_by = ds.get("managedByText", ds.get("managedBy", "Unknown"))
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
        
    except requests.RequestException as e:
        return f"Failed to search datasets: {e}"


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
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("code") != 200:
            return f"Error: {data.get('errorMsg', 'Search failed')}"
        
        datasets = data.get("data", {}).get("datasets", [])
        
        agency_lower = agency.lower()
        filtered = [
            ds for ds in datasets
            if agency_lower in ds.get("managedBy", "").lower()
            or agency_lower in ds.get("managedByText", "").lower()
        ]
        
        if not filtered:
            return f"No datasets found managed by {agency}"
        
        results = []
        for ds in filtered[:limit]:
            ds_id = ds.get("datasetId", "N/A")
            name = ds.get("name", "Untitled")
            format_type = ds.get("format", "Unknown")
            link = f"https://data.gov.sg/datasets/{ds_id}/view"
            
            results.append(f"- [{name}]({link}) ({format_type}) - ID: {ds_id}")
        
        return f"Datasets from {agency} ({len(filtered)} found):\n\n" + "\n".join(results)
        
    except requests.RequestException as e:
        return f"Failed to list datasets: {e}"
