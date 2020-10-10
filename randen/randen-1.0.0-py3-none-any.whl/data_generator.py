"""
Randen: Random DataFrame Generator
    A small utility to generate random dataframes for testing, benchmarking etc. purposes
    Supported dataframe types:
    - string
    - datetime
    - char
    - int
    - float
    - bool
    - mix(provide column types)

TODO:
    - Add Null ratio support
    - Add Documentation build(readdocs? )
"""

__author__ = "Kanishk Varshney"
__date__ = "05-10-2020"
__appname__ = "randen"

import time
import random
import secrets

import logging
from typing import List
from functools import partial
from datetime import datetime
from random import random, choice
from collections import Counter
from string import ascii_letters, ascii_lowercase, ascii_uppercase, digits

import numpy as np
import pandas as pd


logging_format = "%(asctime)s [%(levelname)s] %(name)s : %(message)s in %(pathname)s:%(lineno)d"
logging.basicConfig(level=logging.DEBUG, format=logging_format)
logger = logging.getLogger(__appname__)


class DataFrameGenerator:
    """Dataframe Generator class

    Usage:
    -----
        dfg = DataFrameGenerator()
        df = get_dataframe(nrows=10, ctypes=[str, int, float])
        ...
        This will return the dataframe with following traits
        > dfg.shape == (10, 3)
        > dfg.columns == ["Str0", "Int0", "Float0"]
        > dfg.dtypes == Str    object
                        Int    int32
                        Float  float64
                        dtype: object


    Supported APIs:
    ---------------
        dfg.get_dataframe(...)

        dfg.get_integer_dataframe(...)

        dfg.get_float_dataframe(...)

        dfg.get_string_dataframe(...)

        dfg.get_char_dataframe(...)

        dfg.get_dates_dataframe(...)

        dfg.get_bool_dataframe(...)

    """
    def __init__(self):
        self._numrows = None

    def _generate_ints(self, _min: int = -100000, _max: int = 100000) -> np.ndarray:
        return np.random.randint(low=_min, high=_max, size=self._numrows)

    def _generate_floats(self, _min: float = -1.0, _max: float = 1.0) -> np.ndarray:
        return ((_max - _min) * np.random.random(size=self._numrows)) + _min

    def _generate_strings(self, _min: int = 10, _max: int = 20) -> List[str]:
        keys = set()
        pickchar = partial(secrets.choice, ascii_letters + digits)
        while len(keys) < self._numrows:
            keys |= {''.join([pickchar()
                              for _ in range(np.random.randint(low=_min, high=_max))])
                     for _ in range(self._numrows - len(keys))}
        return list(keys)

    def _generate_dates(self, start: datetime = None, end: datetime = None) -> pd.DatetimeIndex:
        if not start:
            start = datetime.fromtimestamp(0)
        if not end:
            end = datetime.now()
        return pd.date_range(start=start, end=end, periods=self._numrows)

    def _generate_bools(self) -> List[bool]:
        return [not random() >= 0.5 for _ in range(self._numrows)]

    def _generate_chars(self, lowercase: bool = True) -> List[str]:
        if lowercase:
            return [choice(ascii_lowercase) for _ in range(self._numrows)]
        else:
            return [choice(ascii_uppercase) for _ in range(self._numrows)]

    def _get_column_names(self, ctypes: List[type], columns: List[str] = None) -> List[str]:
        """
        TODO: Change column names to Str0, Str1, Integer0, Integer1, ... format
        TODO: Optimize the column name generation?
        Args:
            ctypes (List[type]): Column types of the dataframe
            columns (List[str], optional): Column names of the dataframe. Defaults to None.

        Returns:
            List[str]: columns; Names of dataframe columns
        """
        if columns is not None and len(ctypes) == len(columns):
            return columns
        columns = []
        _ctypes_count = Counter(ctypes)
        for i, _ctype in enumerate(ctypes):
            _column_name = f"{_ctype.__name__.capitalize()}{i}"
            columns.append(_column_name)
        return columns

    def get_dataframe(self, nrows: int, ctypes: List[type], columns: List[str] = None) -> pd.DataFrame:
        """Generate random data frame of shape 'nrows x len(ctypes)'

        Args:
            nrows (int): Number of rows
            ctypes (List[type]): Column types of the dataframe
            columns (List[str], optional): Column names of the dataframe. Defaults to None.

        Raises:
            ValueError: If requested Column datatype is unsupported

        Returns:
            pd.DataFrame:
        """        

        assert ctypes is not None, "provide columns' data types"
        if columns is not None:
            assert len(columns) == len(ctypes), "provide all or No Columns names"

        columns = self._get_column_names(ctypes, columns)
        self._numrows = nrows
        out_df = pd.DataFrame()
        for i, _ctype in enumerate(ctypes):
            _col_name = columns[i]
            if _ctype == int:
                _data_list = self._generate_ints()
            elif _ctype == float:
                _data_list = self._generate_floats()
            elif _ctype == bool:
                _data_list = self._generate_bools()
            elif _ctype == str:
                _data_list = self._generate_strings()
            elif _ctype == bytes:
                _data_list = self._generate_chars()
            elif _ctype == datetime:
                _data_list = self._generate_dates()
            else:
                logger.error(f"Unsuported datatype {_ctype} requested")
                raise ValueError(f"Unsupported datatype {_ctype} requested")

            out_df[_col_name] = _data_list

        return out_df

    def get_integer_dataframe(self, nrows: int, ncols: int, nullratio=0, columns: List[str] = None,
                              minval: int = -100000, maxval: int = 100000) -> pd.DataFrame:
        """Generate a dataframe of ONLY integer datatype values

        Args:
            nrows (int): Number of rows
            ncols (int): Number of columns of type int
            nullratio (int, optional): [description]. Defaults to 0.
            columns (List[str], optional): Column names of the dataframe. Defaults to None.
            minval (int, optional): Minimum value of the integers. Defaults to -100000.
            maxval (int, optional): Maximum value of the integers. Defaults to 100000.

        Returns:
            pd.DataFrame:
        """        
        if columns is not None:
            assert len(columns) == ncols, "provide all or No Columns names"

        logger.info(f"Generating {nrows}x{ncols} all integer dataframe")
        self._numrows = nrows

        out_df = pd.DataFrame()
        for i in range(ncols):
            _col_name = columns[i] if columns is not None else f"Integer{i}"
            out_df[_col_name] = self._generate_ints(_min=minval, _max=maxval)

        return out_df

    def get_float_dataframe(self, nrows: int, ncols: int, nullratio: float = 0, columns: List[str] = None,
                            minval: float = -1.0, maxval: float = 1.0) -> pd.DataFrame:
        """Generate a dataframe of ONLY floating point datatype values

        Args:
            nrows (int): Number of rows
            ncols (int): Number of columns of type float
            nullratio (float, optional): [description]. Defaults to 0.
            columns (List[str], optional): Column names of the dataframe. Defaults to None.
            minval (float, optional): Minimum value of the floats. Defaults to -1.0.
            maxval (float, optional): Maximum value of the floats. Defaults to 1.0.

        Returns:
            pd.DataFrame:
        """        
        if columns is not None:
            assert len(columns) == ncols, "Provide all or No Columns names"

        logger.info(f"Generating {nrows}x{ncols} all float dataframe")
        self._numrows = nrows

        out_df = pd.DataFrame()
        for i in range(ncols):
            _col_name = columns[i] if columns is not None else f"Float{i}"
            out_df[_col_name] = self._generate_floats(_min=minval, _max=maxval)

        return out_df

    def get_boolean_dataframe(self, nrows: int, ncols: int, nullratio=0, columns=None) -> pd.DataFrame:
        """Generate a dataframe of ONLY boolean datatype values

        Args:
            nrows (int): Number of rows
            ncols (int): Number of columns
            nullratio (int, optional): [description]. Defaults to 0.
            columns (List[str], optional): Column names of the dataframe. Defaults to None.

        Returns:
            pd.DataFrame:
        """        
        if columns is not None:
            assert len(columns) == ncols, "Provide all or No Columns names"

        logger.info(f"Generating {nrows}x{ncols} all boolean dataframe")
        self._numrows = nrows

        out_df = pd.DataFrame()
        for i in range(ncols):
            _col_name = columns[i] if columns is not None else f"Bool{i}"
            out_df[_col_name] = self._generate_bools()

        return out_df

    def get_char_dataframe(self, nrows: int, ncols: int, nullratio: float = 0, columns: List[str] = None,
                           lowercase: bool = True) -> pd.DataFrame:
        """Generate a dataframe of ONLY character/byte datatype values

        Args:
            nrows (int): Number of rows
            ncols (int): Number of columns
            nullratio (float, optional): [description]. Defaults to 0.
            columns (List[str], optional): Column names of the dataframe. Defaults to None.
            lowercase (bool, optional): Characters lowercase or uppercase. Defaults to True.

        Returns:
            pd.DataFrame:
        """        
        if columns is not None:
            assert len(columns) == ncols, "Provide all or No Columns names"

        logger.info(f"Generating {nrows}x{ncols} all character dataframe")
        self._numrows = nrows

        out_df = pd.DataFrame()
        for i in range(ncols):
            _col_name = columns[i] if columns is not None else f"Char{i}"
            out_df[_col_name] = self._generate_chars(lowercase=lowercase)

        return out_df

    def get_string_dataframe(self, nrows: int, ncols: int, nullratio: float = 0, columns: List[str] = None,
                             minstrlen: int = 10, maxstrlen: int = 20) -> pd.DataFrame:
        """Generate a dataframe of ONLY string datatype values

        Args:
            nrows (int): Number of rows
            ncols (int): Number of columns
            nullratio (float, optional): [description]. Defaults to 0.
            columns (List[str], optional): Column names of the dataframe. Defaults to None.
            minstrlen (int, optional): Minimum string length. Defaults to 10.
            maxstrlen (int, optional): Maximum string length. Defaults to 20.

        Returns:
            pd.DataFrame:
        """        
        if columns is not None:
            assert len(columns) == ncols, "Provide all or No Columns names"

        logger.info(f"Generating {nrows}x{ncols} all string dataframe")
        self._numrows = nrows

        out_df = pd.DataFrame()
        for i in range(ncols):
            _col_name = columns[i] if columns is not None else f"Str{i}"
            out_df[_col_name] = self._generate_strings(_min=minstrlen, _max=maxstrlen)

        return out_df.astype(str)

    def get_dates_dataframe(self, nrows: int, ncols: int, nullratio: float = 0, columns: List[str] = None,
                            start: datetime = None, end: datetime = None) -> pd.DataFrame:
        """Generate a dataframe of ONLY datetime datatype values

        Args:
            nrows (int): Number of rows
            ncols (int): Number of columns
            nullratio (float, optional): [description]. Defaults to 0.
            columns (List[str], optional): Column names of the dataframe. Defaults to None.
            start (datetime, optional): Starting datetime range. Defaults to None.
            end (datetime, optional): Ending datetime range. Defaults to None.

        Returns:
            pd.DataFrame:
        """        
        if columns is not None:
            assert len(columns) == ncols, "Provide all or No Columns names"

        logger.info(f"Generating {nrows}x{ncols} all dates dataframe")
        self._numrows = nrows

        out_df = pd.DataFrame()
        for i in range(ncols):
            _col_name = columns[i] if columns is not None else f"Date{i}"
            out_df[_col_name] = self._generate_dates(start=start, end=end)

        return out_df


if __name__ == "__main__":
    pass
