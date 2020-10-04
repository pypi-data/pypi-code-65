import re
from itertools import chain
from ipaddress import ip_address
from datetime import datetime

from CGPCLI.Errors import NotValidCGPStringError

class IP():
    def __init__(self, ip, port=None):
        self.ip = ip_address(ip)
        if port is not None:
            self.port = port
        
    def __repr__(self):
        try:
            return f'IPAddress {self.ip}:{self.port}'
        except AttributeError:
            return f'IPAddress {self.ip}'
        
    def __eq__(self, other):
        try:
            return True if f'{self.ip}:{self.port}' == f'{other.ip}:{other.port}' else False
        except AttributeError:
            return True if self.ip == other.ip else False

def parse_to_python_object(string):
    def sequence(*funcs):
        if len(funcs) == 0:
            def result(src):
                yield (), src
            return result
        def result(src):
            for arg1, src in funcs[0](src):
                for others, src in sequence(*funcs[1:])(src):
                    yield (arg1,) + others, src
        return result

    number_regex = re.compile(r"#(-?(?:(?:0x[\da-fA-F]+)|(?:0[ob])?\d+))(.*)", re.DOTALL)
    
    def parse_number(src):
        match = number_regex.match(src)
        if match is not None:
            number, src = match.groups()
            if '0b' in number:
                number = int(number, 2)
            elif '0o' in number:
                number = int(number, 8)
            elif '0x' in number:
                number = int(number, 16)
            else:
                number = int(number)
            yield number, src
    
    date_regex = re.compile(r"(\#T(?:\d{2}-\d{2}-\d{4}_\d{2}:\d{2}:\d{2}))\s*(.*)", re.DOTALL)

    def parse_date(src):
        match = date_regex.match(src)
        if match is not None:
            date, src = match.groups()
            yield datetime.strptime(date, '#T%d-%m-%Y_%H:%M:%S'), src

    ip_regex = re.compile(r"#I\[([a-zA-Z0-9.:]*)](?::(\d+))?(.*)", re.DOTALL)

    def parse_ip(src):
        match = ip_regex.match(src)
        if match is not None:
            ip, port, src = match.groups()
            yield IP(ip, port), src
    
    datablock_regex = re.compile(r"(\[.*\])(.*)", re.DOTALL)        

    def parse_datablock(src):
        match = datablock_regex.match(src)
        if match is not None:
            sert, src = match.groups()
            yield sert, src

    quoted_regex = re.compile(r"^\"(.*?(?<!\\))\"(.*)", re.DOTALL)
    unquoted_regex = re.compile(r"^([\w.@#-]+)(.*)", re.DOTALL)

    def parse_string(src):
        match = quoted_regex.match(src)
        if match is not None:
            string, src = match.groups()
            yield string, src.lstrip()
            
        match = unquoted_regex.match(src)
        if match is not None:
            string, src = match.groups()
            yield string, src.lstrip()      

    def parse_word(word, value=None):
        l = len(word)
        def result(src):
            if src.startswith(word):
                yield value, src[l:].lstrip()
        result.__name__ = "parse_%s" % word
        return result

    parse_true = parse_word("true", True)
    parse_false = parse_word("false", False)
    parse_null = parse_word("null", None)

    def parse_value(src):
        for match in chain(
            parse_number(src),
            parse_ip(src),
            parse_datablock(src),
            parse_date(src),
            parse_true(src),
            parse_false(src),
            parse_null(src),
            parse_string(src),
            parse_array(src),
            parse_object(src),
            ):
            yield match
            return

    parse_left_bracket = parse_word("(")
    parse_right_bracket = parse_word(")")
    parse_empty_array = sequence(parse_left_bracket, parse_right_bracket)

    def parse_array(src):
        for _, src in parse_empty_array(src):
            yield [], src
            return

        for (_, items, _), src in sequence(
            parse_left_bracket,
            parse_comma_separated_values,
            parse_right_bracket,
            )(src):
            yield items, src

    parse_comma = parse_word(",")

    def parse_comma_separated_values(src):
        result = []
        for value, src in parse_value(src):
            result.append(value)
            break
        else:
            return
        while src:
            for (_, value), src in sequence(parse_comma, parse_value)(src):
                result.append(value)
                break
            else:
                break
        yield result, src

    parse_left_curly_bracket = parse_word("{")
    parse_right_curly_bracket = parse_word("}")
    parse_semicolomn = parse_word(";")
    parse_empty_object = sequence(parse_left_curly_bracket, parse_right_curly_bracket)

    def parse_object(src):
        for _, src in parse_empty_object(src):
            yield {}, src
            return
        for (_, items, _), src in sequence(
            parse_left_curly_bracket,
            parse_semicolomn_separated_keyvalues,
            parse_right_curly_bracket,
            )(src):
            yield items, src

    parse_equals = parse_word("=")

    def parse_keyvalue(src):
        for (key, _, value, _), src in sequence(
            parse_string,
            parse_equals,
            parse_value,
            parse_semicolomn,
            )(src):
            yield {key: value}, src
 
    def parse_semicolomn_separated_keyvalues(src):
        result = {}
        for value, src in parse_keyvalue(src):
            result.update(value)
            break
        else:
            return
        while src:
            for (value), src in parse_keyvalue(src):
                result.update(value)
                break
            else:
                break
        yield result, src

    string = string.replace('\n', '')

    match = list(parse_value(string))

    if len(match) != 1:
        raise NotValidCGPStringError()

    result, src = match[0]
    
    return result

def parse_to_CGP_object(python_object):
    result = ''
    
    if isinstance(python_object, str):
        if '"' in python_object:
            python_object = python_object.replace('"','\"')
        result += f'"{python_object}"'
    
    elif isinstance(python_object, int):
        result += f'#{str(python_object)}'
    
    elif isinstance(python_object, dict):
        result += '{' + ''.join(f'"{str(x)}" = {parse_to_CGP_object(y)};' for x, y in zip(list(python_object.keys()), list(python_object.values()))) + '}'
            
    elif isinstance(python_object,list):
        result += '(' + ''.join(parse_to_CGP_object(x) + ', ' for x in python_object)[:-2] + ')'
    
    elif isinstance(python_object, datetime):
        result += datetime.strftime(python_object, '#T%d-%m-%Y_%H:%M:%S')
    
    elif isinstance(python_object, IP):
        result += f'#I[{python_object.ip}]'
        try:
            result += f':{python_object.port}'
        except AttributeError:
            pass
        
    elif isinstance(python_object, True):
        result += "true"
    
    elif isinstance(python_object, False):    
        result += "false"
        
    elif isinstance(python_object, None):
        result += "null"
        
    return result