import json, os, sys, datetime
from io import StringIO
from pygments import highlight, lexers, formatters

class Utils:
    
    @staticmethod
    def encodeString(str):
        bytes        = str.encode("utf-8")
        base64_bytes =  base64.b64encode(bytes)
        return base64_bytes.decode("utf-8")

    @staticmethod
    def decodeString(str):
        bytes        = str.encode("utf-8")
        base64_bytes =  base64.b64decode(bytes)
        return base64_bytes.decode("utf-8")

    @staticmethod
    def stringToJSON(str):
        return json.loads(str)

    @staticmethod
    def dictToJSON(dictObj):
        strObj = StringIO()
        json.dump(dictObj, strObj, default=str, indent=4, sort_keys=True)
        return strObj.getvalue()

    @staticmethod
    def printJSON(jsonObject):
        colorful_json = highlight(jsonObject, lexers.JsonLexer(), formatters.TerminalFormatter())
        print(colorful_json)

    @staticmethod
    def alignRight(length,vlr):
        return vlr + " ".ljust(length-len(vlr)," ")    

    @staticmethod
    def removeCharsColors(text):
        if isinstance(text, str):
           text = text.replace(Colors.UNDERLINE,"") \
                      .replace(Colors.RESET,"") \
                      .replace(Colors.BLACK,"") \
                      .replace(Colors.RED,"") \
                      .replace(Colors.GREEN,"") \
                      .replace(Colors.YELLOW,"") \
                      .replace(Colors.BLUE,"") \
                      .replace(Colors.MAGENTA,"") \
                      .replace(Colors.CYAN,"") \
                      .replace(Colors.WHITE,"") \
                      .replace(Colors.BBLACK,"") \
                      .replace(Colors.BRED,"") \
                      .replace(Colors.BGREEN,"") \
                      .replace(Colors.BYELLOW,"") \
                      .replace(Colors.BBLUE,"") \
                      .replace(Colors.BMAGENTA,"") \
                      .replace(Colors.BCYAN,"") \
                      .replace(Colors.BWHITE,"") \
                      .replace(Colors.BG_BLACK,"") \
                      .replace(Colors.BG_RED,"") \
                      .replace(Colors.BG_GREEN,"") \
                      .replace(Colors.BG_YELLOW,"") \
                      .replace(Colors.BG_BLUE,"") \
                      .replace(Colors.BG_PURPLE,"") \
                      .replace(Colors.BG_CYAN,"") \
                      .replace(Colors.BG_WHITE,"") \
                      .replace(Colors.IBLACK,"") \
                      .replace(Colors.IRED,"") \
                      .replace(Colors.IGREEN,"") \
                      .replace(Colors.IYELLOW,"") \
                      .replace(Colors.IBLUE,"") \
                      .replace(Colors.IMAGENTA,"") \
                      .replace(Colors.ICYAN,"") \
                      .replace(Colors.IWWHITE,"") \
                      .replace(Colors.BIBLACK,"") \
                      .replace(Colors.BIRED,"") \
                      .replace(Colors.BIGREEN,"") \
                      .replace(Colors.BIYELLOW,"") \
                      .replace(Colors.BIBLUE,"") \
                      .replace(Colors.BIPURPLE,"") \
                      .replace(Colors.BICYAN,"") \
                      .replace(Colors.BIWHITE,"") \
                      .replace(Colors.On_IBLACK,"") \
                      .replace(Colors.On_IRED,"") \
                      .replace(Colors.On_IGREEN,"") \
                      .replace(Colors.On_IYELLOW,"") \
                      .replace(Colors.On_IBLUE,"") \
                      .replace(Colors.On_IPURPLE,"") \
                      .replace(Colors.On_ICYAN,"") \
                      .replace(Colors.On_IWHITE,"")
        return text    


class Colors:
    
    UNDERLINE = '\033[4m'
    RESET     = '\033[0m'

    # Regular Colors
    BLACK     = '\033[0;30m'
    RED       = '\033[0;31m'
    GREEN     = '\033[0;32m'
    YELLOW    = '\033[0;33m'
    BLUE      = '\033[0;34m'
    MAGENTA   = '\033[0;35m'
    CYAN      = '\033[0;36m'
    WHITE     = '\033[0;37m'

    # Bold
    BBLACK    ="\033[1;30m"
    BRED      ="\033[1;31m"
    BGREEN    ="\033[1;32m"
    BYELLOW   ="\033[1;33m"
    BBLUE     ="\033[1;34m"
    BMAGENTA  ="\033[1;35m"
    BCYAN     ="\033[1;36m"
    BWHITE    ="\033[1;37m"

    # Background Colors
    BG_BLACK  = '\033[40m'
    BG_RED    = '\033[41m'
    BG_GREEN  = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE   = '\033[44m'
    BG_PURPLE = '\033[45m'
    BG_CYAN   = '\033[46m'
    BG_WHITE  = '\033[47m'

    # High Intensty
    IBLACK    ="\033[0;90m"
    IRED      ="\033[0;91m"
    IGREEN    ="\033[0;92m"
    IYELLOW   ="\033[0;93m"
    IBLUE     ="\033[0;94m"
    IMAGENTA  ="\033[0;95m"
    ICYAN     ="\033[0;96m"
    IWWHITE   ="\033[0;97m"

    # Bold High Intensty
    BIBLACK   ="\033[1;90m"
    BIRED     ="\033[1;91m"
    BIGREEN   ="\033[1;92m"
    BIYELLOW  ="\033[1;93m"
    BIBLUE    ="\033[1;94m"
    BIPURPLE  ="\033[1;95m"
    BICYAN    ="\033[1;96m"
    BIWHITE   ="\033[1;97m"

    # High Intensty backgrounds
    On_IBLACK ="\033[0;100m"
    On_IRED   ="\033[0;101m"
    On_IGREEN ="\033[0;102m"
    On_IYELLOW="\033[0;103m"
    On_IBLUE  ="\033[0;104m"
    On_IPURPLE="\033[0;105m"
    On_ICYAN  ="\033[0;106m"
    On_IWHITE ="\033[0;107m"

class Emoticons:

    _PROMPT      = ['⛅','⛅']
    _WAITING     = ['💤💤💤','☕☕☕']
    _SEE_YA      = ['👋','✌']
    _ERROR       = ['❌💣','❌☠']
    _TOOL        = ['🔧','⚒']
    _THUMBS_UP   = ['👍','✔']
    _POINT_RIGHT = ['👉','❖']
    _WINK        = ['😉','☻']
    _OPS         = ['😕','☹']
    _PIN         = ['📌','✎']
    _ENV         = ['📝','✍']
    _TIME        = ['🕘','☕']
    _WAIT_DISTR  = ['🍺','♨']
    _WAIT_DISTR2 = ['🍼','⚾']
    _MAGNIFIER   = ['🔍','☌']
    _BLOCKS      = ['📦','❒']
    _REDMARK     = ['🔴','⚫']
    _UPLOAD      = ['📤','✈']
    _UPLOAD_PART = ['🔹','➩']
    _FOLDER      = ['🔹','➩']
    _OK          = ['✅','✅']
    _IMGS        = [
                     ['🕒','🕓','🕔','🕕','🕖','🕗','🕘','🕙','🕚','🕛','🕐','🕑'],
                     ['☰','☱','☲','☴','☵','☶','☷','☶','☴']
                   ]

    @staticmethod
    def isWindows():
        return 1 if os.name == "nt" else 0
    
    @staticmethod
    def prompt():
        return Emoticons._PROMPT[Emoticons.isWindows()]
    @staticmethod
    def waiting():
        return Emoticons._WAITING[Emoticons.isWindows()]    
    @staticmethod
    def seeYa():
        return Emoticons._SEE_YA[Emoticons.isWindows()]
    @staticmethod
    def error():
        return Emoticons._ERROR[Emoticons.isWindows()]
    @staticmethod
    def tool():
        return Emoticons._TOOL[Emoticons.isWindows()]
    @staticmethod
    def thumbsUp():
        return Emoticons._THUMBS_UP[Emoticons.isWindows()] 
    @staticmethod
    def pointRight():
        return Emoticons._POINT_RIGHT[Emoticons.isWindows()]
    @staticmethod
    def wink():
        return Emoticons._WINK[Emoticons.isWindows()]
    @staticmethod
    def pin():
        return Emoticons._PIN[Emoticons.isWindows()]
    @staticmethod
    def env():
        return Emoticons._ENV[Emoticons.isWindows()]
    @staticmethod
    def time():
        return Emoticons._TIME[Emoticons.isWindows()]
    @staticmethod
    def waitDistract():
        return Emoticons._WAIT_DISTR[Emoticons.isWindows()]
    @staticmethod
    def waitDistract2():
        return Emoticons._WAIT_DISTR2[Emoticons.isWindows()]
    @staticmethod
    def ops():
        return Emoticons._OPS[Emoticons.isWindows()]
    @staticmethod
    def magnifier():
        return Emoticons._MAGNIFIER[Emoticons.isWindows()]
    @staticmethod
    def ok():
        return Emoticons._OK[Emoticons.isWindows()]    
    @staticmethod
    def redMark():
        return Emoticons._REDMARK[Emoticons.isWindows()]
    @staticmethod
    def blocks():
        return Emoticons._BLOCKS[Emoticons.isWindows()]        


