import dataclasses
import datetime
import enum
import logging
import urllib.parse
from functools import partial
from typing import *

import http_server_base
import http_server_base.model
import http_server_base.tools
import tornado.httpclient
from functional import Option, OptionNone, Some

import openapi_parser.exporter.exporting_features.client
from openapi_parser.model import ModelPath, ModelServer
from openapi_parser.parser import OpenApiParser
from openapi_parser.util.naming_conventions import name_parts
from openapi_parser.util.utils import StrIO
from .abstract_writer import yielder, writer
from .footer_writer import FooterWriter
from .header_writer import HeaderWriter
from .inspect_writer import InspectWriter
from .method_writer import MethodWriter, MethodType

class ClientWriter(HeaderWriter, InspectWriter, MethodWriter, FooterWriter):
    @property
    def from_imports(self) -> Iterator[str]:
        imports =\
        [
            dataclasses.dataclass,
            dataclasses.field,
            datetime.date,
            datetime.datetime,
            datetime.time,
            enum.Enum,
            http_server_base.model.IEncoder,
            http_server_base.SubrequestClient,
            http_server_base.tools.HttpSubrequest,
            http_server_base.tools.RequestLogger,
            logging.getLogger,
            tornado.httpclient.HTTPRequest,
            urllib.parse.ParseResult,
            urllib.parse.urlparse,
        ]
        other_imports = \
        [
            'typing.*',
            '.model.*',
            '.utils.datetime_decoder',
            '.utils.filter_out_smart',
            '.utils.FilteringJsonEncoder',
        ]
        
        yield from self.objects_to_from_imports(imports)
        yield from other_imports
    
    def parse_server_data(self, client_name: str, servers: List[ModelServer]) -> Option[Tuple[str, Iterator[str]]]:
        servers = [ s for s in servers if (s.url != '/') ]
        if (not servers):
            return OptionNone
        
        def _name_gen(s: ModelServer) -> Option[str]:
            return Option(s.description or s.url).map(self.enum_entry_name_pretty).map(self.object_valid_name_filter)
        
        default_server_name = _name_gen(servers[0]).get_or_else('Server1')
        enum_name = self.class_name_pretty(client_name + '-' + 'servers')
        def _gen() -> Iterator[str]:
            self.export(enum_name)
            yield f'class {enum_name}(Enum(str)):'
            with self.indent():
                yield from self.inline_description(f"Enum-container of default servers used for `{client_name}`")
                for i, s in enumerate(servers):
                    s_name = _name_gen(s).get_or_else(f'Server{i + 1}')
                    yield f'{s_name} = {s.url!r}'
            yield
        
        return Some((f'{enum_name}.{default_server_name}' , _gen()))
    
    def dump_client_class(self, parser: OpenApiParser) -> Iterator[str]:
        package_name_parts = name_parts(parser.name)
        if (package_name_parts[-1] == 'client'):
            package_name_parts.pop(-1)
        
        package_name_parts.append('api')
        package_name_parts.append('client')
        client_name = self.class_name_pretty(parser.id_separator.join(package_name_parts))
        logger_name = f'{parser.name}.client'
        self.export(client_name)
        
        default_server, enum_gen = Option(parser.metadata).flat_map(lambda m: self.parse_server_data(client_name, m.servers)).tuple_transform(2) # type: Option[str], Option[Iterator[str]]
        if (enum_gen.non_empty):
            yield from enum_gen.get
        
        yield '@dataclass'
        yield f"class {client_name}(SubrequestClient):"
        with self.indent():
            yield from self.smart_description(partial(self.generate_item_description, item=Option(parser.metadata).map(lambda m: m.info).as_optional, item_type='client'))
            
            yield "server: str" + default_server.map(' = {}'.format).get_or_else('')
            yield "logger_name: str = " + self.constructor('field', init=False, repr=False, default=repr(logger_name))
            yield "model_encoder: Type[IEncoder] = " + self.constructor('field', init=False, repr=False, default='FilteringJsonEncoder')
            yield
            
            yield '# region Utility Methods'
            yield from self.dump_class_methods(openapi_parser.exporter.exporting_features.client)
            yield '# endregion'
            
            yield '# region Client Methods'
            for path, mdl in parser.loaded_objects.items():
                if (isinstance(mdl, ModelPath)):
                    for http_method, e in mdl.endpoints.items():
                        yield from self.dump_endpoint(e, endpoint_path=mdl.endpoint_path, http_method=http_method, method_type=MethodType.RegularMethod, asynchronous=True)
            yield '# endregion'
            yield
    
    def dump_client_file(self, parser: OpenApiParser) -> Iterator[str]:
        yield from self.dump_headers()
        yield from self.dump_client_class(parser)
        yield from self.dump_footers()
    
    # region Writers
    @yielder
    def yield_client_class(self, p: OpenApiParser) -> Iterator[Tuple[int, str]]:
        # noinspection PyTypeChecker
        return self.dump_client_class(p)
    
    @overload
    def write_client_class(self, p: OpenApiParser) -> Iterator[str]:
        pass
    # noinspection PyOverloads
    @overload
    def write_client_class(self, p: OpenApiParser, *, file: StrIO) -> None:
        pass
    @writer
    def write_client_class(self, p: OpenApiParser) -> Optional[Iterator[str]]:
        # noinspection PyTypeChecker
        return self.yield_client_class(p)
    
    @yielder
    def yield_client_file(self, p: OpenApiParser) -> Iterator[Tuple[int, str]]:
        # noinspection PyTypeChecker
        return self.dump_client_file(p)
    
    @overload
    def write_client_file(self, p: OpenApiParser) -> Iterator[str]:
        pass
    # noinspection PyOverloads
    @overload
    def write_client_file(self, p: OpenApiParser, *, file: StrIO) -> None:
        pass
    @writer
    def write_client_file(self, p: OpenApiParser) -> Optional[Iterator[str]]:
        # noinspection PyTypeChecker
        return self.yield_client_file(p)
    # endregion


__all__ = \
[
    'ClientWriter',
]
