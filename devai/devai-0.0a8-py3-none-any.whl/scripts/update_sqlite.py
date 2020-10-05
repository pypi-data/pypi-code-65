from fire import Fire
from sqlalchemy import create_engine
import pandas as pd
from devai import Path


def update_sqlite(db_path, csv_path, table_name="data", create_db=False):
    """
    not the most effecient method of updating an existing database with new rows. 
    """
    assert Path(db_path).is_file(
    ) or create_db, f"{db_path} doesn't exist or is not a file"
    engine = create_engine(f"sqlite:///{db_path}")
    sqlite_connection = engine.connect()
    sqlite_table = table_name
    df = pd.read_csv(csv_path, encoding="latin")

    if not create_db:
        existing = pd.read_sql(sqlite_table, sqlite_connection)
        df = pd.concat([existing, df])
        df.drop_duplicates(inplace=True)
        df.reset_index(inplace=True)
    df.to_sql(sqlite_table, sqlite_connection,
              if_exists="replace", index=False)
    sqlite_connection.close()


in_jup = False
try:
    get_ipython
    in_jup = True
except:
    pass

if in_jup:
    update_sqlite("snow.db", "incident (4).csv", create_db=True)
elif __name__ == "__main__":
    Fire(update_sqlite)
