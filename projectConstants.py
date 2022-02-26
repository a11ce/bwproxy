from typing import Literal, Any, Generic, TypeVar

VERSION = "2.0"
CREDITS = chr(0x23F) + " https://a11ce.com/bwproxy"

T = TypeVar("T")


class Map(dict[str, T], Generic[T]):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """

    def __init__(self, *args: dict[str, Any], **kwargs: Any):
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


XY = tuple[int, int]
Box = tuple[XY, XY]

CACHE_LOC = "cardcache/cardcache.p"

MTG_COLORS = Literal["W", "U", "B", "R", "G"]

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

BASIC_LANDS = ["Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"]

MANA_SYMBOLS = ["W", "U", "B", "R", "G"]
# Can be obtained programmatically, but that's more concise
HYBRID_SYMBOLS = ["W/U", "U/B", "B/R", "R/G", "G/W", "W/B", "U/R", "B/G", "R/W", "G/U"]
COLOR_NAMES = {"W": "white", "U": "blue", "B": "black", "R": "red", "G": "green"}

FONT_CODE_POINT: dict[str, str] = {}
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
FONT_CODE_POINT["{MDFC_FRONT}"] = chr(0x21A)
FONT_CODE_POINT["{MDFC_BACK}"] = chr(0x21B)
FONT_CODE_POINT["{TDFC_FRONT}"] = chr(0x21C)
FONT_CODE_POINT["{TDFC_BACK}"] = chr(0x21D)
FONT_CODE_POINT["{PAINTBRUSH}"] = chr(0x23F)  # Paintbrush Symbol

DFC_LAYOUTS = ["transform", "modal_dfc"]
# fuse and aftermath aren't "real" layouts, but I introduce them in the Card wrapper
# SPLIT_LAYOUTS = ["flip", "split", "fuse", "aftermath", "adventure"]

TODO = """
Split / Fuse / Flip / Adventure frames (Maybe also Class, Sagas and Leveler?) ❌
Better Double-Faced card handler (front/back face symbols, add both to the file) ✅
Better search functionality:
* searching "Likeness of the Seeker" results in "Azusa's Many Journeys" ✅
* seaching "Alive" results in "Buried Alive" (should be "Alive // Well") ✅
* searching "Endbringer" results in "Shauku, Endbringer" ✅
Replace magic numbers (750, 1050...) with constants ❌
Add options for A4 and letter paper ✅
Better mana symbols, both in cost and in text ✅
(should be in the new font file, only problem is Tamiyo, Compleated Sage) ✅
Color indicator in text ✅
Tested searching for Failure // Comply via api, Failure is the first result

Move to Scryfall API ✅
"""


# A MtG card is 2.5 in x 3.5 in
# Standard resolution is 300 dpi
# A4 paper is 8.25 in x 11.75 in
# Letter paper is 8.5 in x 11 in
# We can have a 3x3 of cards in both A4 and letter
# If we resize a MtG card to 2 in x 2.8 in (x0.8)
# We can have a 4x4 in A4 and 5x3 in letter (horizontal)

PageFormat = Literal["a4paper", "letter"]

A4_FORMAT: PageFormat = "a4paper"
LETTER_FORMAT: PageFormat = "letter"
PAGE_FORMAT: list[PageFormat] = ["a4paper", "letter"]

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DPI = 300
A4_PAPER: XY = (int(8.25 * DPI), int(11.75 * DPI))
LETTER_PAPER: XY = (int(8.5 * DPI), int(11 * DPI))
CARD_H = int(2.5 * DPI)
CARD_V = int(3.5 * DPI)
CARD_SIZE: XY = (CARD_H, CARD_V)
CARD_SIZE_H: XY = (CARD_V, CARD_H)
SMALL_CARD_SIZE: XY = (int(CARD_H * 0.75), int(CARD_V * 0.75))
CARD_DISTANCE = 20
BORDER = 15

TITLE_FONT_SIZE = 70
TYPE_FONT_SIZE = 50
TEXT_FONT_SIZE = 40
OTHER_FONT_SIZE = 25
SYMBOL_SIZE = 40

PTL_BOX_DIM: XY = (125, 70)
PTL_BOX_MARGIN: XY = (25, 5)

STD_LAYOUT = Map[Map[int]](
    {
        "BORDER": Map[int](
            {
                "TITLE": 0,
                "TYPE_LINE": 460,
            }
        ),
        "SIZE": Map[int](
            {
                "TITLE": 90,
                "TYPE_LINE": 50,
                "OTHER": 40
            }
        ),
        "FONT_MIDDLE": Map[int](),
    }
)
STD_LAYOUT.BORDER.ILLUSTRATION = STD_LAYOUT.BORDER.TITLE + STD_LAYOUT.SIZE.TITLE
STD_LAYOUT.BORDER.RULES_BOX = STD_LAYOUT.BORDER.TYPE_LINE + STD_LAYOUT.SIZE.TYPE_LINE
STD_LAYOUT.BORDER.OTHER = CARD_V - STD_LAYOUT.SIZE.OTHER
STD_LAYOUT.SIZE.RULES_BOX = STD_LAYOUT.BORDER.OTHER - STD_LAYOUT.BORDER.RULES_BOX
STD_LAYOUT.FONT_MIDDLE.TITLE = (
    STD_LAYOUT.BORDER.TITLE + STD_LAYOUT.SIZE.TITLE // 2 - BORDER // 2
)
STD_LAYOUT.FONT_MIDDLE.TYPE_LINE = (
    STD_LAYOUT.BORDER.TYPE_LINE + STD_LAYOUT.SIZE.TYPE_LINE // 2 - BORDER // 2
)

STD_SYMBOL_POSITION: XY = (
    CARD_H - BORDER - SYMBOL_SIZE,
    STD_LAYOUT.BORDER.TYPE_LINE + (STD_LAYOUT.SIZE.TYPE_LINE - SYMBOL_SIZE) // 2,
)
STD_PTL_BOX: Box = (
    (CARD_H - PTL_BOX_DIM[0] - PTL_BOX_MARGIN[0], CARD_V - PTL_BOX_DIM[1] - PTL_BOX_MARGIN[1]),
    (CARD_H - PTL_BOX_MARGIN[0], CARD_V - PTL_BOX_MARGIN[1])
)


def ptlTextPosition(box: Box) -> XY:
    return ((box[0][0] + box[1][0]) // 2, (box[0][1] + box[1][1]) // 2)


SPLIT_LAYOUT = Map[Map[int]](
    {
        "BORDER": Map[int](
            {
                "TITLE": 0,
                "TYPE_LINE": 300,
            }
        ),
        "SIZE": Map[int](
            {
                "TITLE": STD_LAYOUT.SIZE.TITLE,
                "TYPE_LINE": STD_LAYOUT.SIZE.TYPE_LINE,
                "FUSE": 50,
                "OTHER": STD_LAYOUT.SIZE.OTHER,
            }
        ),
        "FONT_MIDDLE": Map[int]()
    }
)
SPLIT_LAYOUT.BORDER.ILLUSTRATION = SPLIT_LAYOUT.BORDER.TITLE + SPLIT_LAYOUT.SIZE.TITLE
SPLIT_LAYOUT.BORDER.RULES_BOX = SPLIT_LAYOUT.BORDER.TYPE_LINE + SPLIT_LAYOUT.SIZE.TYPE_LINE
SPLIT_LAYOUT.BORDER.OTHER = CARD_H - SPLIT_LAYOUT.SIZE.OTHER
SPLIT_LAYOUT.BORDER.FUSE = SPLIT_LAYOUT.BORDER.OTHER - SPLIT_LAYOUT.SIZE.FUSE
SPLIT_LAYOUT.SIZE.RULES_BOX = SPLIT_LAYOUT.BORDER.OTHER - SPLIT_LAYOUT.BORDER.RULES_BOX
SPLIT_LAYOUT.SIZE.RULES_BOX_FUSE = SPLIT_LAYOUT.BORDER.FUSE - SPLIT_LAYOUT.BORDER.RULES_BOX
SPLIT_LAYOUT.FONT_MIDDLE.TITLE = (
    SPLIT_LAYOUT.BORDER.TITLE + SPLIT_LAYOUT.SIZE.TITLE // 2 - BORDER // 2
)
SPLIT_LAYOUT.FONT_MIDDLE.TYPE_LINE = (
    SPLIT_LAYOUT.BORDER.TYPE_LINE + SPLIT_LAYOUT.SIZE.TYPE_LINE // 2 - BORDER // 2
)
SPLIT_LAYOUT.FONT_MIDDLE.FUSE = SPLIT_LAYOUT.BORDER.FUSE + SPLIT_LAYOUT.SIZE.FUSE // 2

SPLIT_SYMBOL_POSITION: tuple[XY, XY] = tuple(
    (
        s - BORDER - SYMBOL_SIZE,
        SPLIT_LAYOUT.BORDER.TYPE_LINE
        + (SPLIT_LAYOUT.SIZE.TYPE_LINE - SYMBOL_SIZE) // 2,
    )
    for s in [CARD_V // 2, CARD_V]
)

ADVENTURE_LAYOUT = Map[Map[int]](
    {
        "BORDER": Map[int](
            {
                "TITLE": STD_LAYOUT.BORDER.RULES_BOX,
                "TYPE_LINE": STD_LAYOUT.BORDER.RULES_BOX + STD_LAYOUT.SIZE.TITLE,
                "RULES_BOX": (
                    STD_LAYOUT.BORDER.RULES_BOX
                    + STD_LAYOUT.SIZE.TITLE
                    + STD_LAYOUT.SIZE.TYPE_LINE
                ),
            }
        ),
        "SIZE": Map[int](
            {
                "TITLE": STD_LAYOUT.SIZE.TITLE,
                "TYPE_LINE": STD_LAYOUT.SIZE.TYPE_LINE,
                "RULES_BOX": STD_LAYOUT.SIZE.RULES_BOX
                - STD_LAYOUT.SIZE.TITLE
                - STD_LAYOUT.SIZE.TYPE_LINE,
            }
        ),
    }
)
ADVENTURE_LAYOUT.FONT_MIDDLE = Map[int](
    {
        "TITLE": ADVENTURE_LAYOUT.BORDER.TITLE
        + ADVENTURE_LAYOUT.SIZE.TITLE // 2
        - BORDER // 2,
        "TYPE_LINE": ADVENTURE_LAYOUT.BORDER.TYPE_LINE
        + ADVENTURE_LAYOUT.SIZE.TYPE_LINE // 2
        - BORDER // 2,
    }
)

AFTERMATH_LAYOUT = Map[Map[int]](
    {
        "BORDER": Map[int](
            {
                "TITLE": 0,
                "TYPE_LINE": 260,
            }
        ),
        "SIZE": Map[int](
            {
                "TITLE": STD_LAYOUT.SIZE.TITLE,
                "TYPE_LINE": STD_LAYOUT.SIZE.TYPE_LINE,
                "OTHER": STD_LAYOUT.SIZE.OTHER,
            }
        ),
        "FONT_MIDDLE": Map[int](),
    }
)
AFTERMATH_LAYOUT.BORDER.ILLUSTRATION = (
    AFTERMATH_LAYOUT.BORDER.TITLE + AFTERMATH_LAYOUT.SIZE.TITLE
)
AFTERMATH_LAYOUT.BORDER.RULES_BOX = (
    AFTERMATH_LAYOUT.BORDER.TYPE_LINE + AFTERMATH_LAYOUT.SIZE.TYPE_LINE
)
AFTERMATH_LAYOUT.BORDER.OTHER = CARD_V // 2 - AFTERMATH_LAYOUT.SIZE.OTHER
AFTERMATH_LAYOUT.SIZE.RULES_BOX = (
    AFTERMATH_LAYOUT.BORDER.OTHER - AFTERMATH_LAYOUT.BORDER.RULES_BOX
)
AFTERMATH_LAYOUT.FONT_MIDDLE.TYPE_LINE = (
    AFTERMATH_LAYOUT.BORDER.TYPE_LINE + AFTERMATH_LAYOUT.SIZE.TYPE_LINE // 2 - BORDER // 2
)
AFTERMATH_SYMBOL_POSITION: XY = (
    CARD_H - BORDER - SYMBOL_SIZE,
    AFTERMATH_LAYOUT.BORDER.TYPE_LINE
    + (AFTERMATH_LAYOUT.SIZE.TYPE_LINE - SYMBOL_SIZE) // 2
)

FLIP_LAYOUT = Map[Map[int]](
    {
        "BORDER": Map[int](
            {
                "TITLE": 0,
            }
        ),
        "SIZE": Map[int](
            {
                "TITLE": STD_LAYOUT.SIZE.TITLE,
                "TYPE_LINE": STD_LAYOUT.SIZE.TYPE_LINE,
                "RULES_BOX": 200,
                "OTHER": STD_LAYOUT.SIZE.OTHER,
            }
        ),
        "FONT_MIDDLE": Map[int](),
    }
)
FLIP_LAYOUT.BORDER.TYPE_LINE = (
    FLIP_LAYOUT.BORDER.TITLE + FLIP_LAYOUT.SIZE.TITLE
)
FLIP_LAYOUT.BORDER.RULES_BOX = (
    FLIP_LAYOUT.BORDER.TYPE_LINE + FLIP_LAYOUT.SIZE.TYPE_LINE
)
FLIP_LAYOUT.BORDER.OTHER = (
    FLIP_LAYOUT.BORDER.RULES_BOX + FLIP_LAYOUT.SIZE.RULES_BOX
)
FLIP_LAYOUT.BORDER.ILLUSTRATION = (
    FLIP_LAYOUT.BORDER.OTHER + FLIP_LAYOUT.SIZE.OTHER
)
FLIP_LAYOUT.FONT_MIDDLE.TYPE_LINE = (
    FLIP_LAYOUT.BORDER.TYPE_LINE + FLIP_LAYOUT.SIZE.TYPE_LINE // 2 - BORDER // 2
)
FLIP_SYMBOL_POSITION: XY = (
    CARD_H - BORDER - SYMBOL_SIZE,
    FLIP_LAYOUT.BORDER.TYPE_LINE
    + (FLIP_LAYOUT.SIZE.TYPE_LINE - SYMBOL_SIZE) // 2
)
FLIP_PTL_BOX: Box = (
    (
        CARD_H - PTL_BOX_DIM[0] - PTL_BOX_MARGIN[0],
        FLIP_LAYOUT.BORDER.ILLUSTRATION - PTL_BOX_DIM[1] - PTL_BOX_MARGIN[1]
    ),
    (
        CARD_H - PTL_BOX_MARGIN[0],
        FLIP_LAYOUT.BORDER.ILLUSTRATION - PTL_BOX_MARGIN[1]
    )
)
