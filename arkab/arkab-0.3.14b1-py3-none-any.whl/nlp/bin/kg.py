#! python
import typer as ty
from arkab.nlp import Knowledge
from rich import print as rp
from rich.console import Console
from rich.table import Column, Table
import castor.attributed_str as NSAttributedDict
import os

cli = ty.Typer()
sum_app = ty.Typer()

cli.add_typer(sum_app, name="summary")  # add multi command


@cli.command('index')
def index(filename: str = ty.Option(None, '--name', '-n'),
          reverse: bool = ty.Option(default=False, help="When reverse enable, using h|t|r pattern"),
          split: str = ty.Option(default='\t')):
    """
    index knowledge.txt
    """
    from arkab.utils import sha
    pwd = os.getcwd()
    # if filename
    name = filename.split('.')[0]
    knowledge = Knowledge(src=filename, separator=split)
    knowledge.build_graph_from_raw()
    knowledge.indexing()
    entities = knowledge.ent2idx
    ent_file = f'{name}-ent2idx.txt'
    rel_file = f'{name}-rel2idx.txt'
    kg_file = f'{name}-kg2idx.txt'
    lock = dict()
    with open(ent_file, 'w') as dest:
        for k, v in entities.items():
            print(f"{k}|{v}", file=dest)
        rp(NSAttributedDict.bgreen(f"{pwd}/{name}-ent2idx.txt created! Pattern is ent|index"))
    lock['ent2idx'] = sha(ent_file)
    with open(rel_file, 'w') as rel_dest:
        rels = knowledge.rel2idx
        for k, v in rels.items():
            print(f"{k}|{v}", file=rel_dest)
        rp(NSAttributedDict.bgreen(f"{pwd}/{name}-rel2idx.txt created with pattern  rel|index"))
    lock['rel2idx'] = sha(rel_file)
    with open(kg_file, 'w') as kg_dest:
        kg = knowledge.index_graph
        for head, tup_list in kg.items():
            # head : head
            # tup: rel, tail
            for tup in tup_list:
                rel, tail = tup
                if reverse:
                    print(f"{head}|{tail}|{rel}", file=kg_dest)
                else:
                    print(f"{head}|{rel}|{tail}", file=kg_dest)
        if reverse:
            # h|r|t
            rp(NSAttributedDict.bgreen(f"{pwd}/{name}-kg2idx.txt created with pattern  h|t|r"))
        else:
            rp(NSAttributedDict.bgreen(f"{pwd}/{name}-kg2idx.txt created with pattern  h|r|t"))
    lock['kg2idx'] = sha(kg_file)
    import toml
    with open('.index.lock', 'w') as il:
        toml.dump(lock, il)


@sum_app.command('all')
def _all(filename: str = ty.Option(None, '--file', '-f'),
         std: bool = ty.Option(True, '-s', help="Enable stdout."),
         split: str = ty.Option('\t', '--spl'),
         descend: bool = ty.Option(False, '--down', '-d'),
         _rel: bool = ty.Option(True, '-r', help="if set False, calc entity count"),
         reverse: bool = ty.Option(default=False, help="When reverse enable, using h|t|r pattern")
         ):
    """Summary all tuples by rel or entities"""
    assert os.path.exists(filename), f"[ERROR] {filename} not exist!"
    from collections import defaultdict
    result = defaultdict(int)
    console = Console()
    table = Table(show_header=True)
    if _rel:
        table.add_column("Relation", justify="right")
    else:
        table.add_column("Entity", justify='right')
    with open(filename) as fp:
        lines = fp.readlines()
        for line in lines:
            line = line.strip()  # remove \n
            if reverse:
                head, tail, rel = line.split(split)
            else:
                head, rel, tail = line.split(split)
            if _rel:
                result[rel] += 1
            else:
                result[head] += 1
                result[tail] += 1
    rp(NSAttributedDict.bcyan(f"Total {len(result)} items."))
    rp(NSAttributedDict.bgreen(f"{'>' * 30}START{'>' * 30}"))
    # sort dict
    result = {k: v for k, v in sorted(result.items(), key=lambda item: item[1], reverse=descend)}
    if std:
        for k, v in result.items():
            table.add_row(k, v)
        console.print(table)
        rp(NSAttributedDict.bgreen(f"{'<' * 30}START{'<' * 30}"))
    else:
        #  output to file
        if os.path.isabs(filename):
            rel_file, suffix = os.path.relpath(filename).split('.')  # remove suffix
            outfile = f"{rel_file}-summary.{suffix}"
            outfile = os.path.join(os.getcwd(), outfile)
            with open(outfile, 'w') as op:
                for k, v in result.items():
                    print(f"{k}\t{v}", file=op)
            rp(NSAttributedDict.bgreen(f"{outfile} created!"))


@sum_app.command('head')
def _head(): ...


@sum_app.command('tail')
def _tail(): ...
