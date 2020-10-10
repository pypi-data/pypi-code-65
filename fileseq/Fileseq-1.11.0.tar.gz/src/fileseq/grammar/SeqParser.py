# Generated from Seq.g4 by ANTLR 4.7.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys

def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\7")
        buf.write("\63\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\3")
        buf.write("\2\3\2\3\2\3\3\6\3\23\n\3\r\3\16\3\24\3\4\3\4\3\4\3\4")
        buf.write("\3\5\6\5\34\n\5\r\5\16\5\35\3\6\3\6\3\7\3\7\6\7$\n\7\r")
        buf.write("\7\16\7%\7\7(\n\7\f\7\16\7+\13\7\3\7\3\7\6\7/\n\7\r\7")
        buf.write("\16\7\60\3\7\2\2\b\2\4\6\b\n\f\2\2\2\61\2\16\3\2\2\2\4")
        buf.write("\22\3\2\2\2\6\26\3\2\2\2\b\33\3\2\2\2\n\37\3\2\2\2\f)")
        buf.write("\3\2\2\2\16\17\5\4\3\2\17\20\5\6\4\2\20\3\3\2\2\2\21\23")
        buf.write("\7\4\2\2\22\21\3\2\2\2\23\24\3\2\2\2\24\22\3\2\2\2\24")
        buf.write("\25\3\2\2\2\25\5\3\2\2\2\26\27\5\b\5\2\27\30\5\n\6\2\30")
        buf.write("\31\5\f\7\2\31\7\3\2\2\2\32\34\7\6\2\2\33\32\3\2\2\2\34")
        buf.write("\35\3\2\2\2\35\33\3\2\2\2\35\36\3\2\2\2\36\t\3\2\2\2\37")
        buf.write(" \7\5\2\2 \13\3\2\2\2!#\7\3\2\2\"$\7\6\2\2#\"\3\2\2\2")
        buf.write("$%\3\2\2\2%#\3\2\2\2%&\3\2\2\2&(\3\2\2\2\'!\3\2\2\2(+")
        buf.write("\3\2\2\2)\'\3\2\2\2)*\3\2\2\2*,\3\2\2\2+)\3\2\2\2,.\7")
        buf.write("\3\2\2-/\7\7\2\2.-\3\2\2\2/\60\3\2\2\2\60.\3\2\2\2\60")
        buf.write("\61\3\2\2\2\61\r\3\2\2\2\7\24\35%)\60")
        return buf.getvalue()


class SeqParser ( Parser ):

    grammarFileName = "Seq.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'.'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "DIRNAME", "FRANGE", "CHAR", 
                      "ALNUM" ]

    RULE_seq = 0
    RULE_dirname = 1
    RULE_basename = 2
    RULE_name = 3
    RULE_frange = 4
    RULE_ext = 5

    ruleNames =  [ "seq", "dirname", "basename", "name", "frange", "ext" ]

    EOF = Token.EOF
    T__0=1
    DIRNAME=2
    FRANGE=3
    CHAR=4
    ALNUM=5

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.7.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None



    class SeqContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def dirname(self):
            return self.getTypedRuleContext(SeqParser.DirnameContext,0)


        def basename(self):
            return self.getTypedRuleContext(SeqParser.BasenameContext,0)


        def getRuleIndex(self):
            return SeqParser.RULE_seq

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSeq" ):
                listener.enterSeq(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSeq" ):
                listener.exitSeq(self)




    def seq(self):

        localctx = SeqParser.SeqContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_seq)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 12
            self.dirname()
            self.state = 13
            self.basename()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DirnameContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DIRNAME(self, i:int=None):
            if i is None:
                return self.getTokens(SeqParser.DIRNAME)
            else:
                return self.getToken(SeqParser.DIRNAME, i)

        def getRuleIndex(self):
            return SeqParser.RULE_dirname

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDirname" ):
                listener.enterDirname(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDirname" ):
                listener.exitDirname(self)




    def dirname(self):

        localctx = SeqParser.DirnameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_dirname)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 16 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 15
                self.match(SeqParser.DIRNAME)
                self.state = 18 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==SeqParser.DIRNAME):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class BasenameContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def name(self):
            return self.getTypedRuleContext(SeqParser.NameContext,0)


        def frange(self):
            return self.getTypedRuleContext(SeqParser.FrangeContext,0)


        def ext(self):
            return self.getTypedRuleContext(SeqParser.ExtContext,0)


        def getRuleIndex(self):
            return SeqParser.RULE_basename

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBasename" ):
                listener.enterBasename(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBasename" ):
                listener.exitBasename(self)




    def basename(self):

        localctx = SeqParser.BasenameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_basename)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 20
            self.name()
            self.state = 21
            self.frange()
            self.state = 22
            self.ext()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class NameContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CHAR(self, i:int=None):
            if i is None:
                return self.getTokens(SeqParser.CHAR)
            else:
                return self.getToken(SeqParser.CHAR, i)

        def getRuleIndex(self):
            return SeqParser.RULE_name

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterName" ):
                listener.enterName(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitName" ):
                listener.exitName(self)




    def name(self):

        localctx = SeqParser.NameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_name)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 25 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 24
                self.match(SeqParser.CHAR)
                self.state = 27 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==SeqParser.CHAR):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class FrangeContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FRANGE(self):
            return self.getToken(SeqParser.FRANGE, 0)

        def getRuleIndex(self):
            return SeqParser.RULE_frange

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFrange" ):
                listener.enterFrange(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFrange" ):
                listener.exitFrange(self)




    def frange(self):

        localctx = SeqParser.FrangeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_frange)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 29
            self.match(SeqParser.FRANGE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ExtContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ALNUM(self, i:int=None):
            if i is None:
                return self.getTokens(SeqParser.ALNUM)
            else:
                return self.getToken(SeqParser.ALNUM, i)

        def CHAR(self, i:int=None):
            if i is None:
                return self.getTokens(SeqParser.CHAR)
            else:
                return self.getToken(SeqParser.CHAR, i)

        def getRuleIndex(self):
            return SeqParser.RULE_ext

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExt" ):
                listener.enterExt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExt" ):
                listener.exitExt(self)




    def ext(self):

        localctx = SeqParser.ExtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_ext)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 39
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,3,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 31
                    self.match(SeqParser.T__0)
                    self.state = 33 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    while True:
                        self.state = 32
                        self.match(SeqParser.CHAR)
                        self.state = 35 
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if not (_la==SeqParser.CHAR):
                            break
             
                self.state = 41
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

            self.state = 42
            self.match(SeqParser.T__0)
            self.state = 44 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 43
                self.match(SeqParser.ALNUM)
                self.state = 46 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==SeqParser.ALNUM):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





