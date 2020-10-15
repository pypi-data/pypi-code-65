"""
This will subtract table suffixes by one
"""

from pathlib import Path
from lxml import etree as et


def main():
    # location of the xmls
    path = Path(r'C:\Projects\CEDMetadata')

    # take one file at a time, and take only xml type of files
    for file_name in path.glob('*.xml'):
        print(f'Starting {file_name.name}')

        # read and parse xml file
        parser = et.XMLParser(strip_cdata=False)

        try:
            metadata_document = et.parse(str(file_name), parser=parser)
        except et.XMLSyntaxError:
            # in case the xml is not correctly formated
            print(f'Skipping {file_name.name}')

        tables = metadata_document.xpath("//SurveyDataset[@abbreviation='ORG']//table")

        process_file = True

        for table in tables:

            table_suffix = table.attrib['name'][-3:]

            if table_suffix == '001':
                process_file = False

            if not process_file:
                continue

            try:
                new_table_suffix = '_' + '0' * (3 - len(str(int(table_suffix) - 1))) + str(int(table_suffix) - 1)
                table_suffix = '_' + table_suffix
            except ValueError:
                print(table_suffix)

            table.attrib['name'] = table.attrib['name'].replace(table_suffix, new_table_suffix)
            table.attrib['displayName'] = table.attrib['displayName'].replace(table_suffix, new_table_suffix)
            try:
                table.attrib['uniqueTableId'] = table.attrib['uniqueTableId'].replace(table_suffix, new_table_suffix)
            except KeyError:
                print('No uniqueTableId, skipping ...')

                # change variable ids
                variables = table.xpath('.//variable')
                for variable in variables:
                    variable.attrib['name'] = variable.attrib['name'].replace(table_suffix, new_table_suffix)

        try:
            metadata_document.write('./output_for_fixed_files/' + file_name.name)
        except OSError:
            print('Invalid argument')


if __name__ == '__main__':
    main()
