"""Arts & Culture category agent prompt."""

from prompt.templates import render_category_prompt

ARTS_CULTURE_SYSTEM_PROMPT = render_category_prompt(
    category_name="Arts & Culture",
    category_url="https://data.gov.sg/datasets?topics=artsandculture",
    dataset_examples="museums, heritage, cultural events, arts funding, etc.",
)
