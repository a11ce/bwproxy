from __future__ import annotations
from typing import Any, List, Dict
from scrython import Named
import re

from . import projectConstants as C

nonColorRe = re.compile(r"[^WUBRG]")


def extractColor(manaCost: str) -> list[C.MTG_COLORS]:
    colors = nonColorRe.sub("", manaCost)
    ret: list[C.MTG_COLORS] = []
    for c in colors:
        if c in C.MANA_SYMBOLS and c not in ret:
            ret.append(c)
    return ret


class Card:
    """
    Handler class for a card, a card face, or a card half.
    Can be initialized with a Scryfall search result.
    Automatically sets aftermath and fuse layouts.
    Automatically sets layout and card face for transform and modal_dfc faces
    Has a method for color indicator reminder text
    """

    def __init__(self, card: dict[str, Any] | Named):
        if isinstance(card, Named):
            self.data: dict[str, Any] = card.scryfallJson  # type: ignore
        else:
            self.data = card

        if self.isEmblem():
            self.data["layout"] = C.EMBLEM
            self.data["type_line"] = "Emblem"
            self.data["name"] = self.data["name"].replace(" Emblem", "")

        if self.isToken():
            self.data["layout"] = C.TOKEN
            if len(self.colors) > 0:
                self.data["color_indicator"] = self.colors

        try:
            layout = self.layout
        except:
            return
        if layout == C.SPLIT:
            # Set up alternative split layouts (aftermath and fuse)
            secondHalfText = self.card_faces[1].oracle_text.split("\n")
            if secondHalfText[0].split(" ")[0] == "Aftermath":
                self.data["layout"] = C.AFTER
            if secondHalfText[-1].split(" ")[0] == "Fuse":
                self.data["layout"] = C.FUSE
                # Adding the fuse text to the main card
                self.data["fuse_text"] = secondHalfText[-1]

    def _checkForKey(self, attr: str) -> Any:
        if attr in self.data:
            return self.data[attr]
        raise KeyError(f"This card has no key {attr}: {self.name}")

    def __str__(self) -> str:
        return f"Card ({self.name})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def name(self) -> str:
        return self._checkForKey("name")

    @property
    def colors(self) -> list[C.MTG_COLORS]:
        return self._checkForKey("colors")

    @property
    def color_indicator(self) -> list[C.MTG_COLORS]:
        return self._checkForKey("color_indicator")

    @property
    def mana_cost(self) -> str:
        return self._checkForKey("mana_cost")

    @property
    def oracle_text(self) -> str:
        return self._checkForKey("oracle_text")

    @property
    def type_line(self) -> str:
        return self._checkForKey("type_line")

    @property
    def power(self) -> str:
        return self._checkForKey("power")

    @property
    def toughness(self) -> str:
        return self._checkForKey("toughness")

    @property
    def loyalty(self) -> str:
        return self._checkForKey("loyalty")

    @property
    def layout(self) -> str:
        return self._checkForKey("layout")

    @property
    def fuse_text(self) -> str:
        return self._checkForKey("fuse_text")

    @property
    def card_faces(self) -> list[Card]:
        faces = self._checkForKey("card_faces")
        layout = self.layout
        faces[0]["face_type"] = layout
        faces[1]["face_type"] = layout
        faces[0]["face_num"] = 0
        faces[1]["face_num"] = 1

        if layout in C.DFC_LAYOUTS:
            faces[0]["face_symbol"] = f"{{{layout}_FRONT}}"
            faces[1]["face_symbol"] = f"{{{layout}_BACK}}"
            faces[0]["layout"] = layout
            faces[1]["layout"] = layout

        if layout == C.FLIP:
            faces[0]["face_symbol"] = f"{{{layout}_FRONT}}"
            faces[1]["face_symbol"] = f"{{{layout}_BACK}}"
            faces[0]["colors"] = self.colors
            faces[1]["colors"] = self.colors
            faces[1]["color_indicator"] = self.colors

        if layout in [C.SPLIT, C.FUSE, C.AFTER]:
            # Subfaces don't have colors, and if you ask the main face it will respond
            # with all the card's colors, so we need to extract them from mana cost
            faces[0]["colors"] = extractColor(faces[0]["mana_cost"])
            faces[1]["colors"] = extractColor(faces[1]["mana_cost"])

        if layout == C.FUSE:
            # Fuse text is handled separately, so we remove it from the faces' oracle text
            faces[0]["oracle_text"] = faces[0]["oracle_text"].replace(
                "\n" + self.fuse_text, ""
            )
            faces[1]["oracle_text"] = faces[1]["oracle_text"].replace(
                "\n" + self.fuse_text, ""
            )

        return [Card(face) for face in faces]

    @property
    def face_symbol(self) -> str:
        """
        face_symbol is the face indicator symbol appearing on dfc cards
        (front face / back face)
        It's also added to flip cards, using tap and untap symbols
        Only set up for faces (not whole cards)
        """
        return self._checkForKey("face_symbol")

    @property
    def face_type(self) -> str:
        """
        face_type is the analogous of layout for all double cards
        Value is the same of parent's layout
        If it's not present, returns "standard"
        """
        try:
            return self._checkForKey("face_type")
        except:
            return C.STD

    @property
    def face_num(self) -> int:
        """
        face_num is the position of the current face in the card (0 or 1)
        0 is the left part (split cards), the vertical part (aftermath),
        the main creature (adventure), the unflipped part (flip)
        or the main face (DFC), while 1 is the other one.
        Only set up for faces (not whole cards)
        """
        return self._checkForKey("face_num")

    @property
    def color_indicator_reminder_text(self) -> str:
        """
        Since the proxies are b/w, we need to write reminder text
        for color indicators and tokens
        """
        try:
            cardColorIndicator: list[C.MTG_COLORS] = self.color_indicator
        except:
            return ""
        
        if len(cardColorIndicator) == 5:
            colorIndicatorText = "all colors"
        else:
            colorIndicatorNames = [C.COLOR_NAMES[c] for c in cardColorIndicator]
            if len(colorIndicatorNames) == 1:
                colorIndicatorText = colorIndicatorNames[0]
            else:
                colorIndicatorText = f'{", ".join(colorIndicatorNames[:-1])} and {colorIndicatorNames[-1]}'
        
        if self.isToken() and self.name in self.type_line:
            name = "This token"
        else:
            name = self.name

        return f"({name} is {colorIndicatorText}.)\n"

    def hasPT(self) -> bool:
        try:
            self.power
            return True
        except KeyError:
            return False

    def hasL(self) -> bool:
        try:
            self.loyalty
            return True
        except KeyError:
            return False

    def hasPTL(self) -> bool:
        return self.hasPT() or self.hasL()

    def isBasicLand(self) -> bool:
        return self.name in C.BASIC_LANDS

    def isToken(self) -> bool:
        return "Token" in self.type_line

    def isTextlessToken(self) -> bool:
        return self.isToken() and self.oracle_text == ""

    def isEmblem(self) -> bool:
        return "Emblem" in self.type_line

    def isTokenOrEmblem(self) -> bool:
        return self.isToken() or self.isEmblem()

    @property
    def flavor_name(self) -> str:
        return self._checkForKey("flavor_name")

    def has_flavor_name(self) -> bool:
        try:
            self.flavor_name
            return True
        except:
            return False


Deck = List[Card]
Flavor = Dict[str, str]

XY = C.XY
Box = C.Box
Layout = C.Layout
