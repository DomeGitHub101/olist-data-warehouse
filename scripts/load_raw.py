import csv
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg import sql


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIRECTORY = PROJECT_ROOT / "data" / "raw"

FILES = {
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_customers_dataset.csv": "customers",
    "olist_products_dataset.csv": "products",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_sellers_dataset.csv": "sellers",
    "olist_geolocation_dataset.csv": "geolocation",
    "product_category_name_translation.csv": "category_translation",
}


def read_columns(path):
    with path.open(encoding="utf-8-sig", newline="") as source:
        columns = next(csv.reader(source), None)

    if not columns or any(not column.strip() for column in columns):
        raise ValueError(f"Missing or empty column names: {path.name}")

    if len(columns) != len(set(columns)):
        raise ValueError(f"Duplicate column names: {path.name}")

    return columns


def load_table(connection, path, table_name, columns):
    table = sql.Identifier("raw", table_name)

    definitions = sql.SQL(", ").join(
        sql.SQL("{} TEXT").format(sql.Identifier(column))
        for column in columns
    )

    column_list = sql.SQL(", ").join(
        sql.Identifier(column) for column in columns
    )

    # Each table is replaced in one transaction.
    with connection.transaction():
        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
                    table, definitions
                )
            )

            cursor.execute(
                sql.SQL("TRUNCATE TABLE {}").format(table)
            )

            copy_query = sql.SQL(
                "COPY {} ({}) FROM STDIN "
                "WITH (FORMAT CSV, HEADER TRUE)"
            ).format(table, column_list)

            with path.open(encoding="utf-8-sig", newline="") as source:
                with cursor.copy(copy_query) as copy:
                    while chunk := source.read(1024 * 1024):
                        copy.write(chunk)

            cursor.execute(
                sql.SQL("SELECT COUNT(*) FROM {}").format(table)
            )
            row_count = cursor.fetchone()[0]

    return row_count


def main():
    load_dotenv(PROJECT_ROOT / ".env")

    # Check all files before starting database changes.
    inputs = []

    for filename, table_name in FILES.items():
        path = RAW_DIRECTORY / filename

        if not path.is_file():
            raise FileNotFoundError(f"CSV file not found: {path}")

        inputs.append((path, table_name, read_columns(path)))

    with psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        autocommit=True,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("CREATE SCHEMA IF NOT EXISTS raw")

        for path, table_name, columns in inputs:
            row_count = load_table(
                connection, path, table_name, columns
            )
            print(f"Loaded raw.{table_name}: {row_count:,} rows")

    print("All 9 tables loaded successfully.")


if __name__ == "__main__":
    main()