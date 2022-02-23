from typing import Literal

VERSION = "1.5"

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
    "default": "black",
}

BASIC_LANDS = ["Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"]

MANA_SYMBOLS = ["W", "U", "B", "R", "G"]
# Can be obtained programmatically, but that's more concise
HYBRID_SYMBOLS = ["W/U", "U/B", "B/R", "R/G", "G/W", "W/B", "U/R", "B/G", "R/W", "G/U"]
COLOR_NAMES = {
    "W": "white",
    "U": "blue",
    "B": "black",
    "R": "red",
    "G": "green"
}

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
SPLIT_LAYOUTS = ["flip", "split", "fuse", "aftermath", "adventure"]

TODO = """
Split / Fuse / Flip / Adventure frames (Maybe also Class, Sagas and Leveler?) ❌
Better Double-Faced card handler (front/back face symbols, add both to the file) ✅
Better search functionality:
* searching "Likeness of the Seeker" results in "Azusa's Many Journeys" ✅
* seaching "Alive" results in "Buried Alive" (should be "Alive // Well") ✅
* searching "Endbringer" results in "Shauku, Endbringer" ✅
Replace magic numbers (750, 1050...) with constants ❌
Add options for A4 and letter paper ❌
Better mana symbols, both in cost and in text ✅
(should be in the new font file, only problem is Tamiyo, Compleated Sage) ✅
Color indicator in text ✅
Tested searching for Failure // Comply via api, Failure is the first result

Move to Scryfall API ✅
"""
