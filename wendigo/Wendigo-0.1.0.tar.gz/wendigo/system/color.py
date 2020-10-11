from collections import namedtuple
from System import Action, Enum
from System.Drawing import Color as _Color

Color = namedtuple("Color", ("a", "r", "g", "b"))

class Colors(Enum):
    """
    Colors.
    """
    MediumPurple = _Color.MediumPurple
    MediumSeaGreen = _Color.MediumSeaGreen
    MediumSlateBlue = _Color.MediumSlateBlue
    MediumSpringGreen = _Color.MediumSpringGreen
    MediumTurquoise = _Color.MediumTurquoise
    MediumVioletRed = _Color.MediumVioletRed
    MidnightBlue = _Color.MidnightBlue
    MediumOrchid = _Color.MediumOrchid
    MintCream = _Color.MintCream
    Moccasin = _Color.Moccasin
    NavajoWhite = _Color.NavajoWhite
    Navy = _Color.Navy
    OldLace = _Color.OldLace
    Olive = _Color.Olive
    OliveDrab = _Color.OliveDrab
    Orange = _Color.Orange
    MistyRose = _Color.MistyRose
    OrangeRed = _Color.OrangeRed
    MediumBlue = _Color.MediumBlue
    Maroon = _Color.Maroon
    LightBlue = _Color.LightBlue
    LightCoral = _Color.LightCoral
    LightGoldenrodYellow = _Color.LightGoldenrodYellow
    LightGreen = _Color.LightGreen
    LightGray = _Color.LightGray
    LightPink = _Color.LightPink
    LightSalmon = _Color.LightSalmon
    MediumAquamarine = _Color.MediumAquamarine
    LightSeaGreen = _Color.LightSeaGreen
    LightSlateGray = _Color.LightSlateGray
    LightSteelBlue = _Color.LightSteelBlue
    LightYellow = _Color.LightYellow
    Lime = _Color.Lime
    LimeGreen = _Color.LimeGreen
    Linen = _Color.Linen
    Magenta = _Color.Magenta
    LightSkyBlue = _Color.LightSkyBlue
    LemonChiffon = _Color.LemonChiffon
    Orchid = _Color.Orchid
    PaleGreen = _Color.PaleGreen
    SlateBlue = _Color.SlateBlue
    SlateGray = _Color.SlateGray
    Snow = _Color.Snow
    SpringGreen = _Color.SpringGreen
    SteelBlue = _Color.SteelBlue
    Tan = _Color.Tan
    Teal = _Color.Teal
    SkyBlue = _Color.SkyBlue
    Thistle = _Color.Thistle
    Turquoise = _Color.Turquoise
    Violet = _Color.Violet
    Wheat = _Color.Wheat
    White = _Color.White
    WhiteSmoke = _Color.WhiteSmoke
    Yellow = _Color.Yellow
    YellowGreen = _Color.YellowGreen
    Tomato = _Color.Tomato
    PaleGoldenrod = _Color.PaleGoldenrod
    Silver = _Color.Silver
    SeaShell = _Color.SeaShell
    PaleTurquoise = _Color.PaleTurquoise
    PaleVioletRed = _Color.PaleVioletRed
    PapayaWhip = _Color.PapayaWhip
    PeachPuff = _Color.PeachPuff
    Peru = _Color.Peru
    Pink = _Color.Pink
    Plum = _Color.Plum
    Sienna = _Color.Sienna
    PowderBlue = _Color.PowderBlue
    Red = _Color.Red
    RosyBrown = _Color.RosyBrown
    RoyalBlue = _Color.RoyalBlue
    SaddleBrown = _Color.SaddleBrown
    Salmon = _Color.Salmon
    SandyBrown = _Color.SandyBrown
    SeaGreen = _Color.SeaGreen
    Purple = _Color.Purple
    LawnGreen = _Color.LawnGreen
    LightCyan = _Color.LightCyan
    Lavender = _Color.Lavender
    DarkKhaki = _Color.DarkKhaki
    DarkGreen = _Color.DarkGreen
    DarkGray = _Color.DarkGray
    DarkGoldenrod = _Color.DarkGoldenrod
    DarkCyan = _Color.DarkCyan
    DarkBlue = _Color.DarkBlue
    Cyan = _Color.Cyan
    Crimson = _Color.Crimson
    Cornsilk = _Color.Cornsilk
    LavenderBlush = _Color.LavenderBlush
    Coral = _Color.Coral
    Chocolate = _Color.Chocolate
    Chartreuse = _Color.Chartreuse
    DarkMagenta = _Color.DarkMagenta
    CadetBlue = _Color.CadetBlue
    Brown = _Color.Brown
    BlueViolet = _Color.BlueViolet
    Blue = _Color.Blue
    BlanchedAlmond = _Color.BlanchedAlmond
    Black = _Color.Black
    Bisque = _Color.Bisque
    Beige = _Color.Beige
    Azure = _Color.Azure
    Aquamarine = _Color.Aquamarine
    Aqua = _Color.Aqua
    AntiqueWhite = _Color.AntiqueWhite
    AliceBlue = _Color.AliceBlue
    Transparent = _Color.Transparent
    BurlyWood = _Color.BurlyWood
    DarkOliveGreen = _Color.DarkOliveGreen
    CornflowerBlue = _Color.CornflowerBlue
    DarkOrchid = _Color.DarkOrchid
    Khaki = _Color.Khaki
    Ivory = _Color.Ivory
    DarkOrange = _Color.DarkOrange
    Indigo = _Color.Indigo
    IndianRed = _Color.IndianRed
    HotPink = _Color.HotPink
    Honeydew = _Color.Honeydew
    GreenYellow = _Color.GreenYellow
    Green = _Color.Green
    Gray = _Color.Gray
    Goldenrod = _Color.Goldenrod
    GhostWhite = _Color.GhostWhite
    Gainsboro = _Color.Gainsboro
    Fuchsia = _Color.Fuchsia
    Gold = _Color.Gold
    FloralWhite = _Color.FloralWhite
    DarkRed = _Color.DarkRed
    DarkSalmon = _Color.DarkSalmon
    DarkSeaGreen = _Color.DarkSeaGreen
    ForestGreen = _Color.ForestGreen
    DarkSlateGray = _Color.DarkSlateGray
    DarkTurquoise = _Color.DarkTurquoise
    DarkSlateBlue = _Color.DarkSlateBlue
    DeepPink = _Color.DeepPink
    DeepSkyBlue = _Color.DeepSkyBlue
    DimGray = _Color.DimGray
    DodgerBlue = _Color.DodgerBlue
    Firebrick = _Color.Firebrick
    DarkViolet = _Color.DarkViolet

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int) -> _Color:
        """
        Get color by RGB.

        Parameters
        ----------
        r: R.
        g: G.
        b: B.

        Returns
        -------
        color: Color.
        """
        return _Color.FromArgb(r, g, b)

    @classmethod
    def from_argb(cls, a: int, r: int, g: int, b: int) -> _Color:
        """
        Get color by ARGB.

        Parameters
        ----------
        a: A.
        r: R.
        g: G.
        b: B.

        Returns
        -------
        color: Color.
        """
        return _Color.FromArgb(a, r, g, b)

    @classmethod
    def to_color(cls, color: _Color) -> Color:
        """
        Cast to Color.

        Returns
        -------
        color: Color.
        """
        return Color(color.A, color.R, color.G, color.B)