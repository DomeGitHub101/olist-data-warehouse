"""Run dbt with connection settings loaded from .env.

Usage: python scripts/run_dbt.py build
       python scripts/run_dbt.py test --select fct_orders
"""

import sys
from pathlib import Path

from dbt.cli.main import dbtRunner
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DBT_DIRECTORY = PROJECT_ROOT / "dbt"


def main():
    # dbt logs non-ASCII characters; Windows consoles may not default to UTF-8.
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")

    load_dotenv(PROJECT_ROOT / ".env")

    args = sys.argv[1:] or ["build"]
    args += [
        "--project-dir", str(DBT_DIRECTORY),
        "--profiles-dir", str(DBT_DIRECTORY),
    ]

    result = dbtRunner().invoke(args)
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
