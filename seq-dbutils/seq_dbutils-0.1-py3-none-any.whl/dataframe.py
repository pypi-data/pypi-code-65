import logging
import re
import sys
from datetime import datetime
from os.path import isfile

import pandas as pd

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")


class DataFrameUtils:

    @staticmethod
    def add_prefixed_incremented_id(engine, df_input, table_name, id_name, id_prefix, id_zero_padding=10):
        if id_name in list(df_input):
            df_with_id = df_input[~df_input[id_name].isnull()].copy()
            df_no_id = df_input[df_input[id_name].isnull()].copy()
            del df_no_id[id_name]
        else:
            df_with_id = pd.DataFrame()
            df_no_id = df_input.copy()

        pk_sql = f'SELECT {id_name} FROM {table_name} ORDER BY {id_name} DESC LIMIT 1;'
        result = engine.execute(pk_sql).fetchone()
        if result:
            # Extract the integer
            last_pk = int(re.sub(id_prefix, '', result[0]))
            df_no_id.loc[:, '_id'] = range(last_pk + 1, len(df_no_id) + last_pk + 1)
        else:
            # Start at 1
            df_no_id.loc[:, '_id'] = range(1, len(df_no_id) + 1)

        df_no_id.loc[:, id_name] = df_no_id['_id'].apply(lambda x: id_prefix + str(x).zfill(id_zero_padding))
        del df_no_id['_id']

        df_out = pd.concat([df_with_id, df_no_id], sort=False)
        return df_out

    @staticmethod
    def read_csv_with_header_mapping(csv_filepath, col_name_mapping_dict=None):
        if isfile(csv_filepath):
            df = pd.read_csv(csv_filepath, header='infer', low_memory=False)
            logging.info(f'Read file {csv_filepath} with lines: %s', len(df))
            if col_name_mapping_dict:
                df.rename(columns=col_name_mapping_dict, inplace=True)
            return df
        else:
            logging.error(f'File {csv_filepath} does not exist. Exiting...')
            sys.exit(1)

    @staticmethod
    def apply_date_format(input_date, format_date):
        if input_date:
            if input_date == '-':
                input_date = None
            else:
                format_time = format_date + ' %H:%M:%S'
                try:
                    input_date = datetime.strptime(input_date, format_date).date()
                except ValueError as ex:
                    if 'unconverted data remains:' in ex.args[0]:
                        input_date = datetime.strptime(input_date, format_time).date()
                    else:
                        logging.error(str(ex))
                        sys.exit(1)
        else:
            input_date = None
        return input_date

    @staticmethod
    def remove_rows_with_blank_col_subset(df, col_list):
        assert isinstance(col_list, list)
        df_subset = df.filter(col_list, axis=1)
        df_na_subset = df_subset[pd.isnull(df_subset).all(axis=1)]
        if not df_na_subset.empty:
            df_no_nas = df.dropna(subset=col_list, how='all')
            df_no_nas.reset_index(inplace=True, drop=True)
        else:
            df_no_nas = df.copy()
        return df_no_nas
