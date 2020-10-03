import json
import sys
from typing import *

import yaml

from openapi_parser.exporter import PackageWriter
from openapi_parser.model import HavingId
from openapi_parser.parser.loader import *

JUSTIFICATION_SIZE = 140
def main(args: Optional[List[str]] = None):
    if (args is None):
        args = sys.argv[1:]
    
    if (len(args) < 2):
        print(f"Not enough arguments, usage: python -m openapi_parser SCHEMA DESTINATION", file=sys.stderr)
        return 1
    
    schema_file = args[0]
    destination_dir = args[1].encode()
    
    with open(schema_file, 'rt', encoding='utf8') as f:
        if (schema_file.endswith('.json')):
            schema = json.load(f)
        elif (schema_file.endswith('.yaml') or schema_file.endswith('.yml')):
            schema = yaml.safe_load(f)
        else:
            print(f"Unsupported extension: '{''.join(schema_file.rpartition('.')[1:])}'", file=sys.stderr)
            return 1
    
    parser = OpenApiParser(schema)
    parser.load_path_items()
    
    for path, mdl in parser.loaded_objects.items():
        print(('# ' + type(mdl).__name__ + (f" '{mdl.id}'" if isinstance(mdl, HavingId) else '')).ljust(JUSTIFICATION_SIZE, ' ') + f" -- '{path}'")
    print('# ' + '=' * JUSTIFICATION_SIZE)
    print('')
    
    package_writer = PackageWriter(destination_dir)
    package_writer.write_package(parser, clean=True)
    
    return 0

if (__name__ == '__main__'):
    exit_code = main()
    exit(exit_code)
