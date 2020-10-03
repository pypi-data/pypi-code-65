import dataclasses
import datetime
import logging
import urllib.parse
from typing import *

import http_server_base
import http_server_base.model
import http_server_base.tools
import tornado.httpclient

import openapi_parser.exporter.exporting_features.client
from openapi_parser.model import ModelPath
from openapi_parser.parser import OpenApiParser
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
            '.utils.FilteringJsonEncoder',
            '.utils.filter_out_smart',
        ]
        
        yield from self.objects_to_from_imports(imports)
        yield from other_imports
    
    def dump_client_class(self, parser: OpenApiParser) -> Iterator[str]:
        client_name = 'MyClient'
        logger_name = 'my-client'
        self.export(client_name)
        
        yield '@dataclass'
        yield f"class {client_name}(SubrequestClient):"
        with self.indent():
            yield "server: str"
            yield f"logger_name: str = field(init=False, repr=False, default=__name__ if (__name__ != '__main__') else {logger_name!r})"
            yield "model_encoder: Type[IEncoder] = field(init=False, repr=False, default=FilteringJsonEncoder)"
            yield
            
            yield from self.dump_class_methods(openapi_parser.exporter.exporting_features.client)
            
            for path, mdl in parser.loaded_objects.items():
                if (isinstance(mdl, ModelPath)):
                    for http_method, e in mdl.endpoints.items():
                        yield from self.dump_endpoint(e, endpoint_path=mdl.endpoint_path, http_method=http_method, method_type=MethodType.RegularMethod, asynchronous=True)
    
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
