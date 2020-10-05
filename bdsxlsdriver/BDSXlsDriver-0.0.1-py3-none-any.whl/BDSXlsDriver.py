import xlrd
import xlwt
from xlutils.copy import copy as xl_copy
from robot.api import logger
from SeleniumLibrary.base import keyword, LibraryComponent
from robot.libraries.BuiltIn import BuiltIn
import json

class BDSXlsDriver:
    def __init__(self, file=None):
        self.file = file

    @keyword
    def _write_to_existing_excel(self, value, column='A', row='1', sheet_name='Sheet1'):
        rd = xlrd.open_workbook(self.file, formatting_info=True)
        wb = xl_copy(rd)
        sheet = None
        if sheet_name not in rd.sheet_names():
            sheet = wb.add_sheet(sheet_name)
            wb.save(self.file)
        else:
            sheet = wb.get_sheet(sheet_name)

        sheet.write(
            int(row) - 1, self._convert_from_label_to_index(column), value)
        wb.save(self.file)

    @keyword
    def _read_from_existing_excel(self, column='A', row='1', sheet_name='Sheet1'):
        wb = xlrd.open_workbook(self.file)
        if sheet_name not in wb.sheet_names():
            return ''

        sheet = wb.sheet_by_name(sheet_name)
        value = sheet.cell_value(
            int(row) - 1, self._convert_from_label_to_index(column))

        return value if value else ''

    def _convert_from_label_to_index(self, label):
        label = label.upper()
        result = 0
        for x in label:
            result *= 26
            result += ord(x) - 65 + 1

        return result - 1