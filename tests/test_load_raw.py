import os
import sys
from pathlib import Path

import psycopg
import pytest
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import load_raw  # noqa: E402


def write_csv(path, text):
    path.write_text(text, encoding="utf-8")
    return path


def test_read_columns_returns_header(tmp_path):
    path = write_csv(tmp_path / "a.csv", "id,name\n1,x\n")

    assert load_raw.read_columns(path) == ["id", "name"]


def test_read_columns_strips_utf8_bom(tmp_path):
    path = tmp_path / "a.csv"
    path.write_bytes("﻿id,name\n".encode("utf-8"))

    assert load_raw.read_columns(path) == ["id", "name"]


@pytest.mark.parametrize("header", ["", "id,,name", "id, ,name"])
def test_read_columns_rejects_empty_names(tmp_path, header):
    path = write_csv(tmp_path / "a.csv", header + "\n")

    with pytest.raises(ValueError, match="Missing or empty"):
        load_raw.read_columns(path)


def test_read_columns_rejects_duplicates(tmp_path):
    path = write_csv(tmp_path / "a.csv", "id,id\n")

    with pytest.raises(ValueError, match="Duplicate"):
        load_raw.read_columns(path)


def test_every_file_maps_to_a_distinct_table():
    assert len(load_raw.FILES) == 9
    assert len(set(load_raw.FILES.values())) == len(load_raw.FILES)


@pytest.fixture
def connection():
    load_dotenv(PROJECT_ROOT / ".env")

    try:
        conn = psycopg.connect(
            host=os.environ["POSTGRES_HOST"],
            port=int(os.environ["POSTGRES_PORT"]),
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            autocommit=True,
            connect_timeout=3,
        )
    except (KeyError, psycopg.OperationalError) as error:
        pytest.skip(f"PostgreSQL not available: {error}")

    with conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        yield conn
        conn.execute("DROP TABLE IF EXISTS raw.pytest_sample")


def test_load_table_replaces_previous_rows(tmp_path, connection):
    path = write_csv(
        tmp_path / "sample.csv",
        'id,comment\n1,"has, comma"\n2,\n',
    )
    columns = load_raw.read_columns(path)

    assert load_raw.load_table(connection, path, "pytest_sample", columns) == 2
    # A second run is a full refresh, not an append.
    assert load_raw.load_table(connection, path, "pytest_sample", columns) == 2

    rows = connection.execute(
        "SELECT id, comment FROM raw.pytest_sample ORDER BY id"
    ).fetchall()
    assert rows == [("1", "has, comma"), ("2", None)]
