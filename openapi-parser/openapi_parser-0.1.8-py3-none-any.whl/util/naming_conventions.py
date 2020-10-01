import re
from typing import Callable

import stringcase

Converter = Callable[[str], str]

def smart_pascal_case(s: str) -> str:
    return stringcase.pascalcase(s.replace(' ', '_').replace('-', '_'))

def smart_snake_case(s: str) -> str:
    s = re.sub(r"[\-.\s]", '_', str(s))
    return re.sub(r"([A-Z](?=[^A-Z]|$)|(?<=[a-z])[A-Z])", r'_\1', s).lower().strip('_')

def smart_const_case(s: str) -> str:
    return smart_snake_case(s).upper()

class_name: Converter = smart_pascal_case
enum_entry_name: Converter = smart_pascal_case
field_name: Converter = smart_snake_case
const_name: Converter = smart_const_case
method_name: Converter = smart_snake_case

def class_name_from_path(cls_path: str) -> str:
    return class_name('_'.join(cls_path.split('/')))


__all__ = \
[
    'Converter',
    
    'class_name',
    'class_name_from_path',
    'const_name',
    'enum_entry_name',
    'field_name',
    'method_name',
    'smart_const_case',
    'smart_pascal_case',
    'smart_snake_case',
]
