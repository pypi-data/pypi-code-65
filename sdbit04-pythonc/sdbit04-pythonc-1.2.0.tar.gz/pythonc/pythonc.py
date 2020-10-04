from py_compile import compile
from argparse import ArgumentParser
import os
import sys
import shutil

def compile_module(input_module):
    module_dir = os.path.abspath(os.path.dirname(input_module))
    compiled_dir_temp = os.path.join(module_dir, "__pycache__")
    if os.path.isdir(compiled_dir_temp):
        shutil.rmtree(compiled_dir_temp)
    try:
        compile(input_module)
    except Exception:
        print("Exception occured")
    else:
        compiled_file_name = os.listdir(compiled_dir_temp)[0]
        compiled_file_temp = os.path.join(compiled_dir_temp, compiled_file_name)
        compiled_file_path = os.path.join(module_dir, compiled_file_name)
        if os.path.isfile(compiled_file_path):
            os.remove(compiled_file_path)
            shutil.move(compiled_file_temp, compiled_file_path)
            shutil.rmtree(compiled_dir_temp)
        else:
            shutil.move(compiled_file_temp, compiled_file_path)
            shutil.rmtree(compiled_dir_temp)

def main_method():
    parser = ArgumentParser(usage="Please provide the module name want to compile")
    parser.add_argument("input_module")
    args = parser.parse_args()
    input_module = args.input_module
    compile_module(input_module)

if __name__ == "__main__":
    main_method()
    
