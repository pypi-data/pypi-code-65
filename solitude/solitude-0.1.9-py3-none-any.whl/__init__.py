import pluggy

__author__ = "Sil van de Leemput"
__email__ = "sil.vandeleemput@radboudumc.nl"
__version__ = "0.1.9"

TOOL_AUTHOR = "DIAG"
TOOL_NAME = "solitude"
hookimpl = pluggy.HookimplMarker(TOOL_NAME)
