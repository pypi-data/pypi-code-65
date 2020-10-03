import json
from typing import *

import dataclasses_json
import http_server_base.model

import openapi_parser.exporter.exporting_features.utils
from openapi_parser.parser import discriminator_decoder
from openapi_parser.util.utils import StrIO
from .abstract_writer import yielder, writer
from .footer_writer import FooterWriter
from .header_writer import HeaderWriter
from .inspect_writer import InspectWriter

class UtilsWriter(HeaderWriter, InspectWriter, FooterWriter):
    @property
    def from_imports(self) -> Iterator[str]:
        imports = \
        [
            json.dumps,
            dataclasses_json.DataClassJsonMixin,
            http_server_base.model.DataClassJsonEncoder,
        ]
        other_imports = \
        [
            'http_server_base.model.iencoder.EncodedObjType',
            'typing.*',
        ]
        
        yield from self.objects_to_from_imports(imports)
        yield from other_imports
    
    @property
    def utils(self) -> Iterator[Any]:
        yield discriminator_decoder
        yield from map(lambda attr: getattr(openapi_parser.exporter.exporting_features.utils, attr), openapi_parser.exporter.exporting_features.utils.__all__)
    
    @property
    def type_vars(self) -> Iterator[str]:
        yield 'T'
        yield 'K'
        yield 'V'
    
    def dump_utils_file(self, items: Iterable[Any] = None, *, ordered: bool = None) -> Iterator[str]:
        yield from self.dump_headers()
        yield from self.dump_type_vars()
        yield from self.dump_utils(items, ordered=ordered)
        yield from self.dump_footers()
    
    # region Writers
    @yielder
    def yield_utils_file(self, items: Iterable[Any] = None, *, ordered: bool = None) -> Iterator[Tuple[int, str]]:
        # noinspection PyTypeChecker
        return self.dump_utils_file(items, ordered=ordered)
    
    @overload
    def write_utils_file(self, items: Iterable[Any] = None, *, ordered: bool = None) -> Iterator[str]:
        pass
    # noinspection PyOverloads
    @overload
    def write_utils_file(self, items: Iterable[Any] = None, *, ordered: bool = None, file: StrIO) -> None:
        pass
    @writer
    def write_utils_file(self, items: Iterable[Any] = None, *, ordered: bool = None) -> Optional[Iterator[str]]:
        # noinspection PyTypeChecker
        return self.yield_utils_file(items, ordered=ordered)
    # endregion


__all__ = \
[
    'UtilsWriter',
]
