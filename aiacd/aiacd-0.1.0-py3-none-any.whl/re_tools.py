def re_extract_try(_object, _pattern, group=0):
    import re

    if isinstance(_object, str):
        try:
            return re.search("%s" % _pattern, _object).group(group)
        except AttributeError:
            return None
    if isinstance(_object, int):
        try:
            # I hate this type of recasting will look into docs later to see if a smarter fix is possible
            return re.search("%s" % _pattern, str(_object)).group(group)
        except AttributeError:
            return None


def re_find_all(_object, _pattern, loc=None):
    import re

    if isinstance(_object, str):
        try:
            if loc:
                return re.findall("%s" % _pattern, _object)[loc]
            else:
                return re.findall("%s" % _pattern, _object)
        except AttributeError:
            return None
    if isinstance(_object, int):
        try:
            # I hate this type of recasting will look into docs later to see if a smarter fix is possible
            if loc:
                return re.findall("%s" % _pattern, str(_object))[loc]
            else:
                return re.findall("%s" % _pattern, str(_object))
        except AttributeError:
            return None


def re_extract(_object, _pattern, group=0):
    from collections.abc import Iterable

    if isinstance(_object, str):
        if isinstance(_pattern, str):
            try:
                if __local_extractor(_object, _pattern, group) is not None:
                    yield __local_extractor(_object, _pattern, group)
                else:
                    return None
            except AttributeError:
                return None
        elif isinstance(_pattern, Iterable):
            for sub in _pattern:
                yield from re_extract(_object, sub)
        else:
            return None
    elif isinstance(_object, Iterable):
        for thing in _object:
            if isinstance(_pattern, str):
                yield from re_extract(thing, _pattern)
            elif isinstance(_pattern, Iterable):
                for sub in _pattern:
                    yield from re_extract(thing, sub)
            else:
                return None
    else:
        return None


def __local_extractor(string_to_search, pattern_to_search, group):
    import re

    m_find = re.search("%s" % pattern_to_search, string_to_search)
    if m_find:
        return m_find.group(group)
    else:
        return None


def re_search_strings():
    search_strings = {
        "search_string_RLS": r"^(RLS-)(.+)(?<=\d)(?=_)",
        "search_string_full_data_RLS": r"(RLS-)(.+)(?<=\d)(?=_)",
        "search_string_results_form": r"(AI_RLS-)(.+)(?<=\d)(?=_)",
        "search_string_RLS_directory": r"(RLS.+)(\\)",
        "search_string_doc_file": r"^(RLS)(.+)(doc)",
        "search_string_spectrum_word": r"(Spectrum)(.+)(doc)",
        "search_string_spectrum_csv": r"(Spectrum)(.+)(csv)",
        "search_string_LIMS": r"^(19)(.+?)(?=_)|(?<=_)(19\d{4,})",
        "search_string_date_first": r"^(2019)(\d+)",
        "search_string_date": r"(2019)(\d+)",
        "search_string_test": r"(47)(.+?)(?=_)",
        "search_string_free_text": r"(?<=_)([a-zA-Z].+)",
        "search_string_match_all_after_last_underscore": r"([^_]*)$",
        "search_string_excel_lims": r"(\w.+)(?=19\d{5})(19\d{5})",
        "search_string_excel_spectrum": r"^(19\d{5})(=? )(\w.+)",
        "search_string_match_exactly_seven_digits": r"(?:\b\d{7}\b)",
        "search_string_match_any_words": r"([a-zA-z])",
        "search_string_match_AI_lims_first": r"(19\d{5}|20\d{5}).([\w]*.+[^\d\W])",
        "search_string_match_AI_Name_First": r"([\w]*.+[^\d\W]).(19\d{5}|20\d{5})",
        "search_string_match_AI": r"(([\w]*.+[^\d\W])(\b..\b)(19\d{5}|20\d{5}))|(("
        r"19\d{5}|20\d{5}).([\w]*.+[^\d\W]))|(([\w]*.+[^\d\W])(\b.\b)(19\d{5}|20\d{5}))|((19\d{5}|20\d{5})(\b.\b)([\w]*.+[^\d\W]))",
        "seach_string_LIMS_in_files_Future": r"(19\d{5}|20\d{5})(?=_)",
        "search_string_AI_match_word": r"([^\d\W]+)",
        "search_string_AI_numeric_only": r"^([\d]+)",
    }

    return search_strings


def regex_yield(_object, _pattern):
    import re

    if _object:
        if isinstance(_object, str):
            if isinstance(_pattern, str):
                if re.search(_pattern, _object):
                    yield _object
                else:
                    return None
            elif not isinstance(_pattern, str):
                for sub_pattern in _pattern:
                    yield from regex_yield(_object, sub_pattern)
        elif not isinstance(_object, str):
            for thing in _object:
                if isinstance(_pattern, str):
                    if re.search(_pattern, thing):
                        yield [thing]
                elif not isinstance(_pattern, str):
                    for sub_pattern in _pattern:
                        yield from regex_yield(thing, sub_pattern)
    else:
        return None
