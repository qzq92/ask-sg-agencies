"""Transport category agent prompt."""

from prompt.templates import render_category_prompt

TRANSPORT_SYSTEM_PROMPT = render_category_prompt(
    category_name="Transport",
    category_url="https://data.gov.sg/datasets?topics=transport",
    dataset_examples="traffic, LTA, public transport, road, parking, etc.",
)
