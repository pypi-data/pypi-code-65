#!/usr/bin/env python3

import sys
from antlr4 import CommonTokenStream, InputStream
from SeqLexer import SeqLexer
from SeqParser import SeqParser


def main(argv):
    input = InputStream(argv[1])
    lexer = SeqLexer(input)
    stream = CommonTokenStream(lexer)
    parser = SeqParser(stream)
    parser.setTrace('-d' in sys.argv)
    tree = parser.seq()
    print(tree.toStringTree(recog=parser))


if __name__ == '__main__':
    main(sys.argv)
