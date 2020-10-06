import pandas as pd
from datetime import datetime
import os

class PTRCalibration:
    TODAY = datetime.today().date()

    def __init__(self, path):
        self.file_list = list(
            map(
                lambda xcl: os.path.join(path, xcl),
                filter(
                    lambda file: os.path.splitext(file)[-1].lower() == ".xlsx",
                    os.listdir(path),
                ),
            )
        )
        self.frame = pd.DataFrame()
        self.frames = []
        self.path = path
        self.permission = []

    def extract_data(self):
        for file in self.file_list:
            try:
                read = pd.read_excel(file, sheet_name=0, header=None).dropna(how="all")
                read = read.rename(columns=read.iloc[0]).drop(read.index[0])
                self.frames.append(read)
            except PermissionError:
                self.permission.append(os.path.split(file)[-1].split("_")[0])

    def save(self):
        extracted_path = os.path.join(self.path, "Extracted")
        if not os.path.isdir(extracted_path):
            os.mkdir(extracted_path)
        archive_path = os.path.join(extracted_path, "Archive")
        if not os.path.isdir(archive_path):
            os.mkdir(archive_path)
        out = pd.concat(self.frames)
        out.to_csv(os.path.join(extracted_path, f"Extracted Log Files.csv"))
        out.to_csv(os.path.join(archive_path, f"Extracted Log Files_{self.TODAY}.csv"))