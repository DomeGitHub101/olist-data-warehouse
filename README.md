# olist-data-warehouse
An e-commerce data warehouse built with Python, PostgreSQL, dbt, and Airflow using the Olist dataset.

## Architecture

```
CSV files ──► raw (TEXT, as-is) ──► staging (typed views) ──► intermediate ──► marts (star schema)
  scripts/load_raw.py                 dbt                        dbt              dbt
                  └──────────── orchestrated daily by Airflow (olist_pipeline) ────────────┘
```

| Schema         | Contents |
|----------------|----------|
| `raw`          | The 9 Olist CSVs loaded unchanged, every column `TEXT`. Full refresh on each load. |
| `staging`      | One view per source table: renamed, typed columns. Geolocation is reduced to one row per zip prefix. |
| `intermediate` | Per-order rollups of items, payments, and the latest review. |
| `marts`        | `fct_orders`, `fct_order_items`, `dim_customers`, `dim_products`, `dim_sellers`, `dim_date`, and the `mart_monthly_sales` KPI table. |

### Mart grains

- **fct_orders**: one row per order, with item/freight/payment values, review score, delivery days, and a late-delivery flag.
- **fct_order_items**: one row per order item, the sales grain.
- **dim_customers**: one row per real customer (`customer_unique_id`). Olist's `customer_id` changes with every order.
- **mart_monthly_sales**: monthly GMV, orders, customers, AOV, review score, and late-delivery rate.

## Setup

Requirements: Docker, Python 3.12, and the [Olist dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

```bash
cp .env.example .env               # then set POSTGRES_PASSWORD
# Put the 9 Olist CSV files in data/raw/

docker compose up -d --wait        # PostgreSQL on 127.0.0.1:5433

python -m venv .venv
.venv/Scripts/activate             # Windows; use .venv/bin/activate on macOS/Linux
pip install -r requirements-dev.txt
```

## Run

```bash
python scripts/load_raw.py         # CSV -> raw schema
python scripts/run_dbt.py build    # build all models and run all tests
```

`scripts/run_dbt.py` loads `.env` and forwards any arguments to dbt, for example
`python scripts/run_dbt.py build --select marts` or `python scripts/run_dbt.py docs generate`.

### Airflow

```bash
docker compose --profile airflow up -d --build
```

Open http://localhost:8080. The `admin` password is printed in the container log
(`docker compose logs airflow | grep password`). The `olist_pipeline` DAG runs
`load_raw → dbt_build_staging → dbt_build_marts`.

To run the whole DAG once without the scheduler:

```bash
docker compose --profile airflow run --rm airflow airflow dags test olist_pipeline
```

## Tests

- **pytest** (`tests/`): CSV header validation, plus an integration test that loads into PostgreSQL. The integration test is skipped when the database isn't reachable.
- **dbt data tests**: uniqueness, not-null, relationships, and accepted values across all layers. A custom `non_negative` generic test covers money columns.
- **dbt singular tests** (`dbt/tests/`): approval timestamps, item row preservation, and payment/item reconciliation.
- **dbt unit test**: payment aggregation logic in `int_order_payments_aggregated`.

```bash
pytest
python scripts/run_dbt.py build
```

## Known data quirks

- One review can cover several orders, and some orders have several reviews. `int_order_reviews_latest` keeps the latest review per order.
- Two product categories have no English translation, and 610 products have no category. `dim_products` falls back to the Portuguese name, or to `unknown`.
- About 0.25% of orders pay a different amount than items + freight, mostly because of installment interest. The reconciliation test allows up to 1%.
- Some geolocation points fall outside Brazil, so they are filtered out before averaging.
