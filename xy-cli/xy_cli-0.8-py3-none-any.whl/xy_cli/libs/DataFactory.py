from faker import Faker

# https://faker.readthedocs.io/en/master/providers.html
DEAULT_MOCK_DATA_TYPE = [
    # ramdam
    'locale',
    'language_code',
    'random_int',
    'random_digit',
    'random_digit_not_null',
    'random_digit_or_empty',
    'random_digit_not_null_or_empty',
    'random_number',
    'random_letter',
    'random_letters',
    'random_lowercase_letter',
    'random_uppercase_letter',
    'random_elements',
    'random_choices',
    'random_element',
    'random_sample',
    'randomize_nb_elements',
    'numerify',
    'lexify',
    'bothify',
    'hexify',

    # address
    'city_suffix',
    'street_suffix',
    'building_number',
    'city',
    'street_name',
    'street_address',
    'postcode',
    'address',
    'country',
    'country_code',

    # automotive
    'license_plate',

    # bank
    'bank_country',
    'bban',
    'iban',
    'swift8',
    'swift11',
    'swift',

    # ena
    'ean',
    'ean8',
    'ean13',
    'localized_ean',
    'localized_ean8',
    'localized_ean13',

    # color
    'color_name',
    'safe_color_name',
    'hex_color',
    'safe_hex_color',
    'rgb_color',
    'rgb_css_color',
    'color',

    # company
    'company',
    'company_suffix',
    'catch_phrase',
    'bs',

    # credit_card
    'credit_card_provider',
    'credit_card_number',
    'credit_card_expire',
    'credit_card_full',
    'credit_card_security_code',

    # currency
    'currency',
    'currency_code',
    'currency_name',
    'currency_symbol',
    'cryptocurrency',
    'cryptocurrency_code',
    'cryptocurrency_name',

    # date_time
    'unix_time',
    'time_delta',
    'date_time',
    'date_time_ad',
    'iso8601',
    'date',
    'date_object',
    'time',
    'time_object',
    'date_time_between',
    'date_between',
    'future_datetime',
    'future_date',
    'past_datetime',
    'past_date',
    'date_time_between_dates',
    'date_between_dates',
    'date_time_this_century',
    'date_time_this_decade',
    'date_time_this_year',
    'date_time_this_month',
    'date_this_century',
    'date_this_decade',
    'date_this_year',
    'date_this_month',
    'time_series',
    'distrib',
    'am_pm',
    'day_of_month',
    'day_of_week',
    'month',
    'month_name',
    'year',
    'century',
    'timezone',
    'pytimezone',
    'date_of_birth',

    # file
    'mime_type',
    'file_name',
    'file_extension',
    'file_path',
    'unix_device',
    'unix_partition',

    # Geo
    'coordinate',
    'latitude',
    'longitude',
    'latlng',
    'local_latlng',
    'location_on_land',

    # internet
    'email',
    'safe_domain_name',
    'safe_email',
    'free_email',
    'company_email',
    'free_email_domain',
    'ascii_email',
    'ascii_safe_email',
    'ascii_free_email',
    'ascii_company_email',
    'user_name',
    'hostname',
    'domain_name',
    'domain_word',
    'dga',
    'tld',
    'http_method',
    'url',
    'ipv4_network_class',
    'ipv4',
    'ipv4_private',
    'ipv4_public',
    'ipv6',
    'mac_address',
    'port_number',
    'uri_page',
    'uri_path',
    'uri_extension',
    'uri',
    'slug',
    'image_url',

    # isbn
    'isbn13',
    'isbn10',

    # job
    'job',

    # lorem
    'words',
    'word',
    'sentence',
    'sentences',
    'paragraph',
    'paragraphs',
    'text',
    'texts',

    # misc
    'boolean',
    'null_boolean',
    'binary',
    'md5',
    'sha1',
    'sha256',
    'uuid4',
    'password',
    'zip',
    'tar',
    'dsv',
    'csv',
    'tsv',
    'psv',
    'json',
    'process_list_structure',
    'process_dict_structure',
    'create_json_structure',
    'fixed_width',

    # Person
    'name',
    'first_name',
    'last_name',
    'name_male',
    'name_nonbinary',
    'name_female',
    'first_name_male',
    'first_name_nonbinary',
    'first_name_female',
    'last_name_male',
    'last_name_nonbinary',
    'last_name_female',
    'prefix',
    'prefix_male',
    'prefix_nonbinary',
    'prefix_female',
    'suffix',
    'suffix_male',
    'suffix_nonbinary',
    'suffix_female',
    # 'language_name',

    # number
    'phone_number',
    'country_calling_code',
    'msisdn',

    # profile
    'simple_profile',
    'profile',

    # python
    'pybool',
    'pystr',
    'pystr_format',
    'pyfloat',
    'pyint',
    'pydecimal',
    'pytuple',
    'pyset',
    'pylist',
    'pyiterable',
    'pydict',
    'pystruct',

    # ssn
    'ssn',

    # user_agent
    'mac_processor',
    'linux_processor',
    'user_agent',
    'chrome',
    'firefox',
    'safari',
    'opera',
    'internet_explorer',
    'windows_platform_token',
    'linux_platform_token',
    'mac_platform_token',
    'android_platform_token',
    'ios_platform_token',
]


class DataFactory():

    def __init__(self, langs=['ja_JP']):
        self.fake = Faker(langs)

    def get_mock_data(self, mock_data_type, default_value, seq):
        if default_value:
            dvs = default_value.split("\n")
            return dvs[self.fake.random_int(min=0, max=len(dvs) - 1)]
        if mock_data_type == "auto_increment":
            val = seq
        elif mock_data_type in DEAULT_MOCK_DATA_TYPE:
            val = getattr(self.fake, mock_data_type)()
        return val
