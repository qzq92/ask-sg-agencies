"""Launcher that applies Windows SSL patches before Streamlit imports anything.

Invoke with: `uv run python run.py` (instead of `uv run streamlit run app.py`).
"""

from config.windows_patch import apply_windows_patch

apply_windows_patch()

import sys
from streamlit.web import cli as stcli


def main() -> None:
    sys.argv = ["streamlit", "run", "app.py"]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
