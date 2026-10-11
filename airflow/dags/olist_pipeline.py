"""Daily ELT: load Olist CSVs into raw, then build and test the dbt models."""

import os
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


PROJECT_DIR = os.environ.get("PROJECT_DIR", "/opt/project")
VENV_BIN = os.environ.get("PIPELINE_VENV_BIN", "/opt/pipeline-venv/bin")
DBT = (
    f"{VENV_BIN}/dbt build "
    f"--project-dir {PROJECT_DIR}/dbt --profiles-dir {PROJECT_DIR}/dbt"
)

with DAG(
    dag_id="olist_pipeline",
    description="Load raw Olist data and build the warehouse with dbt",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    tags=["olist", "dbt"],
) as dag:
    load_raw = BashOperator(
        task_id="load_raw",
        bash_command=f"{VENV_BIN}/python {PROJECT_DIR}/scripts/load_raw.py",
    )

    build_staging = BashOperator(
        task_id="dbt_build_staging",
        bash_command=f"{DBT} --select staging intermediate",
    )

    build_marts = BashOperator(
        task_id="dbt_build_marts",
        bash_command=f"{DBT} --select marts",
    )

    load_raw >> build_staging >> build_marts
