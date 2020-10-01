"""Tools for GLAM ETL."""
import click
from google.cloud import bigquery
from .utils import run
from pathlib import Path
import os

ROOT = Path(__file__).parent.parent.parent


def _check_root():
    assert (ROOT / "sql").exists(), f"{ROOT} is not the project root"


@click.group()
def glam():
    """Tools for GLAM ETL."""
    pass


@glam.group()
def glean():
    """Tools for Glean in GLAM."""
    pass


@glean.command()
@click.option("--project", default="glam-fenix-dev")
@click.option("--dataset", default="glam_etl_dev")
def list_daily(project, dataset):
    """List the start and end dates for clients daily tables."""
    _check_root()
    client = bigquery.Client()
    app_df = client.query(
        f"""
        WITH
        extracted AS (
            SELECT
                DISTINCT REGEXP_EXTRACT(table_name, "(.*)__") AS app_id,
            FROM
                `{project}`.{dataset}.INFORMATION_SCHEMA.TABLES
            WHERE
                table_name LIKE "%clients_daily%" )
        SELECT
            app_id,
            (app_id LIKE "%_glam_%") AS is_logical
        FROM
            extracted
        ORDER BY
            is_logical,
            app_id
    """
    ).to_dataframe()

    query = []
    for row in app_df.itertuples():
        query += [
            f"""
            SELECT
                "{row.app_id}" as app_id,
                {row.is_logical} as is_logical,
                date(min(submission_date)) as earliest,
                date(max(submission_date)) as latest
            FROM
                `{project}`.{dataset}.{row.app_id}__view_clients_daily_scalar_aggregates_v1
            """
        ]

    range_df = (
        client.query("\nUNION ALL\n".join(query))
        .to_dataframe()
        .sort_values(["is_logical", "app_id"])
    )
    click.echo(range_df)


@glean.command()
@click.argument("app-id", type=str)
@click.argument("start-date", type=str)
@click.argument("end-date", type=str)
@click.option("--dataset", type=str, default="glam_etl_dev")
def backfill_incremental(app_id, start_date, end_date, dataset):
    """Backfill the incremental tables using existing daily tables.

    To rebuild the table from scratch, drop the clients_scalar_aggregates and
    clients_histogram_aggregates tables.
    """
    _check_root()
    run(
        "script/glam/generate_glean_sql",
        cwd=ROOT,
        env={**os.environ, **dict(PRODUCT=app_id, STAGE="incremental")},
    )
    run(
        "script/glam/backfill_glean",
        cwd=ROOT,
        env={
            **os.environ,
            **dict(
                DATASET=dataset,
                PRODUCT=app_id,
                STAGE="incremental",
                START_DATE=start_date,
                END_DATE=end_date,
                RUN_EXPORT="false",
            ),
        },
    )


@glean.command()
@click.argument("app-id", type=str)
@click.option("--project", default="glam-fenix-dev")
@click.option("--dataset", type=str, default="glam_etl_dev")
def export(app_id, project, dataset):
    """Run the export ETL and write the final csv to a gcs bucket."""
    _check_root()
    run(
        "script/glam/generate_glean_sql",
        cwd=ROOT,
        env={**os.environ, **dict(PRODUCT=app_id, STAGE="incremental")},
    )
    run(
        "script/glam/run_glam_sql",
        cwd=ROOT,
        env={
            **os.environ,
            **dict(
                PROJECT=project,
                DATASET=dataset,
                PRODUCT=app_id,
                STAGE="incremental",
                EXPORT_ONLY="true",
            ),
        },
    )
    run(
        "script/glam/export_csv",
        cwd=ROOT,
        env={
            **os.environ,
            **dict(SRC_PROJECT=project, DATASET=dataset, PRODUCT=app_id),
        },
    )


if __name__ == "__main__":
    glam()
