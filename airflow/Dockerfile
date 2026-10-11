FROM apache/airflow:2.10.5-python3.12

USER root
RUN mkdir /opt/pipeline-venv && chown airflow: /opt/pipeline-venv
USER airflow

# dbt and the loader run in their own virtualenv so their dependencies
# cannot conflict with Airflow's pinned packages.
COPY requirements.txt /tmp/requirements.txt
RUN python -m venv /opt/pipeline-venv \
    && /opt/pipeline-venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt
