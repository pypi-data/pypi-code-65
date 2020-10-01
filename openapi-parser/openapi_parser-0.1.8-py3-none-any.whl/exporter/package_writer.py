import os
import shutil
from tempfile import NamedTemporaryFile
from typing import *

from openapi_parser.parser import OpenApiParser
from openapi_parser.util.utils import StrIO
from .abstract_writer import Writer
from .client_writer import ClientWriter
from .model_writer import ModelWriter
from .pacakge_init_writer import PackageInitWriter
from .utils_writer import UtilsWriter

class PackageWriter(Writer):
    destination_dir: str
    
    def __init__(self, destination_dir: AnyStr):
        if (isinstance(destination_dir, bytes)):
            destination_dir = destination_dir.decode()
        self.destination_dir = os.path.abspath(destination_dir)
        super().__init__()
    
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def filename(self, path: AnyStr) -> str:
        if (isinstance(path, bytes)):
            path = path.decode()
        
        if (not os.path.isabs(path)):
            path = os.path.join(self.destination_dir, path)
        
        return path
    
    def sub_package(self, name: AnyStr) -> 'PackageWriter':
        return PackageWriter(self.filename(name))
    
    def open_file(self, path: AnyStr) -> StrIO:
        path = self.filename(path)
        dir = os.path.dirname(path)
        if (not os.path.isdir(dir)):
            os.makedirs(dir)
        
        return open(path, 'wt', encoding='utf8')
    
    def remove_package(self):
        shutil.rmtree(self.destination_dir, ignore_errors=True)

    def write_init(self, parser: OpenApiParser):
        with self.open_file('__init__.py') as output:
            writer = PackageInitWriter()
            writer.write_package_init_file(parser, file=output)
    def write_utils(self, parser: OpenApiParser):
        writer = UtilsWriter()
        self.smart_writer(lambda: writer.yield_utils_file(), 'utils', writer=writer)
    def write_model(self, parser: OpenApiParser):
        writer = ModelWriter()
        self.smart_writer(lambda: writer.yield_model_file(parser), 'model', writer=writer)
    def write_client(self, parser: OpenApiParser):
        writer = ClientWriter()
        self.smart_writer(lambda: writer.yield_client_file(parser), 'client', writer=writer)
    
    def smart_writer(self, lines_gen: Callable[[], Iterator[Tuple[int, str]]], module_name: str, *, max_lines: int = 5000, writer: Optional[Writer] = None):
        if (writer is None):
            writer = self

        line_num = 0
        with NamedTemporaryFile(mode='wt', newline=writer.NEWLINE, prefix=f'{module_name}-', suffix='.py', delete=False) as temp:
            for indent_level, line in lines_gen():
                writer.write_line(temp, writer.join_line(indent_level, line))
                line_num += 1
        
        if (line_num < 2 * max_lines):
            with self.open_file(f'{module_name}.py') as dest: pass
            shutil.move(temp.name, dest.name)
        else:
            os.remove(temp.name)
            self.partial_writer(lines_gen(), module_name, max_lines=max_lines, writer=writer)
    
    def partial_writer(self, lines: Iterator[Tuple[int, str]], module_name: str, *, max_lines: int = 5000, writer: Optional[Writer] = None):
        if (writer is None):
            writer = self
        
        with self.sub_package(module_name) as sub_package:
            line_num = 0
            part_num = 0
            file: Optional[StrIO] = None
            for indent_level, line in lines:
                if (file is None or indent_level == 0 and line == '' and line_num > max_lines):
                    if (file is not None):
                        file.close()
                    
                    file = sub_package.open_file(f'_{part_num + 1}.py')
                    if (part_num > 0):
                        writer.write_line(file, f'from ._{part_num} import *')
                    
                    part_num += 1
                    line_num = 0
                
                if (line.startswith('from .')):
                    line = 'from ..' + line[len('from .'):]
                
                writer.write_line(file, writer.join_line(indent_level, line))
                line_num += 1
            
            if (file is not None):
                file.close()
            
            with sub_package.open_file('__init__.py') as file:
                writer.write_line(file, f'from ._{part_num} import *')
                writer.write_line(file, f'from ._{part_num} import __all__')
    
    def write_package(self, parser: OpenApiParser, *, clean: bool = False):
        if (clean):
            self.remove_package()
        
        self.write_init(parser)
        self.write_utils(parser)
        self.write_model(parser)
        self.write_client(parser)


__all__ = \
[
    'PackageWriter',
]
