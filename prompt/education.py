"""Education category agent prompt."""

from prompt.templates import render_category_prompt

EDUCATION_SYSTEM_PROMPT = render_category_prompt(
    category_name="Education",
    category_url="https://data.gov.sg/datasets?topics=education",
    dataset_examples="schools, enrolment, exam results, MOE statistics, etc.",
)
