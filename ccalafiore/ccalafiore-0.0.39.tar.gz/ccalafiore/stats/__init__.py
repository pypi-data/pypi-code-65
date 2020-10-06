# import os

__name__ = 'ccalafiore.stats'
__all__ = ['descriptive', 'paired_t_test', 'unpaired_t_test']
# __all__ = []
# cwd = os.path.dirname(__file__)
# format_modules = '.py'
# len_format_modules = len(format_modules)
# for m in os.listdir(cwd):
#     directory_m = os.path.join(cwd, m)
#     if os.path.isfile(directory_m) and m.endswith(format_modules) and (m != '__init__.py'):
#         __all__.append(m[:-len_format_modules])
#     elif os.path.isdir(directory_m) and os.path.isfile(os.path.join(directory_m, '__init__.py')):
#         __all__.append(m)

for m in __all__:
    __import__('.'.join([__name__, m]))
del m

# del cwd, m, directory_m, format_modules, len_format_modules, os
