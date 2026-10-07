import csv
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg import sql


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = PROJECT_ROOT / "data" / "raw" / "olist_orders_dataset.csv"

COLUMNS = [
    "order_id",
    "customer_id",
    "order_status",
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


def main():
    load_dotenv(PROJECT_ROOT / ".env")

    if not CSV_PATH.is_file():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

    # Validate the header before changing the database.
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as source:
        header = next(csv.reader(source), None)

    if header != COLUMNS:
        raise ValueError(f"Unexpected CSV columns: {header}")

    with psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("CREATE SCHEMA IF NOT EXISTS raw")

            column_definitions = sql.SQL(", ").join(
                sql.SQL("{} TEXT").format(sql.Identifier(column))
                for column in COLUMNS
            )

            cursor.execute(
                sql.SQL(
                    "CREATE TABLE IF NOT EXISTS raw.orders ({})"
                ).format(column_definitions)
            )

            # Full refresh: replace the previous snapshot.
            cursor.execute("TRUNCATE TABLE raw.orders")

            copy_query = sql.SQL(
                "COPY raw.orders ({}) FROM STDIN "
                "WITH (FORMAT CSV, HEADER TRUE)"
            ).format(
                sql.SQL(", ").join(
                    sql.Identifier(column) for column in COLUMNS
                )
            )

            with CSV_PATH.open(encoding="utf-8-sig", newline="") as source:
                with cursor.copy(copy_query) as copy:
                    while chunk := source.read(1024 * 1024):
                        copy.write(chunk)

            cursor.execute("SELECT COUNT(*) FROM raw.orders")
            row_count = cursor.fetchone()[0]

    print(f"Successfully loaded {row_count:,} rows into raw.orders")


if __name__ == "__main__":
    main()