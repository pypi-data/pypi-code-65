import typer
import os.path as path
import os
import random
from collections import defaultdict
import csv
from rich import print as rp
from rich.console import Console
from rich.table import Column, Table
from castor.attributed_str import bold
import castor.attributed_str
from castor.jsoner import Jsoner
from binaryornot.check import is_binary

app = typer.Typer()
type_dict = dict()
type_dict[type(1)] = 'Int'
type_dict[type('hello')] = 'String'
type_dict[type(type_dict)] = 'Dict'
type_dict[type([1, 2, 3])] = 'Array'
type_dict[type(True)] = 'Bool'


# display_filename_prefix_middle = '├──'
# display_filename_prefix_last = '└──'
# display_parent_prefix_middle = '    '
# display_parent_prefix_last = '│   '


@app.command()
def json(filename: str,
         tree: bool = False,
         sample: bool = typer.Option(True, help="Sample Array when enable")):
    """
    JSON Visualizer
    """
    assert path.isfile(filename), f"{filename} is no a file"
    jsoner = Jsoner(filename=filename)
    if tree:
        jsoner.print_tree()
    else:
        jsoner.printer()


@app.command()
def text(filename: str,
         k: int = typer.Option(10, '-k'),
         output: int = typer.Option(-1, "--out", '-o')
         ):
    assert path.isfile(filename), \
        f"[ERROR] {filename} is not a file!"
    with open(filename, 'r') as fp:
        lines = fp.readlines()
        print(f"{filename} Total lines {len(lines)}")
        print('====================Sample=========================')
        indexes = random.choices([i for i in range(len(lines))], k=k)
        for i in indexes:
            line_text = bold(f"Line {i}")
            rp(f"{line_text}\t{lines[i]}")
        if output != -1:
            #  output
            indexes = random.choices([i for i in range(len(lines))], k=output)
            sample_file = f"{filename.split('.')[0]}-sample.txt"
            with open(sample_file, 'w') as sp:
                for line in indexes:
                    print(line, file=sp)
            rp(castor.attributed_str.clear(f"{sample_file} Created!"))


@app.command('csv')
def csv(filename: str = typer.Option(None, '--file', '-f'),
        k: int = typer.Option(3, '-k', help="Number of samples")
        ):
    # todo: length check
    assert path.isfile(filename), f"{filename} Not Exists!"
    table = Table(show_header=True, header_style="bold magenta")
    console = Console()
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        rows = [row for row in reader]
        if len(rows) != 0:
            # not empty
            header = rows[0]
            for h in header:
                table.add_column(h)
            samples = random.choices(rows[1:], k=k)
            for s in samples:
                table.add_row(*tuple(s))
        rp(castor.attributed_str.bcyan(f"{filename}: {len(rows) - 1} row(s)"))
        rp(castor.attributed_str.bcyan(f"Sample {k} items"))
        rp(castor.attributed_str.bred('=' * 25))
        console.print(table)
        rp(castor.attributed_str.bred('=' * 25))


@app.command('xls')
def excel(filename):
    rp(castor.attributed_str.bred("Will Implement in future version"))


@app.command('lock')
def locker(name: str = typer.Option("hash", '-n', '--name', help="Give lock name")):
    # lock current file
    def sha(filename):
        import hashlib
        _sha = hashlib.sha1()
        if is_binary(filename):
            f = open(filename, 'rb')
            _sha.update(f.read())
        else:
            with open(filename, 'r') as f:
                _sha.update(f.read().encode('utf-8'))
        return _sha.hexdigest()
    pwd = os.getcwd()
    result = dict()
    rp(f"Locking plain text file in {pwd}")
    file_list = os.listdir(pwd)
    for f in file_list:
        full_path = os.path.join(pwd, f)
        if path.isfile(full_path):
            hash_res = sha(full_path)
            result[f] = hash_res
    import toml
    lock_file = os.path.join(pwd, f'.{name}.lock')
    if os.path.exists(lock_file):
        old_result = toml.load(f=open(lock_file, 'r'))
        rp(castor.attributed_str.clear("Verifying file..."))
        diff = defaultdict(list)
        for k, v in result.items():
            if k in old_result.keys():
                if old_result[k] != result[k]:
                    diff['modified'].append(k)
            else:
                diff['new'].append(k)
        for k, v in old_result.items():
            if k not in result.keys():
                diff['deleted'].append(k)
        rp(castor.attributed_str.bred(f"{len(diff['deleted'])} files deleted"))
        for item in diff['deleted']:
            rp(castor.attributed_str.bred(f"----{item}"))
        rp(castor.attributed_str.byellow(f"{len(diff['modified'])} files modified"))
        for item in diff['modified']:
            rp(castor.attributed_str.byellow(f"-+-+{item}"))
        rp(castor.attributed_str.bred(f"{len(diff['new'])} files created"))
        for item in diff['new']:
            rp(castor.attributed_str.bgreen(f"++++{item}"))
        toml.dump(o=result, f=open(lock_file, 'w'))
        rp(f"{lock_file} updated")
    else:
        toml.dump(o=result, f=open(lock_file, 'w'))
        rp(f"{lock_file} created")
