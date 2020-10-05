# Copyright 2020 Aptpod, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""pandas.Timestamp オブジェクトや pandas.Timedelta オブジェクト、 Unix タイムスタンプ、時刻を表す文字列の相互変換用メソッドを提供します。
"""

import numpy as np
import pandas as pd
import pytz


def timestamp2unixmicro(ts):
    """pandas.Timestampオブジェクトをマイクロ秒単位の Unix タイムスタンプへ変換します。

    Args:
        ts (pandas.Timestamp): 変換元の pandas.Timestamp オブジェクト

    Returns:
        int: マイクロ秒単位の Unix タイムスタンプ
    """
    s = "{:019d}".format(ts.value)
    return int(s[:16])


def timestamp2unix(ts):
    """pandas.Timestampオブジェクトを (秒,ナノ秒) 形式の Unix タイムスタンプへ変換します。

    Args:
        ts (pandas.Timestamp): 変換元の pandas.Timestamp オブジェクト

    Returns:
        (int, int): (秒,ナノ秒) 形式の Unix タイムスタンプ
    """
    s = "{:019d}".format(ts.value)
    return int(s[:10]), int(s[10:])


def unix2timestamp(unix_sec, unix_nano, tz=pytz.utc):
    """Unix タイムスタンプを pandas.Timestamp オブジェクトに変換します。

    Args:
        unix_sec (int): 変換元 Unix タイムスタンプの秒部分
        unix_nano (int): 変換元 Unix タイムスタンプのナノ秒部分
        tz (pytz.timezone): タイムゾーン

    Returns:
        pandas.Timestamp: 変換後の pandas.Timestamp オブジェクト
    """
    return pd.Timestamp(int(unix_sec * 1e9) + unix_nano, tz=tz)


def timedelta2micro(td):
    """pandas.Timedelta オブジェクトをマイクロ秒に変換します。

    Args:
        td (pandas.Timedelta): pandas.Timedelta オブジェクト

    Returns:
        int: 変換後の時間（マイクロ秒単位）
    """
    return int(td.value / 1e3)


def micro2timedelta(micro):
    """マイクロ秒を pandas.Timedelta オブジェクトに変換します。

    Args:
        micro (int): 変換元の時間（マイクロ秒単位）

    Returns:
        pandas.Timedelta: 変換後の pandas.Timedelta オブジェクト
    """
    return pd.Timedelta(microseconds=micro)


def timestamp2str(ts):
    """pandas.Timestamp オブジェクトを ``%Y-%m-%dT%H:%M:%S.%fZ`` 形式の文字列に変換します。

    Args:
        ts (pandas.Timestamp): 変換元の pandas.Timestamp オブジェクト

    Returns:
        str: 変換後の文字列
    """
    return ts.tz_convert("UTC").strftime(
        "%Y-%m-%dT%H:%M:%S.%f{:03d}Z".format(ts.nanosecond)
    )


def str2timestamp(s):
    """``%Y-%m-%dT%H:%M:%S.%fZ`` 形式の文字列を pandas.Timestamp オブジェクトに変換します。

    Args:
        s (str): 変換元の文字列

    Returns:
        pandas.Timestamp: 変換後の pandas.Timestamp オブジェクト
    """
    try:
        return pd.to_datetime(s, utc=True)
    except:
        return pd.NaT
