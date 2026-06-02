"""Prompt templates package."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

_template_dir = Path(__file__).parent
_env = Environment(loader=FileSystemLoader(_template_dir), trim_blocks=True, lstrip_blocks=True)


def render_category_prompt(
    category_name: str,
    category_url: str,
    dataset_examples: str,
    format_note: str = "",
) -> str:
    """Render a category agent prompt from the Jinja2 template."""
    template = _env.get_template("category_agent.jinja2")
    return template.render(
        category_name=category_name,
        category_url=category_url,
        dataset_examples=dataset_examples,
        format_note=format_note,
    )
