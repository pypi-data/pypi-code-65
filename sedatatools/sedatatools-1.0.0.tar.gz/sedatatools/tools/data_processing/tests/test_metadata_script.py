from sedatatools.sedatatools.tools.data_processing.create_metadata_file import check_data_type
from sedatatools.sedatatools.tools.data_processing.create_metadata_file import create_acronym
from sedatatools.sedatatools.tools.data_processing.create_metadata_file import get_table_fipses
from sedatatools.sedatatools.tools.data_processing.create_metadata_file import verify_config


class TestHelpers:
    def test_getting_config_file(self):
        tableFips = 'SL200_FIPS'
        geoLevelInfo = [
            ['SL100', 'Canada', '2', '2', '0'], [
                'SL200', 'Provinces/Territories', '2', '2', '1',
            ],
        ]
        assert get_table_fipses(
            tableFips, geoLevelInfo,
        ) == 'SL100_FIPS,SL200_FIPS'

    def test_acronym_creation(self):
        test_string = 'FORWARD SORTATION AREA'
        assert create_acronym(test_string) == 'FSA'

    def test_acronym_creation_single_word(self):
        test_string = 'state'
        assert create_acronym(test_string) == 'STATE'

    def test_acronym_creation_weird_chars(self):
        test_string = 'Province/Territories'
        assert create_acronym(test_string) == 'PT'

    def test_data_type_checks_char(self):
        assert check_data_type('char') == 1

    def test_data_type_checks_int(self):
        assert check_data_type('int') == 3

    def test_data_type_checks_float(self):
        assert check_data_type('float') == 2

    def test_config_verification(self):
        assert verify_config(r'c:\some invalid path') is False
