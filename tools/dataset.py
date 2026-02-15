"""Dataset metadata lookup tool for data.gov.sg."""

import requests
from langchain_core.tools import tool

DATA_GOV_SG_API_BASE = "https://api-production.data.gov.sg"


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
