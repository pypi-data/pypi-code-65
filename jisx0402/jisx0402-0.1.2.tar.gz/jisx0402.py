import csv
from typing import List
import re

from pydantic import BaseModel


class Record(BaseModel):
    code: str  # 全国地方公共団体コード
    prefecture: str  # 都道府県名
    prefecture_kana: str  # 都道府県名(半角カナ)
    city: str  # 市町村名
    city_kana: str  # 市町村名(半角カナ)

    @property
    def full_city_name(self) -> str:
        """都道府県名 + 市町村名
        e.g. 福岡県福岡市
        """
        return self.prefecture + self.city

    @property
    def full_city_name_kana(self) -> str:
        """都道府県名 + 市町村名(半角カナ)
        e.g. ﾎｯｶｲﾄﾞｳｻｯﾎﾟﾛｼ
        """
        return self.prefecture_kana + self.city_kana

    @property
    def attrs(self) -> List[str]:
        return [
            "code",
            "prefecture",
            "prefecture_kana",
            "city",
            "city_kana",
            "full_city_name",
            "full_city_name_kana",
        ]


CODES = []
RECORDS = []

with open("data.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        CODES.append(row["code"])
        RECORDS.append(Record(**row))

CODE_TO_RECORD = dict(zip(CODES, RECORDS))


def code2record(code) -> Record:
    return CODE_TO_RECORD[str(code).zfill(6)]


def search(key: str, pattern: str) -> List[Record]:
    """指定したkeyについて正規表現で検索する
    e.g.) search("prefecture", r"福.県")
    """
    assert hasattr(RECORDS[0], key), f"Choose key from {RECORDS[0].attrs}"
    return [r for r in RECORDS if re.match(pattern, getattr(r, key))]
