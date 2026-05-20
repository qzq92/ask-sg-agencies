"""Geospatial category agent prompt."""

from prompt.templates import render_category_prompt

GEOSPATIAL_SYSTEM_PROMPT = render_category_prompt(
    category_name="Geospatial",
    category_url="https://data.gov.sg/datasets?formats=GEOJSON|KML|SHP|KMZ",
    dataset_examples="maps, boundaries, locations, GIS data, etc.",
    format_note="GEOJSON, KML, SHP, KMZ formats",
)
