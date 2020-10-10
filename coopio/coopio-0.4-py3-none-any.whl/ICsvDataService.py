from abc import ABC, abstractmethod
import pandas as pd
import os
from typing import TypeVar, Dict, List
from coopio.IDataService import IDataService

T = TypeVar('T')

class ICsvDataService(IDataService):

    def __init__(self, data_file_path: str):
        self.data_file_path = data_file_path
        self.create_file_if_not_exists(self.data_file_path)

    def read_in_data(self, file_path: str):
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            return None

    def write_data(self, df: pd.DataFrame, file_path: str):
        self.create_file_if_not_exists(file_path)
        try:
            df.to_csv(file_path, index=False)
            return True
        except:
            return False

    def create_file_if_not_exists(self, file_path):
        if not os.path.exists(file_path):
            with open(file_path, "w"):
                pass

    def add_or_update(self, obj_identifier: str, objs: List[T]) -> bool:
        existing_data = self.read_in_data(self.data_file_path)

        if existing_data is not None:
            for obj in objs:
                new_data = pd.Series(vars(obj))
                existing_line = next(
                    ((i, line) for i, line in existing_data.iterrows() if str(line[obj_identifier]) == str(vars(obj)[obj_identifier])), None)

                if existing_line:
                    existing_data.loc[existing_line[0], existing_line[1].index] = new_data.values
                else:
                    existing_data = existing_data.append(new_data, ignore_index=True)

        else:
            existing_data = pd.DataFrame([vars(obj) for obj in objs])

        return self.write_data(existing_data, self.data_file_path)

    def retrieve_data(self, obj_identifier: str, ids: List[str] = None) -> List[T]:
        existing_data = self.read_in_data(self.data_file_path)

        if existing_data is not None:
            if ids is not None:
                existing_data = existing_data[existing_data[obj_identifier].isin(ids)]

            ret = self.translate_from_data_rows(existing_data)
        else:
            ret = []

        return ret

    def delete(self, obj_identifier: str, ids: List[str]) -> Dict[str, bool]:
        existing_data = self.read_in_data(self.data_file_path)
        if existing_data is None:
            return {id: True for id in ids}

        ret = {}
        new_data = existing_data
        for id in ids:
            try:
                existing_indexes = [i for i, line in existing_data.iterrows() if str(line[obj_identifier]) == id]

                new_data = new_data.drop(existing_indexes)
                ret[id] = True
            except:
                ret[id] = False

        self.write_data(new_data, self.data_file_path)
        return ret

    @abstractmethod
    def translate_from_data_rows(self, df: pd.DataFrame) -> List[T]:
        pass

