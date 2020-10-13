import re


class Chevrons:
    def __init__(self, original_string):
        self.pattern = re.compile('[\"|\'][^\"\']+[\"|\']')
        self.original_string = original_string

    def __is_applicable(self, original_string: str) -> bool:

        return bool(
            re.findall(self.pattern, original_string)
        )

    def __chevronize(self, quoted_string: str) -> str:

        as_list = list(quoted_string)

        as_list[0] = '«'
        as_list[-1] = '»'

        return "".join(as_list)

    def __get_matches(self, original_string: str) -> list:

        return [
            match.group(0) for match in re.finditer(
                pattern=self.pattern, string=original_string
            )
        ]

    def __remove_unpaired_quotes(self, original_string: str) -> str:

        return original_string.replace("\'", "").replace("\"", "")

    def apply(self) -> str:

        if self.__is_applicable(self.original_string):
            for quoted_string in self.__get_matches(self.original_string):
                self.original_string = self.original_string.replace(
                    quoted_string, self.__chevronize(quoted_string)
                )
        self.original_string = self.__remove_unpaired_quotes(self.original_string)

        return self.original_string
