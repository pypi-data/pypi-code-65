import pandas as pd
from sqlalchemy import create_engine

from sedatatools.sedatatools.tools.connectors.prime import Prime


def test_lower_lvls_all_upper_lvls(database):
    pass
    # 1. check if all geo in lower levels have proper geos in upper levels
    # 2. check if all geos in higher levels have any geo in lower levels
    # 3. check geo column uniqueness
    # 4. check if row column is autoincrement by one
    # 5. check if all tables have the same number of record as the names tables
    # 6. check if all tables exists on all levels
    # 7. check if there are all required FIPS and name columns


def db_init():
    global ENG
    db_creds = Prime()
    db_name = ''
    ENG = create_engine(
        f'mssql+pyodbc://{db_creds.user_name}:{db_creds.password}@prime/{db_name}?driver=SQL+Server+Native+Client+11.0', connect_args={'autocommit': True},
    )


def metadata_init(metadata_path):
    metadata_path


if __name__ == '__main__':
    metadata_path = r'C:\Projects\Website-ASP.NET\pub\ReportData\Metadata\CED2017.xml'
    db_init()
    metadata_init(metadata_path)

    test_lower_lvls_all_upper_lvls()
    pass
