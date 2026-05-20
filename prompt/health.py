"""Health category agent prompt."""

from prompt.templates import render_category_prompt

HEALTH_SYSTEM_PROMPT = render_category_prompt(
    category_name="Health",
    category_url="https://data.gov.sg/datasets?topics=health",
    dataset_examples="COVID, healthcare, MOH, disease, hospital, etc.",
)
