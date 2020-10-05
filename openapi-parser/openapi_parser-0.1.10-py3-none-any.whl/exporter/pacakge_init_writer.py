from typing import *

from openapi_parser.parser import OpenApiParser
from openapi_parser.util.utils import StrIO
from .abstract_writer import Writer, yielder, writer
from .header_writer import HeaderWriter

class PackageInitWriter(HeaderWriter, Writer):
    
    @property
    def submodules(self) -> Iterator[str]:
        yield 'client'
    
    @property
    def from_imports(self) -> Iterator[str]:
        for m in self.submodules:
            yield f'.{m}.*'
    
    def dump_package_init(self, parser: OpenApiParser) -> Iterator[str]:
        yield '__all__ = [ ]'
        yield '__pdoc__ = { }'
        yield '__pdoc_extras__ = [ ]'
        yield
        
        yield '_submodules = \\'
        yield '['
        with self.indent():
            for m in self.submodules:
                yield f'{m},'
        yield ']'
        yield
        
        yield "for _submodule in _submodules:"
        with self.indent():
            yield "_submodule_name = _submodule.__name__.partition(f'{__name__}.')[-1]"
            yield "__all__.extend(_submodule.__all__)"
            yield "__pdoc__[_submodule_name] = True"
            yield "_submodule.__pdoc__ = getattr(_submodule, '__pdoc__', dict())"
            yield "_extras = getattr(_submodule, '__pdoc_extras__', list())"
            yield "for _element in _submodule.__all__:"
            with self.indent():
                yield "__pdoc__[_element] = _element in _extras"
        yield
    
    def dump_package_init_file(self, parser: OpenApiParser) -> Iterator[str]:
        yield from self.dump_headers()
        yield from self.dump_package_init(parser)
    
    # region Writers
    @yielder
    def yield_package_init(self, parser: OpenApiParser) -> Iterator[Tuple[int, str]]:
        # noinspection PyTypeChecker
        return self.dump_package_init(parser)
    
    @overload
    def write_package_init(self, parser: OpenApiParser) -> Iterator[str]:
        pass
    # noinspection PyOverloads
    @overload
    def write_package_init(self, parser: OpenApiParser, *, file: StrIO) -> None:
        pass
    @writer
    
    def write_package_init_file(self, parser: OpenApiParser) -> Optional[Iterator[str]]:
        # noinspection PyTypeChecker
        return self.yield_package_init_file(parser)
    @yielder
    def yield_package_init_file(self, parser: OpenApiParser) -> Iterator[Tuple[int, str]]:
        # noinspection PyTypeChecker
        return self.dump_package_init_file(parser)
    
    @overload
    def write_package_init_file(self, parser: OpenApiParser) -> Iterator[str]:
        pass
    # noinspection PyOverloads
    @overload
    def write_package_init_file(self, parser: OpenApiParser, *, file: StrIO) -> None:
        pass
    @writer
    def write_package_init_file(self, parser: OpenApiParser) -> Optional[Iterator[str]]:
        # noinspection PyTypeChecker
        return self.yield_package_init_file(parser)
    # endregion
    