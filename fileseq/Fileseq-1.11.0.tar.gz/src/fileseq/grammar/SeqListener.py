# Generated from Seq.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .SeqParser import SeqParser
else:
    from SeqParser import SeqParser

# This class defines a complete listener for a parse tree produced by SeqParser.
class SeqListener(ParseTreeListener):

    # Enter a parse tree produced by SeqParser#seq.
    def enterSeq(self, ctx:SeqParser.SeqContext):
        pass

    # Exit a parse tree produced by SeqParser#seq.
    def exitSeq(self, ctx:SeqParser.SeqContext):
        pass


    # Enter a parse tree produced by SeqParser#dirname.
    def enterDirname(self, ctx:SeqParser.DirnameContext):
        pass

    # Exit a parse tree produced by SeqParser#dirname.
    def exitDirname(self, ctx:SeqParser.DirnameContext):
        pass


    # Enter a parse tree produced by SeqParser#basename.
    def enterBasename(self, ctx:SeqParser.BasenameContext):
        pass

    # Exit a parse tree produced by SeqParser#basename.
    def exitBasename(self, ctx:SeqParser.BasenameContext):
        pass


    # Enter a parse tree produced by SeqParser#name.
    def enterName(self, ctx:SeqParser.NameContext):
        pass

    # Exit a parse tree produced by SeqParser#name.
    def exitName(self, ctx:SeqParser.NameContext):
        pass


    # Enter a parse tree produced by SeqParser#frange.
    def enterFrange(self, ctx:SeqParser.FrangeContext):
        pass

    # Exit a parse tree produced by SeqParser#frange.
    def exitFrange(self, ctx:SeqParser.FrangeContext):
        pass


    # Enter a parse tree produced by SeqParser#ext.
    def enterExt(self, ctx:SeqParser.ExtContext):
        pass

    # Exit a parse tree produced by SeqParser#ext.
    def exitExt(self, ctx:SeqParser.ExtContext):
        pass


