import json
from pathlib import Path

import pyodbc
from lxml import etree as et

# from sedatatools.tools.connectors.prime import Prime

"""
This class will be used to retrieve values from the database
Parts of if are based on the old dataget app which is now deprecated

Constructor should load the data for all years if not specified differently in the first or 'level' argument.
Level should accept string with name (e.g. Nation) or summary level (e.g. SL010).

 Properties on the Survey level:

    - number of datasets
    - number of tables
    - number of variables

 Properties on the Dataset level:

    - number of tables
    - number of variables

 Properties on the Table level:

    - number of variables
    - metadata (description)
    - min
    - max
    - avg
    - median
    - full title
    - title wrapped
    - NA number
    - shape

 Properties on the Variable level:
    - metadata (description)
    - format
    - type
    - full title
    - title wrapped
    - aggregation method

Usage:
 First step is to create an object with project_name as a parameter.
 Data will be accessed as the nested properties Survey>Dataset>Table>Variable e.g. ACS2018_5yr.SE.A00001.A00001_001

"""


# class ValueElement:
#     """
#     This is a base class for the elements with values in the DB i.e. tables and variables
#     """
#
#     def __init__(self):
#         self.prime_credentials = Prime()
#         self.db_name = 'master'  # TODO change this later on
#
#         try:
#             conn = pyodbc.connect(f'driver={{ODBC Driver 13 for SQL Server}};server=prime,1433;'
#                                   f'database={self.db_name};UID={self.prime_credentials.user_name};PWD={self.prime_credentials.password}')
#         except pyodbc.Error:
#             conn = pyodbc.connect(f'driver={{SQL server}};server=prime,1433;'
#                                   f'database={self.db_name};UID={self.prime_credentials.user_name};PWD={self.prime_credentials.password}')
#
#         self.cursor = conn.cursor()


class Helpers:
    def __init__(self, metadata_location=r'C:\Projects\Website-ASP.NET\pub\ReportData\Metadata'):
        self.project_id_to_file_name_map = {}
        self.extract_project_ids(metadata_location)

    def extract_project_ids(self, metadata_location):
        """
        Use only first two lines of every file to quickly extract project names from the metadata XMLs
        """

        metadata_location = Path(metadata_location)
        for file in metadata_location.glob('*.xml'):
            with open(str(file), 'r', encoding="mbcs") as f:
                try:
                    raw_survey_tag = [
                        line for line in [
                        next(f) for _ in range(2)
                        ] if 'survey' in line
                    ][0]
                except IndexError:
                    continue  # if there's no survey tag just continue
                except Exception as e:
                    print(e)
                survey_tag = et.ElementTree(
                    et.fromstring(raw_survey_tag + '</survey>'),
                )
                project_id = str(survey_tag.xpath('//survey/@name')[0])
                self.project_id_to_file_name_map[project_id] = Path.joinpath(
                    metadata_location, file.name,
                )

    @staticmethod
    def get_metadata(metadata_file_path):
        doc = et.parse(str(metadata_file_path))
        return doc


class Variable:
    def __init__(self, xml_element_variable):
        # super().__init__()
        self.name = xml_element_variable.attrib['name']
        self.label = xml_element_variable.attrib['title']
        self.q_label = xml_element_variable.attrib['qLabel']
        self.guid = xml_element_variable.attrib['GUID']
        self.formula = xml_element_variable.attrib['FormulaFunctionBodyCSharp']
        self.type = xml_element_variable.attrib['dataType']
        self.format = xml_element_variable.attrib['formatting']
        self.customFormatStr = xml_element_variable.attrib['customFormatStr']
        self.agg_method = xml_element_variable.attrib['AggregationStr']

    # def values(self, lvl):
    #     self.cursor.execute(f'SELECT {self.levels[lvl]} FROM {self.name}')  # this doesn't work yet TODO
    #     table_value = self.cursor.fetchall()
    #     return table_value

    @staticmethod
    def name_type(database_type):
        if database_type == '3':
            return 'integer'
        else:
            return 'unknown'

    def to_json(self):
        return json.dumps(self, default=lambda x: x.__dict__, sort_keys=True, indent=4)


class Table:
    def __init__(self, xml_element_table):
        # super().__init__()
        self.name = xml_element_table.attrib['name']
        self.title = xml_element_table.attrib['title']
        self.titleWrapped = xml_element_table.attrib['titleWrapped']
        self.guid = xml_element_table.attrib['GUID']
        self.visibility_map = xml_element_table.attrib['VisibleInMaps']
        self.visibility_report = xml_element_table.attrib['Visible']
        self.table_suffix = xml_element_table.attrib['DbTableSuffix']

        self.number_of_variables = len(xml_element_table.xpath('.//variable'))
        self.variable = {}

        for variable in xml_element_table.xpath('.//variable'):
            self.variable[variable.attrib['name']] = Variable(variable)

        # self.min_value: int
        # self.max_value: int
        # self.avg_value: int
        # self.median_values: int
        # self.null_count: int
        # self.shape: tuple

    # def values(self, lvl):
    #     self.cursor.execute(f'SELECT * FROM {self.levels[lvl]} + {self.table_suffix}')
    #     table_value = self.cursor.fetchall()
    #     return table_value

    def to_json(self):
        return json.dumps(self, default=lambda x: x.__dict__, sort_keys=True, indent=4)

    # min_value: int
    # max_value: int
    # avg_value: int
    # median_values: int
    # null_count: int
    # shape: tuple


class Dataset:

    def __init__(self, xml_element_dataset):
        self.name = xml_element_dataset.attrib['name']
        self.display_name = xml_element_dataset.attrib['DisplayName']
        self.guid = xml_element_dataset.attrib['GUID']
        self.abbreviation = xml_element_dataset.attrib['DisplayName']
        self.visibility = xml_element_dataset.attrib['Visible']
        self.db_name = xml_element_dataset.attrib['name']

        self.number_of_tables = len(xml_element_dataset.xpath('.//table'))
        self.number_of_variables = len(
            xml_element_dataset.xpath('.//variable'),
        )

        self.table = {}
        for table in xml_element_dataset.xpath('.//table'):
            self.table[table.attrib['name']] = Table(table)

        self.tables_list = self.table.keys()

    def to_json(self):
        return json.dumps(self, default=lambda x: x.__dict__, sort_keys=True, indent=4)


class Survey:

    def __init__(self, project_id):
        self.datasets = {}

        self.metadata_file_name = Helpers(
        ).project_id_to_file_name_map[project_id]

        self.project_metadata = Helpers().get_metadata(self.metadata_file_name)

        self.levels = self.project_metadata.xpath('//geoType/@Label')
        self.summary_levels = self.project_metadata.xpath('//geoType/@Name')

        self.survey = self.project_metadata.xpath('//survey')[0]

        self.name = self.survey.attrib['name']
        self.display_name = self.survey.attrib['DisplayName']
        self.guid = self.survey.attrib['GUID']
        self.abbreviation = self.survey.attrib['DisplayName']
        self.visibility = self.survey.attrib['Visible']

        self.optimized_retrieval = self.project_metadata.xpath['//UseOptimizedDataRetrieval'][0]
        self.project_id = project_id

        self.number_of_datasets = len(
            self.project_metadata.xpath['//SurveyDataset'],
        )
        self.number_of_tables = len(self.project_metadata.xpath['//table'])
        self.number_of_variables = len(
            self.project_metadata.xpath['//variable'],
        )

        for dataset in self.project_metadata.xpath('//SurveyDataset'):
            self.datasets[dataset.attrib['name']] = Dataset(dataset)

    def to_json(self):
        return json.dumps(self, default=lambda x: x.__dict__, sort_keys=True, indent=4)

    name: str
    display_name: str
    guid: str
    visibility: bool
    optimized_retrieval: str
    datasets: dict
    hash: str
    file_name: str

    number_of_datasets: int
    number_of_tables: int
    number_of_variables: int


if __name__ == '__main__':
    test_ob = Survey('ACS2018_5yr')

    print(test_ob)
