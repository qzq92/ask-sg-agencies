"""Collection search tools for data.gov.sg."""

from __future__ import annotations

from difflib import SequenceMatcher

from langchain_core.tools import tool

from config.agency_mapping import get_agency_search_terms
from tools.datagov_api import (
    DATA_GOV_SG_API_BASE,
    MAX_COLLECTION_PAGES,
    CollectionRecord,
    DataGovApiError,
    api_ok,
    request_json,
)

_collections_cache: list[CollectionRecord] | None = None


def load_all_collections() -> list[CollectionRecord]:
    """Fetch and cache all collections from the data.gov.sg API."""
    global _collections_cache
    if _collections_cache is not None:
        return _collections_cache

    collections: list[CollectionRecord] = []
    for page in range(1, MAX_COLLECTION_PAGES + 1):
        data = request_json(
            f"{DATA_GOV_SG_API_BASE}/v2/public/api/collections",
            params={"page": page},
            timeout=30,
        )
        if not api_ok(data):
            error_msg = data.get("errorMsg") or f"Failed on page {page}"
            raise DataGovApiError(error_msg)

        batch = data.get("data", {}).get("collections", [])
        if not batch:
            break
        collections.extend(batch)

    if not collections:
        raise DataGovApiError("No collections returned from data.gov.sg.")

    _collections_cache = collections
    return collections


def rank_collections(
    query: str,
    collections: list[CollectionRecord],
) -> list[tuple[float, CollectionRecord]]:
    extra_terms = get_agency_search_terms(query)
    scored = [
        (_score_collection(col, query, extra_terms), col)
        for col in collections
    ]
    scored = [(score, col) for score, col in scored if score > 0.15]
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored


def _collection_search_text(collection: CollectionRecord) -> str:
    return " ".join(
        [
            collection.get("name", ""),
            collection.get("description", ""),
            collection.get("managedByAgencyName", ""),
            " ".join(collection.get("sources", [])),
        ]
    ).lower()


def _score_collection(
    collection: CollectionRecord,
    query: str,
    extra_terms: list[str],
) -> float:
    name = collection.get("name", "").lower()
    agency = collection.get("managedByAgencyName", "").lower()
    text = _collection_search_text(collection)
    query_lower = query.lower()
    terms = {query_lower, *[t.lower() for t in extra_terms]}

    score = 0.0
    for term in terms:
        if not term:
            continue
        if name == term:
            score = max(score, 1.0)
        elif term in name:
            score = max(score, 0.9)
        elif term in agency:
            score = max(score, 0.85)
        elif term in text:
            score = max(score, 0.7)
        else:
            score = max(score, SequenceMatcher(None, term, name).ratio() * 0.6)

    return score


def _format_collection(collection: CollectionRecord, rank: int) -> str:
    collection_id = collection.get("collectionId", "N/A")
    name = collection.get("name", "Untitled")
    agency = collection.get("managedByAgencyName", "Unknown")
    description = collection.get("description", "")[:150]
    if len(collection.get("description", "")) > 150:
        description += "..."

    child_ids = collection.get("childDatasets", [])
    collection_link = f"https://data.gov.sg/collections/{collection_id}/view"
    lines = [
        f"{rank}. **{name}**",
        f"   Collection ID: {collection_id}",
        f"   Agency: {agency}",
        f"   Description: {description}",
        f"   Link: {collection_link}",
    ]
    if child_ids:
        lines.append(f"   Child datasets ({len(child_ids)}):")
        for ds_id in child_ids[:5]:
            lines.append(
                f"     - {ds_id}: https://data.gov.sg/datasets/{ds_id}/view"
            )
        if len(child_ids) > 5:
            lines.append(f"     - ... and {len(child_ids) - 5} more")
    return "\n".join(lines)


@tool
def search_collections(query: str, limit: int = 5) -> str:
    """Search data.gov.sg collections by name and return the closest matches.

    Use this when the user mentions an agency (e.g. HDB, LTA) or topic and you
    need the correct collectionId and portal links. Matches against collection
    name, description, managing agency, and sources.

    Args:
        query: Agency acronym, agency name, or topic keywords (e.g. "HDB", "housing")
        limit: Maximum number of collections to return (default 5)
    """
    try:
        collections = load_all_collections()
        top = rank_collections(query, collections)[: min(limit, 10)]

        if not top:
            return f"No collections found matching '{query}'."
        header = (
            f"Closest collection matches for '{query}' "
            f"({len(top)} shown, {len(collections)} collections searched):\n\n"
        )
        body = "\n\n".join(
            _format_collection(col, rank=i + 1) for i, (_, col) in enumerate(top)
        )
        return header + body
    except DataGovApiError as exc:
        return f"Failed to search collections: {exc}"
