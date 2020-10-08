import os
from datetime import datetime
from google.cloud import bigquery

project_id = os.environ["GCP_PROJECT"]
BQ = bigquery.Client(project=project_id)


def stream_json_into_bq(json_string, destination_ref):

    current_time = datetime.now()
    current_timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")

    try:
        table = BQ.get_table(destination_ref)

        rows_to_insert = [(json_string, current_timestamp)]

        errors = BQ.insert_rows(
            table, rows_to_insert, row_ids=[None] * len(rows_to_insert)
        )

        print("errors:", errors)

    except Exception as e:
        print(e)


def stream_json_into_bq_with_id(id_string, json_string, destination_ref):

    current_time = datetime.now()
    current_timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")

    try:
        table = BQ.get_table(destination_ref)

        rows_to_insert = [(id_string, json_string, current_timestamp)]

        errors = BQ.insert_rows(
            table, rows_to_insert, row_ids=[None] * len(rows_to_insert)
        )

        print("errors:", errors)

    except Exception as e:
        print(e)
