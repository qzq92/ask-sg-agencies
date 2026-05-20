"""Housing category agent prompt."""

from prompt.templates import render_category_prompt

HOUSING_SYSTEM_PROMPT = render_category_prompt(
    category_name="Housing",
    category_url="https://data.gov.sg/datasets?topics=housing",
    dataset_examples="HDB resale prices, property, BTO, rental, etc.",
)
