import math
from pathlib import Path
from contextlib import contextmanager
import pandas as pd
from enum import Enum
import functools
from typing import Union, List


class OutputFormat(Enum):
    __slots__ = ()
    WGS84 = 0
    TWD97 = 1


class GeoCoordinate:
    __slots__ = ()
    distance_between_longitude_on_equatorial = 0.000008983152841195214  # 赤道每公尺經度差
    distance_between_latitude = 0.00000899823754  # 每公尺緯度差

    class CSVConverter:
        __slots__ = ('csv_file',)

        def __init__(self, csv_file: Path):
            self.csv_file = csv_file

        @contextmanager
        def enter(
            self,
            col_x: Union[int, str], col_y: Union[int, str], new_col_x: Union[int, str], new_col_y: Union[int, str],
            output_format: OutputFormat,
            output_path: Path = None, sep=',', columns: List[str] = None
        ) -> pd.DataFrame:
            df = pd.DataFrame()
            try:
                gc = GeoCoordinate()
                cvt_fun = functools.wraps(gc.twd97_2_wgs84)(
                    lambda tx, ty: gc.twd97_2_wgs84(tx, ty)) if output_format is OutputFormat.WGS84 \
                    else functools.wraps(gc.wgs84_2_twd97)(
                    lambda x, y: gc.wgs84_2_twd97(x, y)) if output_format is OutputFormat.TWD97 else None
                if cvt_fun is None:
                    raise AttributeError('output_format is not correct!')
                df = pd.read_csv(self.csv_file, encoding='utf-8', sep=sep)
                new_col_x_name = new_col_x if isinstance(new_col_x, str) else '__x__'
                new_col_y_name = new_col_y if isinstance(new_col_y, str) else '__y__'
                df_xy = df[new_col_x_name] = df.apply(
                    lambda series_data: ' '.join(
                        [str(_) for _ in cvt_fun(series_data[col_x], series_data[col_y])]
                    )
                    , axis=1)
                df[[new_col_x_name, new_col_y_name]] = df_xy.str.split(expand=True)
                df = df.reindex(columns=columns)  # change the position of column.
                yield df
            finally:
                if len(df) == 0:
                    return
                if output_path is None:
                    print(df)
                    return
                if output_path.suffix.upper() == '.CSV':
                    df.to_csv(output_path, index=False)
                    return
                if output_path.suffix.lower() in ('.xlsx', '.xls'):
                    from openpyxl import Workbook
                    wb = Workbook()
                    ws = wb.active
                    ws.append(columns if columns else df.columns.tolist())
                    [ws.append(row.tolist()) for row in df.values]  # row is ndarray
                    wb.save(output_path)

    def twd97_2_wgs84(self, tx: float, ty: float):
        """
        :param tx: E ≡ x ≡ longitude
        :param ty: N ≡ y ≡ latitude
        :return:
        """
        y = ty * self.distance_between_latitude
        x = 121 + (tx - 250000) * self._distance_per_longitude(y)

        return x, y,

    def wgs84_2_twd97(self, x: float, y: float):
        ty = y / self.distance_between_latitude
        tx = (x - 121) / self._distance_per_longitude(y) + 250000
        return tx, ty

    def _distance_per_longitude(self, latitude: float):
        """
        計算該緯度每公尺的緯度差
        """
        return self.distance_between_longitude_on_equatorial / math.cos(math.radians(latitude))
