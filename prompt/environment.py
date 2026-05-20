"""Environment category agent prompt."""

from prompt.templates import render_category_prompt

ENVIRONMENT_SYSTEM_PROMPT = render_category_prompt(
    category_name="Environment",
    category_url="https://data.gov.sg/datasets?topics=environment",
    dataset_examples="weather, air quality, PM2.5, recycling, NEA, climate, etc.",
)
