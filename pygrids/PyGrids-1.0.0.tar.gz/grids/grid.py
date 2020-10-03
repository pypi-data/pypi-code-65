import numpy
import datetime
import pickle
import os

from .errors import LogTypeError, FormatGridError

NULL = '∅'
LOG_EVENT_TYPES = [
    'UPDATE_CELL',
    'GET_CELL',
    'GRID_VIEW',
    'LOG_VIEW'
]

def gen(iterable):
    for i in iterable:
        yield i


class GridLog:
    def __init__(self, grid):
        self.grid = grid
        self.created_at = datetime.datetime.now()
        self._data = "# GridLog created at [{}]:\n".format(self.created_at)

    def __str__(self):
        return self.read()

    def log(self, event, *args):
        if event not in LOG_EVENT_TYPES:
            raise LogTypeError(event)
        self._data += '-> [{}] ({}) at [{}]\n'.format(event, ', '.join(args),datetime.datetime.now())

    def read(self):
        self.log('LOG_VIEW')
        return self._data
    
    def readlines(self):
        lines = self._data.split('\n')
        while '' in lines:
            lines.remove('')
        return lines


def construct_grid_template_line(x):
    cell_line = ' '.join(['%s'] * x)
    return cell_line


class Grid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self._data = numpy.array(
            [[None] * self.width] * self.height
        )

        self.log = GridLog(self)
    
    def __str__(self):
        return self.view()
    
    def __repr__(self):
        return '<Grid {}x{} created at {}>'.format(self.width, self.height, repr(str(self.log.created_at)))

    def view(self, text_align='left'):
        format_line = construct_grid_template_line(self.width)
        lines = [format_line % tuple(y) for y in self.format_cells(text_align)]
        return '\n'.join(lines)

    def format_cells(self, text_align='left'):
        str_cells = [[str(repr(x)) if x is not None else NULL for x in y] for y in self._data]

        longest_cell_len = 0
        for y in str_cells:
            for x in y:
                if len(x) > longest_cell_len:
                    longest_cell_len = len(x)
        if longest_cell_len % 2:
            longest_cell_len += 1
        
        if text_align == 'left':
            for y in str_cells:
                line = []
                for x in y:
                    line.append(x + ' ' * (longest_cell_len - len(x)))
                yield gen(line)
        elif text_align == 'right':
            for y in str_cells:
                line = []
                for x in y:
                    line.append(' ' * (longest_cell_len - len(x)) + x)
                yield gen(line)
        elif text_align == 'center':
            for y in str_cells:
                line = []
                for x in y:
                    line.append(' ' * ((longest_cell_len - len(x))/2) + x + ' ' * ((longest_cell_len - len(x))/2))
                yield gen(line)
        else:
            raise FormatGridError("{} isn't an acceptable text alignement. Only left, right, or center are allowed.".format(text_align))

    def collapsed_cells(self):
        return list(self._data)

    def update_cell(self, x, y, new_value):
        self.log.log('UPDATE_CELL', str(x), str(y), repr(new_value))
        self._data[y - 1][x - 1] = new_value
    
    def get_cell(self, x, y):
        self.log.log('GET_CELL', str(x), str(y))
        cell = self._data[y - 1][x - 1]
        return cell if cell is not None else NULL
    
    def x_by_y(self):
        self.log.log('GRID_VIEW', 'x_by_y')
        for x in zip(*self._data):
            yield gen(x)
    
    def y_by_x(self):
        self.log.log('GRID_VIEW', 'y_by_x')
        for y in self._data:
            yield gen(y)
    
    def save(self, filename='grid1.dat'):
        def non_conflicting_file(file):
            if os.path.exists(file):
                new_file, ext = file.split('.')
                new_file = int(''.join([char for char in file if char.isdecimal()])) + 1
                return non_conflicting_file('.'.join([new_file, ext]))
            else:
                return file
        
        name = non_conflicting_file(filename)
        with open(name, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)