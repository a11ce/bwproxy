from typing import Literal

VERSION = "1.5"

CACHE_LOC = "cardcache/cardcache.p"

MTG_COLORS = Literal["White", "Blue", "Black", "Red", "Green"]

FRAME_COLORS = {
    "White": "#fcf4a3",
    "Blue": "#127db4",
    "Black": "#692473",
    "Red": "#e13c32",
    "Green": "#0f7846",
    "Gold": "#d4af37",
    "Colorless": "#919799"
}

MAGIC_SYMBOL_ORDER = ['W', 'U', 'B', 'R', 'G']
# Can be obtained programmatically, but that's more concise 
MAGIC_HYBRID_ORDER = ['W/U', 'U/B', 'B/R', 'R/G', 'G/W', 'W/B', 'U/R', 'B/G', 'R/W', 'G/U']

FONT_CODE_POINT: dict[str, str] = {}
for i in range(21):
    FONT_CODE_POINT["{" + str(i) + "}"] = chr(0x200 + i) # Generic mana cost (0 to 20)
FONT_CODE_POINT["{X}"] = chr(0x215)
FONT_CODE_POINT["{Y}"] = chr(0x216)
FONT_CODE_POINT["{Z}"] = chr(0x217)
FONT_CODE_POINT["{T}"] = chr(0x218)
FONT_CODE_POINT["{Q}"] = chr(0x219)
FONT_CODE_POINT["{MDFC_FRONT}"] = chr(0x21A)
FONT_CODE_POINT["{MDFC_BACK}"] = chr(0x21B)
FONT_CODE_POINT["{TDFC_FRONT}"] = chr(0x21C)
FONT_CODE_POINT["{TDFC_BACK}"] = chr(0x21D)
FONT_CODE_POINT["{S}"] = chr(0x21E)
FONT_CODE_POINT["{C}"] = chr(0x21F)
for (i, c) in enumerate(MAGIC_SYMBOL_ORDER): # Colored Mana
    FONT_CODE_POINT["{" + c + "}"] = chr(0x220 + i)
for (i, c) in enumerate(MAGIC_SYMBOL_ORDER): # Two-Hybrid Mana
    FONT_CODE_POINT["{2/" + c + "}"] = chr(0x225 + i)
for (i, c) in enumerate(MAGIC_SYMBOL_ORDER): # Phyrexian Mana
    FONT_CODE_POINT["{" + c + "/P}"] = chr(0x22A + i)
FONT_CODE_POINT["{P}"] = chr(0x22F) # Standard Phyrexian Mana
for (i, h) in enumerate(MAGIC_HYBRID_ORDER): # Hybrid Mana
    FONT_CODE_POINT["{" + h + "}"] = chr(0x230 + i)
for (i, h) in enumerate(MAGIC_HYBRID_ORDER): # Hybrid Phyrexian Mana
    FONT_CODE_POINT["{" + h + "/P}"] = chr(0x240 + i)
FONT_CODE_POINT["{E}"] = chr(0x23A) # Energy Counter
FONT_CODE_POINT["{PAINTBRUSH}"] = chr(0x23F) # Paintbrush Symbol


TODO = """
Split / Fuse / Flip / Adventure frames (Maybe also Class, Sagas and Leveler?)
Better Double-Faced card handler (front/back face symbols, add both to the file)
Better search functionality:
* searching "Likeness of the Seeker" results in "Azusa's Many Journeys"
* seaching "Alive" results in "Buried Alive" (should be "Alive // Well")
* searching "Endbringer" results in "Shauku, Endbringer"
Replace magic numbers (750, 1050...) with constants
Add options for A4 and letter paper
Better mana symbols, both in cost and in text
(should be in the new font file, only problem is Tamiyo, Compleated Sage)
Color indicator in text
Tested searching for Failure // Comply via api, Failure is the first result

Move to Scryfall API
"""