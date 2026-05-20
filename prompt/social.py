"""Social category agent prompt."""

from prompt.templates import render_category_prompt

SOCIAL_SYSTEM_PROMPT = render_category_prompt(
    category_name="Social",
    category_url="https://data.gov.sg/datasets?topics=social",
    dataset_examples="demographics, population, community, welfare, etc.",
)
