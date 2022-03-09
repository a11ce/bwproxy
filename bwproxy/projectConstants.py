from collections import defaultdict
from typing import (
    Any,
    DefaultDict,
    Generic,
    Optional,
    TypeVar,
    Dict,
    Tuple,
    List,
    Union,
    overload,
)
from typing_extensions import Self

VERSION = "v2.1"
# 0x23F is the paintbrush symbol
CREDITS = chr(0x23F) + " https://a11ce.com/bwproxy"

# Helper classes and functions

T = TypeVar("T")


class Map(Dict[str, T], Generic[T]):
    """
    Map is a dictionary that can be manipulated using dot notation instead of bracket notation.
    Just like a dictionary, it raises a KeyError if it cannot retrieve a property.
    """

    def __init__(self, *args: Dict[str, Any], **kwargs: Any):
        self.update(*args, **kwargs)

    def __getattr__(self, attr: str):
        return self[attr]

    def __setattr__(self, key: str, value: Any):
        self.__setitem__(key, value)

    def __setitem__(self, key: str, value: Any):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item: str):
        self.__delitem__(item)

    def __delitem__(self, key: str):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


class XY(Tuple[int, int]):
    """
    XY is a two int tuple that can be added to other tuples, subtracted,
    and scaled by a constant factor.
    Being a tuple subclass, should be able to be used wherever a tuple is needed,
    but Image.paste is not happy with that.
    Call XY.tuple() in that case.
    """

    @overload
    def __new__(cls, x: int, y: int) -> Self:
        pass

    @overload
    def __new__(cls, x: Tuple[int, int], y: None = None) -> Self:
        pass

    def __new__(
        cls, x: Union[int, Tuple[int, int]] = (0, 0), y: Optional[int] = None
    ) -> Self:
        if isinstance(x, int):
            assert isinstance(y, int)
            return super().__new__(cls, (x, y))
        else:
            return super().__new__(cls, x)

    def __add__(self, other: Tuple[int, int]) -> Self:
        return XY(self[0] + other[0], self[1] + other[1])

    def __sub__(self, other: Tuple[int, int]) -> Self:
        return XY(self[0] - other[0], self[1] - other[1])

    def scale(self, factor: Union[int, float]) -> Self:
        return XY(int(self[0] * factor), int(self[1] * factor))

    def tuple(self) -> Tuple[int, int]:
        return tuple(self)

    def transpose(self) -> Self:
        return XY(self[1], self[0])


Box = Tuple[XY, XY]
Layout = Map[Map[int]]

# File locations

# Cards and Tokens/Emblems have different caches, since there are cards with the same name as tokens
# Notable example: Blood token and Flesh // Blood
CACHE_LOC = "cardcache/cardcache.p"
TOKEN_CACHE_LOC = "cardcache/tokencache.p"
BACK_CARD_SYMBOLS_LOC = "symbols"

SERIF_FONT = "fonts/matrixb.ttf"
MONOSPACE_FONT = "fonts/MPLANTIN.ttf"

# MTG constants: colors, basic lands, color names...

MTG_COLORS = str  # Literal["W", "U", "B", "R", "G"]

FRAME_COLORS = {
    "W": "#fcf4a3",
    "U": "#127db4",
    "B": "#692473",
    "R": "#e13c32",
    "G": "#0f7846",
    "C": "#919799",
    "M": "#d4af37",  # Multicolor / Gold
    "default": "#000000",
}

BASIC_LANDS_NONSNOW = ["Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"]
BASIC_LANDS = BASIC_LANDS_NONSNOW + [
    f"Snow-Covered {l}" for l in BASIC_LANDS_NONSNOW if l != "Wastes"
]

MANA_SYMBOLS: List[MTG_COLORS] = ["W", "U", "B", "R", "G"]
# Can be obtained programmatically, but that's more concise
HYBRID_SYMBOLS = ["W/U", "U/B", "B/R", "R/G", "G/W", "W/B", "U/R", "B/G", "R/W", "G/U"]
COLOR_NAMES = {"W": "white", "U": "blue", "B": "black", "R": "red", "G": "green"}

# Layout types
STD = "standard"
SPLIT = "split"
FUSE = "fuse"
AFTER = "aftermath"
ADV = "adventure"
FLIP = "flip"
LAND = "land"
TOKEN = "token"
EMBLEM = "emblem"
TDFC = "transform"
MDFC = "modal_dfc"

DFC_LAYOUTS = [TDFC, MDFC]
TWO_PARTS_LAYOUTS = [SPLIT, FUSE, AFTER, ADV, FLIP]

# FONT_CODE_POINT includes the symbols used in the card text and mana cost.
# Those were added manually to the font file at the specified unicode point
FONT_CODE_POINT: Dict[str, str] = {}
for i in range(21):
    FONT_CODE_POINT[f"{{{i}}}"] = chr(0x200 + i)  # Generic mana cost (0 to 20)
for (i, c) in enumerate(MANA_SYMBOLS):
    FONT_CODE_POINT[f"{{{c}}}"] = chr(0x220 + i)  # Colored Mana
    FONT_CODE_POINT[f"{{2/{c}}}"] = chr(0x225 + i)  # Two-Hybrid Mana
    FONT_CODE_POINT[f"{{{c}/P}}"] = chr(0x22A + i)  # Phyrexian Mana
for (i, h) in enumerate(HYBRID_SYMBOLS):
    FONT_CODE_POINT[f"{{{h}}}"] = chr(0x230 + i)  # Hybrid Mana
    FONT_CODE_POINT[f"{{{h}/P}}"] = chr(0x240 + i)  # Hybrid Phyrexian Mana
FONT_CODE_POINT["{X}"] = chr(0x215)
FONT_CODE_POINT["{Y}"] = chr(0x216)
FONT_CODE_POINT["{Z}"] = chr(0x217)
FONT_CODE_POINT["{T}"] = chr(0x218)  # Tap
FONT_CODE_POINT["{Q}"] = chr(0x219)  # Untap
FONT_CODE_POINT["{S}"] = chr(0x21E)  # Snow Mana
FONT_CODE_POINT["{C}"] = chr(0x21F)  # Colorless Mana
FONT_CODE_POINT["{P}"] = chr(0x22F)  # Standard Phyrexian Mana
FONT_CODE_POINT["{E}"] = chr(0x23A)  # Energy Counter
FONT_CODE_POINT[f"{{{MDFC}_FRONT}}"] = chr(0x21A)
FONT_CODE_POINT[f"{{{MDFC}_BACK}}"] = chr(0x21B)
FONT_CODE_POINT[f"{{{TDFC}_FRONT}}"] = chr(0x21C)
FONT_CODE_POINT[f"{{{TDFC}_BACK}}"] = chr(0x21D)
FONT_CODE_POINT[f"{{{FLIP}_FRONT}}"] = chr(0x218)  # Tap
FONT_CODE_POINT[f"{{{FLIP}_BACK}}"] = chr(0x219)  # Untap
FONT_CODE_POINT["{PAINTBRUSH}"] = chr(0x23F)  # Paintbrush Symbol

TODO = """
Class, Sagas and Leveler frames?
Flip as dfc, aftermath as split (with flag)
Colored Mana symbols
Flavor Names for DFC, Adventures and possibly Flip?
Stop changing fonts
COMMENTS
"""

# Info relative to card pagination, mainly card and element sizes

# A MtG card is 2.5 in x 3.5 in
# Standard resolution is 300 dpi
# A4 paper is 8.25 in x 11.75 in
# Letter paper is 8.5 in x 11 in
# We can have a 3x3 of cards in both A4 and letter
# If we resize a MtG card to 1.875 in x 2.625 in (x0.75)
# We can have a 4x4 of cards in both A4 and letter

PageFormat = str  # Literal["a4paper", "letter"]

A4_FORMAT: PageFormat = "a4paper"
LETTER_FORMAT: PageFormat = "letter"
PAGE_FORMAT: List[PageFormat] = ["a4paper", "letter"]

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DPI = 300
A4_PAPER = XY(int(8.25 * DPI), int(11.75 * DPI))
LETTER_PAPER = XY(int(8.5 * DPI), int(11 * DPI))
CARD_H = int(2.5 * DPI)
CARD_V = int(3.5 * DPI)
CARD_SIZE = XY(CARD_H, CARD_V)
CARD_BOX: Box = (XY(0, 0), CARD_SIZE)
SMALL_CARD_SIZE = CARD_SIZE.scale(factor=0.75)
# Distance between cards when paginated, in pixels
CARD_DISTANCE = 20
# Desired distance in pixels between elements inside the card, e.g. between card border and title
BORDER = 15

TITLE_FONT_SIZE = 70
TYPE_FONT_SIZE = 50
TEXT_FONT_SIZE = 40
OTHER_FONT_SIZE = 25
SET_ICON_SIZE = 40
ILLUSTRATION_SIZE = 600

# PTL box (stands for Power/Toughness/Loyalty) is always the same dimension
# And its lower right vertex is always the same distance from the card lower right vertex
PTL_BOX_DIM = XY(175, 70)
PTL_BOX_MARGIN = XY(25, 5)

# Info about the card layout (how the lines are positioned to make the frame and various card sections)
# Every layout has a NAME_LAYOUT Map[Map[int]] with info about
# - the upper borders (BORDER) for different card sections (title, illustration, type line, rules box, other)
# - the size for different card sections
# - the vertical middle anchor for one-line text (title, type line)
# There also is the position of the set icon, and the position of the PTL box

# Helper functions for layout


def calcLayoutData(
    layoutType: str,
    bottom: int = CARD_V,
    left: int = 0,
    right: int = CARD_H,
    rulesBoxSize: int = 0,
):
    """
    Defines the layouts for all card types.
    Layouts start with TITLE at 0, then it has
    TITLE, ILLUSTRATION, TYPE_LINE, RULES_BOX and OTHER.
    The illustration size is deduced from the card vertical size
    (which depends on the layout type, for split it's the horizontal dim)
    All the borders are calculated using the sizes
    Almost all the sizes stay the same across layouts,
    except for rules box size and illustration.
    The text aligment is calculated using box size, only for PTL
    - Adventure frames are weird because they don't start at 0
    and don't have the OTHER line (also illustration is 0)
    - Flip frames have the illustration at the bottom,
    between the two halves of the card
    - Fuse cards have another section (the fuse box),
    which is specified at the end.
    """
    layout = Map[Map[int]](
        BORDER=Map[int](TITLE=0, BOTTOM=bottom, LEFT=left, RIGHT=right),
        SIZE=Map[int](
            TITLE=90,
            TYPE_LINE=50,
            RULES_BOX=rulesBoxSize,
            OTHER=40,
            PTL_BOX_H=PTL_BOX_DIM[0],
            PTL_BOX_V=PTL_BOX_DIM[1],
        ),
        FONT_MIDDLE=Map[int](),
    )

    if layoutType == ADV:
        layout.BORDER.TITLE = STD_LAYOUT.BORDER.RULES_BOX
        layout.SIZE.RULES_BOX = (
            STD_LAYOUT.SIZE.RULES_BOX - layout.SIZE.TITLE - layout.SIZE.TYPE_LINE
        )
        layout.BORDER.BOTTOM = layout.BORDER.BOTTOM - layout.SIZE.OTHER
        layout.SIZE.OTHER = 0

    if layoutType == FLIP:
        layout.BORDER.TYPE_LINE = layout.BORDER.TITLE + layout.SIZE.TITLE
        layout.BORDER.RULES_BOX = layout.BORDER.TYPE_LINE + layout.SIZE.TYPE_LINE
        layout.BORDER.OTHER = layout.BORDER.RULES_BOX + layout.SIZE.RULES_BOX
        layout.BORDER.ILLUSTRATION = layout.BORDER.OTHER + layout.SIZE.OTHER

        layout.SIZE.ILLUSTRATION = layout.BORDER.BOTTOM - 2 * layout.BORDER.ILLUSTRATION

        layout.BORDER.PTL_BOX_BOTTOM = layout.BORDER.ILLUSTRATION - PTL_BOX_MARGIN[1]

    else:
        layout.BORDER.ILLUSTRATION = layout.BORDER.TITLE + layout.SIZE.TITLE
        layout.BORDER.OTHER = layout.BORDER.BOTTOM - layout.SIZE.OTHER
        layout.BORDER.RULES_BOX = layout.BORDER.OTHER - layout.SIZE.RULES_BOX
        layout.BORDER.TYPE_LINE = layout.BORDER.RULES_BOX - layout.SIZE.TYPE_LINE

        layout.SIZE.ILLUSTRATION = layout.BORDER.TYPE_LINE - layout.BORDER.ILLUSTRATION

        layout.BORDER.PTL_BOX_BOTTOM = layout.BORDER.BOTTOM - PTL_BOX_MARGIN[1]

    layout.BORDER.PTL_BOX_RIGHT = layout.BORDER.RIGHT - PTL_BOX_MARGIN[0]
    layout.BORDER.PTL_BOX_LEFT = layout.BORDER.PTL_BOX_RIGHT - layout.SIZE.PTL_BOX_H
    layout.BORDER.PTL_BOX_TOP = layout.BORDER.PTL_BOX_BOTTOM - layout.SIZE.PTL_BOX_V

    layout.SIZE.H = layout.BORDER.RIGHT - layout.BORDER.LEFT
    layout.SIZE.V = layout.BORDER.BOTTOM - layout.BORDER.TITLE

    layout.FONT_MIDDLE.PTL_H = layout.BORDER.PTL_BOX_LEFT + layout.SIZE.PTL_BOX_H // 2
    layout.FONT_MIDDLE.PTL_V = layout.BORDER.PTL_BOX_TOP + layout.SIZE.PTL_BOX_V // 2

    if layoutType == SPLIT:
        layout.SIZE.FUSE = 50
        layout.BORDER.FUSE = layout.BORDER.OTHER - layout.SIZE.FUSE
        layout.SIZE.RULES_BOX_FUSE = layout.SIZE.RULES_BOX - layout.SIZE.FUSE
        layout.FONT_MIDDLE.FUSE = layout.BORDER.FUSE + layout.SIZE.FUSE // 2

    return layout


def calcIconPosition(layout: Layout) -> XY:
    """
    Returns the set icon position, given the layout and the right border of the card
    """
    return XY(
        layout.BORDER.RIGHT - BORDER - SET_ICON_SIZE,
        layout.BORDER.TYPE_LINE + (layout.SIZE.TYPE_LINE - SET_ICON_SIZE) // 2,
    )


def calcIllustrationPosition(layout: Layout) -> XY:
    """
    Returns the illustration position for basic lands and emblems
    """
    return XY(
        (layout.BORDER.RIGHT - ILLUSTRATION_SIZE) // 2,
        layout.BORDER.ILLUSTRATION
        + (layout.SIZE.ILLUSTRATION - ILLUSTRATION_SIZE) // 2,
    )


def ptlTextPosition(box: Box) -> XY:
    return (box[0] + box[1]).scale(0.5)


# Standard layout (normal cards)
STD_LAYOUT = calcLayoutData(layoutType=STD, rulesBoxSize=500)
STD_SET_ICON_POSITION = calcIconPosition(layout=STD_LAYOUT)


# Split layout (for split, fuse, and right half of aftermath)
SPLIT_LAYOUT_LEFT = calcLayoutData(
    layoutType=SPLIT, bottom=CARD_H, left=0, right=CARD_V // 2, rulesBoxSize=360
)
SPLIT_LAYOUT_RIGHT = calcLayoutData(
    layoutType=SPLIT, bottom=CARD_H, left=CARD_V // 2, right=CARD_V, rulesBoxSize=360
)
SPLIT_SET_ICON_POSITION: Tuple[XY, XY] = (
    calcIconPosition(layout=SPLIT_LAYOUT_LEFT),
    calcIconPosition(layout=SPLIT_LAYOUT_RIGHT),
)


# Adventure layout (for the Adventure part of the card, the other one uses the standard layout)
ADVENTURE_LAYOUT = calcLayoutData(
    layoutType=ADV,
    bottom=CARD_V,
    left=0,
    right=CARD_H // 2,
)


# Aftermath layout (for the upper half of aftermath)
AFTERMATH_LAYOUT = calcLayoutData(
    layoutType=AFTER,
    bottom=CARD_V // 2,
    rulesBoxSize=175,
)
AFTERMATH_SET_ICON_POSITION = calcIconPosition(layout=AFTERMATH_LAYOUT)


# Flip layout (Only one half is specified here, for the other just flip the card and redraw)
FLIP_LAYOUT = calcLayoutData(
    layoutType=FLIP,
    rulesBoxSize=200,
)
FLIP_SET_ICON_POSITION = calcIconPosition(layout=FLIP_LAYOUT)


# Textless land layout
LAND_LAYOUT = calcLayoutData(layoutType=LAND, rulesBoxSize=0)
LAND_SET_ICON_POSITION = calcIconPosition(layout=LAND_LAYOUT)
LAND_MANA_SYMBOL_POSITION = calcIllustrationPosition(layout=LAND_LAYOUT)


# Vanilla token layout (has one line for color indicator)
TOKEN_LAYOUT = calcLayoutData(layoutType=TOKEN, rulesBoxSize=100)
TOKEN_SET_ICON_POSITION = calcIconPosition(layout=TOKEN_LAYOUT)
TOKEN_ARC_WIDTH = 600


# Emblem and normal token layout (has more rules space)
EMBLEM_LAYOUT = calcLayoutData(layoutType=EMBLEM, rulesBoxSize=250)
EMBLEM_SET_ICON_POSITION = calcIconPosition(layout=EMBLEM_LAYOUT)
EMBLEM_SYMBOL_POSITION = calcIllustrationPosition(layout=EMBLEM_LAYOUT)

LAYOUTS: DefaultDict[str, List[Layout]] = defaultdict(
    lambda: [STD_LAYOUT],
    {
        SPLIT: [SPLIT_LAYOUT_LEFT, SPLIT_LAYOUT_RIGHT],
        FUSE: [SPLIT_LAYOUT_LEFT, SPLIT_LAYOUT_RIGHT],
        AFTER: [AFTERMATH_LAYOUT, SPLIT_LAYOUT_RIGHT],
        FLIP: [FLIP_LAYOUT, FLIP_LAYOUT],
        ADV: [STD_LAYOUT, ADVENTURE_LAYOUT],
        LAND: [LAND_LAYOUT],
        TOKEN: [TOKEN_LAYOUT],
        EMBLEM: [EMBLEM_LAYOUT],
    },
)
