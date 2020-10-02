#  Copyright (c) 2020  SBA - MIT License
import os.path
import re
import argparse
import sys
from fnmatch import translate


def build_pro(root, translations, src, frm):
    name = os.path.basename(os.path.abspath(root))
    src_re = re.compile('|'.join(translate(i) for i in src)
                        ) if src is not None else None
    frm_re = re.compile('|'.join(translate(i) for i in frm)
                        ) if frm is not None else None
    srcs, frms = [], []
    for dirpath, _dirnames, filenames in os.walk(root):
        for file in filenames:
            if src is not None and src_re.match(file):
                srcs.append(os.path.join(dirpath, file))
            elif frm is not None and frm_re.match(file):
                frms.append(os.path.join(dirpath, file))
    with open(f'{name}.pro', 'w') as pro:
        sep = '\\\n' + ' ' * 15
        if len(srcs) > 0:
            pro.write('SOURCES      = ' + sep.join(srcs) + '\n\n')
        if len(frms) > 0:
            pro.write('FORMS        = ' + sep.join(frms) + '\n\n')
        if len(translations) > 0:
            pro.write('TRANSLATIONS = ' + sep.join(
                f'{name}_{i}.ts' for i in translations))


def parse(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('root')
    parser.add_argument('translations', nargs='+')
    parser.add_argument('--src', '-s', action='append', default=['*.py'])
    parser.add_argument('--frm', '-f', action='append', default=['*.ui'])
    params = parser.parse_args(args)
    return params


def run(args):
    params = vars(parse(args))
    build_pro(**params)


if __name__ == '__main__':
    run(sys.argv[1:])
