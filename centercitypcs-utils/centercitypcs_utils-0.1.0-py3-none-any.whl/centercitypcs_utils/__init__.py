"""
Utility Functions
"""

__version__ = "0.1.0"

import sqlalchemy
import pandas as pd
import gspread
import gspread_dataframe


def get_sql_as_df(database_url: str, query_file: str, **kwargs: dict) -> pd.DataFrame:
    with open(query_file, "r") as query_file:
        query = query_file.read()

    with sqlalchemy.create_engine(
        database_url, max_identifier_length=128
    ).connect() as db:
        df = pd.read_sql(query, db, **kwargs)

    return df


def get_google_sheet_as_df(
    spreadsheet_key: str, service_account: str, worksheet_number: str = 0, **kwargs,
) -> pd.DataFrame:
    access = gspread.service_account(service_account)
    spreadsheet = access.open_by_key(spreadsheet_key)
    sheet = spreadsheet.get_worksheet(worksheet_number)
    df = gspread_dataframe.get_as_dataframe(sheet, evaluate_formulas=True, **kwargs)

    df.dropna("rows", how="all", inplace=True)
    df.dropna("columns", how="all", inplace=True)

    return df
