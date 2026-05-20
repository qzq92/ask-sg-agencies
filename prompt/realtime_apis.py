"""Real-time APIs category agent prompt."""

from prompt.templates import render_category_prompt

REALTIME_APIS_SYSTEM_PROMPT = render_category_prompt(
    category_name="Real-time APIs",
    category_url="https://data.gov.sg/datasets?formats=API",
    dataset_examples="live data, weather APIs, traffic APIs, etc.",
    format_note="API-format datasets",
)
