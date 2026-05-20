"""Economy category agent prompt."""

from prompt.templates import render_category_prompt

ECONOMY_SYSTEM_PROMPT = render_category_prompt(
    category_name="Economy",
    category_url="https://data.gov.sg/datasets?topics=economy",
    dataset_examples="GDP, trade, business, employment, ACRA, etc.",
)
