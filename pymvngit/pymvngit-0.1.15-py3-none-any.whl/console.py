from pymvngit.utils import Utils,Emoticons,Colors
import os, sys

LINE_LENGTH = 150

class Console:

    @staticmethod
    def _separator():
        print(Colors.RESET + "+" + Colors.GREEN + "-".ljust(LINE_LENGTH,"-") + Colors.RESET + "+")
    
    @staticmethod
    def warning(msg):
        print("")
        print(" ",Emoticons.ops(),msg)
        print("")

    @staticmethod
    def error(msg,spaceBelow=True):
        print("")
        print(" ",Emoticons.error(),msg)
        if spaceBelow:
           print("")

    @staticmethod
    def message(msg):
        print("  ",Colors.GREEN + msg + Colors.RESET)

    @staticmethod
    def title(msg,top=True,bottom=True):
        if top: Console._separator()
        print(" ",Emoticons.pin(),msg)
        if bottom: Console._separator()

    @staticmethod
    def title2(msg,top=True,bottom=True):
        if top: Console._separator()
        print(" ",Emoticons.blocks(),msg)
        if bottom: Console._separator()    

    @staticmethod
    def line(msg,top=True,bottom=True):
        if top: Console._separator()
        print(" ",msg)
        if bottom: Console._separator()    

    @staticmethod
    def printTable(header,prettyTable, tableArgs):
        Console.title(header)
        print(prettyTable.printMe(False, tableArgs))

    @staticmethod
    def printTable2(header,prettyTable,tableArgs):
        print(header)
        print(prettyTable.printMe(False, tableArgs))    

    @staticmethod
    def clear():
        if os.name == "nt":
           os.system('cls')
        else:   
           os.system('clear')

    @staticmethod
    def printLine(line,Arrow=True):
        arrow = Colors.IBLUE + "---> " if Arrow else ""
        print("  "  + arrow + Colors.GREEN + line)  
    
    @staticmethod
    def printHeaderCommand(command):
        #print(Colors.GREEN)
        print(Colors.RESET + "+" + Colors.GREEN + "-".ljust(LINE_LENGTH,"-") + Colors.RESET + "+" + Colors.GREEN)
        print("  " + Emoticons.pin() + "  " + Colors.GREEN + command + Colors.RESET)
        print(Colors.RESET + "+" + Colors.GREEN + "-".ljust(LINE_LENGTH,"-") + Colors.RESET + "+" + Colors.RESET)

    @staticmethod
    def printFooter():
        Console._separator()
        print("")
    
    @staticmethod
    def addOkMsg(length,msg):
        lenDiff = length - len(Utils.removeCharsColors(msg))
        return msg + ".".ljust(lenDiff,".") + ".Ok!" + Emoticons.ok()

    @staticmethod
    def addWaitMsg(length,msg):
        lenDiff = (length-2) - len(Utils.removeCharsColors(msg))
        return msg + ".".ljust(lenDiff,".") + ".Wait!" + Emoticons.waiting()

    @staticmethod
    def addKoMsg(length,msg):
        lenDiff = length - len(Utils.removeCharsColors(msg))
        return msg + ".".ljust(lenDiff," ") + ".KO!" + Emoticons.error()
    
    @staticmethod
    def addToMsg(length,msg,texto):
        lenDiff = length - len(Utils.removeCharsColors(msg))
        return msg + ".".ljust(lenDiff,".") + "." + texto

