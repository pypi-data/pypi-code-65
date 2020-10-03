from basic_http.data_structures.multikey import MultiKeyDictionary
import basic_http.exceptions.structures


class HttpHeader(object):
    def __init__(self, data: dict = None):
        self.__header = MultiKeyDictionary()

        if data:
            self.update(data)

    @staticmethod
    def __check_data(data):
        try:
            for key, value in data.items():
                if not isinstance(key, str) and not isinstance(value, str):
                    raise basic_http.exceptions.structures.WrongHttpHeaderDataType('Header data must be str.')
        except AttributeError:
            raise basic_http.exceptions.structures.\
                WrongHttpHeaderDataType(f'Data must be dict or { MultiKeyDictionary() } object.')

    def update(self, header) -> None:
        self.__check_data(header)
        self.__header.update(header)

    def add(self, header):
        self.__check_data(header)

        for name, value in header.items():
            self.__header.add(name, value)

    def add_one(self, name, value):
        self.add({
            name: value
        })

    def get_all_header(self, header_name: str) -> list:
        self.__check_data({
            header_name: ''
        })

        results = []
        for key, value in self.__header.items():
            if key.lower() == header_name.lower():
                results.append(value)

        return results

    def get_cookies(self):
        return self.get_all_header('Set-Cookie')

    def __setitem__(self, header_name: str, header_value) -> None:
        self.__check_data({
            header_name: header_value
        })

        self.__header[header_name] = header_value

    def __getitem__(self, header_name: str) -> str:
        self.__check_data({
            header_name: ''
        })

        for key, value in self.__header.items():
            if key.lower() == header_name.lower():
                return value

        raise basic_http.exceptions.structures.KeyNotFound(f'Header \'{ header_name }\' does not exist.')

    def __str__(self) -> str:
        header = str()
        for key, value in self.__header.items():
            header += key + ': ' + value + '\r\n'

        return header

    def __iter__(self):
        for key, value in self.__header.items():
            yield key
