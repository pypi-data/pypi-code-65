"""
parse output data from cascade/sequin.mfs
"""

import lark

import logging
logger = logging.getLogger(__name__)

from . import lark_common

grammar = '''\
seqx_start: seqx_focuson seqx_replacement seqx_individual_seq
seqx_focuson: _seqx_focuson_invalid | seqx_focuson_valid
_seqx_focuson_invalid: "No focuson events were found" _NL
seqx_focuson_valid: _seqx_focuson1 _seqx_focuson2
_seqx_focuson1:\
    "The Final States of 'Focuson' Sequences" _NL\
    "Atoms Escaping from the Target Surfaces          Adatoms Trapped at Target Surfaces     Replace-      Close" _NL\
    "Front        Back         Side         Other        Front        Back         Other        ments        Pairs" _NL\
    pint (_S pint)~8 _NL
_seqx_focuson2:\
    "Linked to     Proper      Improper      Inter-       Forcibly    Cut Off in   Truncated" _NL\
    "Other Layer    Pairs        Pairs        stitial     Terminated     SINGLE     Sequences      'Lost'" _NL\
    pint (_S pint)~7 _NL
seqx_replacement: _seqx_replacement_invalid | seqx_replacement_valid
_seqx_replacement_invalid: "No replacement events were found" _NL
seqx_replacement_valid: _seqx_replacement1 _seqx_replacement2 seqx_replacement3
_seqx_replacement1:\
    "The Final States of Replacement Sequences" _NL\
    "Atoms Escaping from the Target Surfaces          Adatoms Trapped at Target Surfaces     Atoms in     Inter-" _NL\
    "Front        Back         Side         Other        Front        Back         Other       Focusons     rupted" _NL\
    pint (_S pint)~8 _NL
_seqx_replacement2:\
    "Large      Linked to     Proper      Improper      Inter-       Forcibly    Cut Off in   Truncated" _NL\
    "Angle     Other Layer    Pairs        Pairs        stitial     Terminated     SINGLE     Sequences      'Lost'" _NL\
    pint (_S pint)~8 _NL

seqx_replacement3:\
    "Analysis of Replacement Sequences" _NL "Straightness Control Parameter" _S pfloat _NL\
    _seqx_replacement3_head\
    seqx_replacement3_maximum\
    _seqx_replacement3_head?\
    seqx_replacement3_data+

_seqx_replacement3_head:\
    "Summary of All Sequences" _NL\
    "Length        Mean          Variance        Skewness        Kurtosis        Std Dev          Error" _NL
seqx_replacement3_maximum: "Maximum" (_S pfloat)~6 _NL
seqx_replacement3_data: pint (_S pfloat)~6 _NL

seqx_individual_seq:\
    "All sequence directions are in external coordinates" _NL\
    ("Equivalent directions combined where possible" _NL)?\
    ("Indeterminate directions are labelled < 0, 0, 0 >" _NL)?\
    seqx_individual_seq_index\
    _seqx_individual_seq_head\
    seqx_individual_seq_maximum\
    seqx_individual_seq_data+
    
seqx_individual_seq_vector: "<" _S pint ":" (_S pint)~3 ">"
seqx_individual_seq_index: "Sequence:" (_S seqx_individual_seq_vector)+ _NL
_seqx_individual_seq_head: "Length" (_S "Mean" _S "Std Dev")+ _NL
seqx_individual_seq_maximum: "Maximum" (_S pfloat _S pfloat)+ _NL
seqx_individual_seq_data: pint (_S pfloat _S pfloat)+ _NL
'''

grammer_join_list = [grammar, lark_common.grammar, lark_common.grammar_elem]

grammar = '\n'.join(grammer_join_list)

class Context():
    def __init__(self):
        self.mobj = {}

class Transformer(lark.Transformer):
    def __init__(self, context):
        super().__init__()
        self.context = context

    def int(self, args):
        return int(args[0])

    def float(self, args):
        return float(args[0])

    def seqx_focuson_valid(self, args):
        return {
                'Atoms Escaping from the Target Surfaces':{
                    'Front':args[0], 'Back':args[1], 'Side':args[2], 'Other':args[3]},
                'Addatoms Trapped at Target Surfaces':{
                    'Front':args[4], 'Back':args[5], 'Other':args[6]},
                'Replacements':args[7],
                'Close Pairs':args[8],
                'Linked to Other Layer':args[9],
                'Proper Pairs':args[10],
                'Improper Pairs':args[11],
                'Interstitial':args[12],
                'Forcibly Terminated':args[13],
                'Cut Off in SINGLE':args[14],
                'Truncated Sequences':args[15],
                'Lost':args[16]}

    def seqx_focuson(self, args):
        self.context.mobj['The Final States of \'Focuson\' Sequences'] = args[0]

    def seqx_replacement_valid(self, args):
        return {
                'Atoms Escaping from the Target Surfaces':{
                    'Front':args[0], 'Back':args[1], 'Side':args[2], 'Other':args[3]},
                'Addatoms Trapped at Target Surfaces':{
                    'Front':args[4], 'Back':args[5], 'Other':args[6]},
                'Atoms in Focusons':args[7],
                'Interrupted':args[8],
                'Large Angle':args[9],
                'Linked to Other Layer':args[10],
                'Proper Pairs':args[11],
                'Improper Pairs':args[12],
                'Interstitial':args[13],
                'Forcibly Terminated':args[14],
                'Cut Off in SINGLE':args[15],
                'Truncated Sequences':args[16],
                'Lost':args[17],
                'Analysis of Replacement Seqences':args[18]}

    def seqx_replacement3(self, args):
        return {
                'Straightness Control Parameter':args[0],
                'data':args[1:]
                }

    def seqx_replacement3_maximum(self, args):
        return {
                'Index': 'Maximum',
                'Mean': args[0],
                'Variance': args[1],
                'Skewness': args[2],
                'Kurtosis': args[3],
                'Std Dev': args[4],
                'Error': args[5],
                }

    def seqx_replacement3_data(self, args):
        return {
                'Index': args[0],
                'Mean': args[1],
                'Variance': args[2],
                'Skewness': args[3],
                'Kurtosis': args[4],
                'Std Dev': args[5],
                'Error': args[6],
                }

    def seqx_replacement(self, args):
        self.context.mobj['The Final States of Replacement Sequences'] = args[0]


    def seqx_individual_seq_vector(self, args):
        return {'Index': args[0],
                'Vector': args[1:4]}

    def seqx_individual_seq_index(self, args):
        '''"Sequence:" (_S seqx_individual_seq_vector)+ _NL'''
        return args

    def seqx_individual_seq_maximum(self, args):
        data = [{'Mean':a, 'Std Dev': b} for a, b in zip(args[0::2], args[1::2])]
        return { 'Index': 'Maximum', 'data':data}

    def seqx_individual_seq_data(self, args):
        data = [{'Mean':a, 'Std Dev': b} for a, b in zip(args[1::2], args[2::2])]
        return { 'Index': args[0], 'data':data}

    def seqx_individual_seq(self, args):
        self.context.mobj['Individual Sequence Statistics'] = {
                'Vector Indicies': args[0],
                'data': args[1:]}


class Parser():
    def __init__(self, context, debug=False):
        self.transformer = Transformer(context)
        self.parser = lark.Lark(grammar=grammar, parser='lalr',
                transformer=self.transformer,
                start='seqx_start',
                debug=debug)

    def parse(self, text):
        return self.parser.parse(text)


def parse(text, debug=False):
    '''parse input text and returns context object'''
    c = Context()
    parser = Parser(c, debug)
    parser.parse(text)
    return c.mobj



if __name__ == '__main__':
    import sys
    import argparse
    import io

    import pprint

    import logging

    logging.basicConfig(level=logging.INFO)

    argparser = argparse.ArgumentParser()

    argparser.add_argument('input', type=argparse.FileType('rt'),
                        default=sys.stdin, nargs='?', help='input file')
    argparser.add_argument('output', type=argparse.FileType('wt'),
                        default=sys.stdout, nargs='?', help='output file')

    args = argparser.parse_args()


    context = Context()
    # prepare lark parser
    parser = Parser(context)

    # $EOF can be embedded for debugging
    buf = io.StringIO()
    for line in args.input:
        if line.startswith('$EOF'):
            buf.write('$EOF')
            break
        buf.write(line)

    # apply parsing
    result = parser.parse(buf.getvalue())

    # show lark object
    print(result.pretty())

    # show context
    pprint.pprint(context.mobj, compact=True, width=120)
