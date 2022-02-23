from __future__ import annotations
from typing import overload, Any
from scrython import Named, ScryfallError
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
import sys
import pickle
import textwrap
import re
import os
import argparse

import drawUtil, constants



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

        try:
            layout = self.layout
        except:
            return
        if layout == "split":
            secondHalfText = self.card_faces[1].oracle_text.split("\n")
            if secondHalfText[0].split(" ")[0] == "Aftermath":
                self.data["layout"] = "aftermath"
            if secondHalfText[-1].split(" ")[0] == "Fuse":
                self.data["layout"] = "fuse"

    def _checkForKey(self, attr: str) -> Any:
        if attr in self.data:
            return self.data[attr]
        raise KeyError(f"This card has no key {attr}")

    @property
    def name(self) -> str:
        return self._checkForKey("name")

    @property
    def colors(self) -> list[constants.MTG_COLORS]:
        return self._checkForKey("colors")

    @property
    def color_indicator(self) -> list[constants.MTG_COLORS]:
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
    def card_faces(self) -> list[Card]:
        faces = self._checkForKey("card_faces")
        layout = self.layout
        if layout in constants.DFC_LAYOUTS:
            layoutSymbol: str = "TDFC" if layout == "transform" else "MDFC"
            faces[0]["layout"] = layout
            faces[1]["layout"] = layout
            faces[0]["face"] = f"{{{layoutSymbol}_FRONT}}"
            faces[1]["face"] = f"{{{layoutSymbol}_BACK}}"
        return [Card(face) for face in faces]

    @property
    def face(self) -> str:
        return self._checkForKey("face")

    @property
    def color_indicator_reminder_text(self) -> str:
        try:
            cardColorIndicator: list[constants.MTG_COLORS] = self.color_indicator
        except:
            return ""
        if len(cardColorIndicator) == 5:
            colorIndicatorText = "all colors"
        else:
            colorIndicatorNames = [constants.COLOR_NAMES[c] for c in cardColorIndicator]
            if len(colorIndicatorNames) == 1:
                colorIndicatorText = colorIndicatorNames[0]
            else:
                colorIndicatorText = f'{", ".join(colorIndicatorNames[:-1])} and {colorIndicatorNames[-1]}'
        return f"({self.name} is {colorIndicatorText}.)\n"


Deck = list[Card]
Flavor = dict[str, str]

specialTextRegex = re.compile(r"\{.+?\}")


def replFunction(m: re.Match[str]):
    t = m.group()
    if t in constants.FONT_CODE_POINT:
        return constants.FONT_CODE_POINT[t]
    return t


@overload
def printSymbols(text: str) -> str:
    ...


@overload
def printSymbols(text: None) -> None:
    ...


def printSymbols(text: str | None) -> str | None:
    if text is None:
        return None
    # First − is \u2212, which is not in the font but is used in Planeswalker abilities
    # The second is \u002d, the ASCII one
    return specialTextRegex.sub(replFunction, text).replace("−", "-")


def loadCards(fileLoc: str) -> tuple[Deck, Flavor]:

    cardCache: dict[str, Card]

    if os.path.exists(constants.CACHE_LOC):
        with open(constants.CACHE_LOC, "rb") as p:
            cardCache = pickle.load(p)
    else:
        cardCache = {}

    with open(fileLoc) as f:
        cardsInDeck: Deck = []
        flavorNames: Flavor = {}

        doubleSpacesRegex = re.compile(r" {2,}")
        cardCountRegex = re.compile(r"^([0-9]+)x?")
        flavorNameRegex = re.compile(r"\[(.*?)\]")
        cardNameRegex = re.compile(r"^(?:\d+x? )?(.*?)(?: \[.*?\])?$")

        line: str
        for line in tqdm(f):  # type: ignore
            line = doubleSpacesRegex.sub(" ", line.strip())

            cardCountMatch = cardCountRegex.search(line)
            cardCount = int(cardCountMatch.groups()[0]) if cardCountMatch else 1

            flavorNameMatch = flavorNameRegex.search(line)

            cardNameMatch = cardNameRegex.search(line)
            cardName: str
            if cardNameMatch:
                cardName = cardNameMatch.groups()[0]
            else:
                raise Exception(f"No card name found in line {line}")

            if flavorNameMatch:
                flavorName = flavorNameMatch.groups()[0]
                flavorNames[cardName] = flavorName

            if cardName in constants.BASIC_LANDS:
                print(
                    f"{cardName} will not be printed. use the basic land generator (check readme) instead"
                )
                continue

            if cardName in cardCache:
                cardData = cardCache[cardName]
            else:
                print(f"{cardName} not in cache. searching...")
                try:
                    cardData: Card = Card(Named(fuzzy=cardName))
                except ScryfallError as err:
                    print(f"Skipping {cardName}. {err}")
                    continue

                cardCache[cardName] = cardData

            if cardData.layout in constants.DFC_LAYOUTS:
                facesData = cardData.card_faces
                for _ in range(cardCount):
                    cardsInDeck.append(facesData[0])
                    cardsInDeck.append(facesData[1])
            else:
                for _ in range(cardCount):
                    cardsInDeck.append(cardData)

    os.makedirs(os.path.dirname(constants.CACHE_LOC), exist_ok=True)
    with open(constants.CACHE_LOC, "wb") as p:
        pickle.dump(cardCache, p)

    return (cardsInDeck, flavorNames)


def makeImage(
    card: Card,
    setSymbol: Image.Image | None,
    flavorNames: Flavor = {},
    useColor: bool = False,
    useTextSymbols: bool = True,
):

    cardName: str = card.name
    cardColors: list[constants.MTG_COLORS] = card.colors
    cardManaCost: str = printSymbols(card.mana_cost)

    # Temp handler for flip / split / fuse cards
    try:
        cardText: str = card.oracle_text
    except KeyError:
        cardText: str = card.card_faces[0].oracle_text
    # Add text replacing the color indicator (if present)
    cardText = card.color_indicator_reminder_text + cardText

    cardTypeLine: str = card.type_line
    cardLayout: str = card.layout

    if useTextSymbols:
        cardText = printSymbols(cardText)

    if useColor:
        if not cardColors:
            frameColor = constants.FRAME_COLORS["C"]
        elif len(cardColors) == 1:
            frameColor = constants.FRAME_COLORS[cardColors[0]]
        else:
            frameColor = [constants.FRAME_COLORS[col] for col in cardColors]
    else:
        frameColor = constants.FRAME_COLORS["default"]

    cardImg, pen = drawUtil.blankCard(frameColor=frameColor)
    if isinstance(frameColor, list):
        if len(frameColor) > 2:
            frameColor = constants.FRAME_COLORS["M"]
        else:
            frameColor = constants.FRAME_COLORS["default"]

    # mana cost TODO cleanup and fix phyrexian
    costFont = ImageFont.truetype("MPLANTIN.ttf", 60)
    xPos = 685
    for c in cardManaCost[::-1]:
        pen.text((xPos, 65), c, font=costFont, fill="black", anchor="ra")
        if c in " /":
            xPos -= 20
        else:
            xPos -= 55

    displayName = flavorNames[cardName] if cardName in flavorNames else cardName
    if cardLayout in ["transform", "modal_dfc"]:
        displayName = printSymbols(f"{card.face} {displayName}")
    # 575 default width for name, default font 60
    nameFont = drawUtil.fitOneLine("matrixb.ttf", displayName, xPos - 100, 60)
    pen.text((70, 85), displayName, font=nameFont, fill="black", anchor="lm")

    # 600 width for typeline with symbol, default font 60
    typeFont = drawUtil.fitOneLine("matrixb.ttf", cardTypeLine, 540, 60)
    pen.text((70, 540), cardTypeLine, font=typeFont, fill="black", anchor="lm")

    if setSymbol is not None:
        cardImg.paste(setSymbol, (620, 520), setSymbol)

    fmtText, textFont = drawUtil.fitMultiLine("MPLANTIN.ttf", cardText, 600, 350, 40)
    pen.text((70, 600), fmtText, font=textFont, fill="black")

    if (
        "Creature" in cardTypeLine
        or "Planeswalker" in cardTypeLine
        or "Vehicle" in cardTypeLine
    ):
        pen.rectangle([550, 930, 675, 1005], outline=frameColor, fill="white", width=5)

        if "Creature" in cardTypeLine or "Vehicle" in cardTypeLine:
            # TODO two-digit p/t
            pt = "{}/{}".format(card.power, card.toughness)
            ptFont = drawUtil.fitOneLine("MPLANTIN.ttf", pt, 85, 60)
            pen.text((570, 970), pt, font=ptFont, fill="black", anchor="lm")

        else:
            loyaltyFont = ImageFont.truetype("MPLANTIN.ttf", 60)
            pen.text((595, 940), card.loyalty, font=loyaltyFont, fill="black")

    proxyFont = ImageFont.truetype("matrixb.ttf", 30)
    pen.text((70, 945), "v{}".format(constants.VERSION), font=proxyFont, fill="black")

    if cardName in flavorNames:
        pen.text((375, 490), cardName, font=proxyFont, fill="black", anchor="md")

    brush = constants.FONT_CODE_POINT["{PAINTBRUSH}"]
    credFont = ImageFont.truetype("MPLANTIN.ttf", 25)
    pen.text((70, 967), f"{brush}a11ce.com/BWProxy", font=credFont, fill="black")

    return (cardName, cardImg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate printable MTG proxies")
    parser.add_argument(
        "decklistPath",
        metavar="decklist_path",
        type=str,
        help="location of decklist file",
    )
    parser.add_argument(
        "setSymbolPath",
        nargs="?",
        metavar="set_symbol_path",
        type=str,
        help="location of set symbol file (optional)",
    )
    parser.add_argument(
        "--color",
        action="store_true",
        help="print card frames and mana symbols in color",
    )

    args = parser.parse_args()

    decklistPath: str = args.decklistPath

    deckName = decklistPath.split(".")[0]
    if args.setSymbolPath:
        setSymbol = Image.open(args.setSymbolPath).convert("RGBA").resize((60, 60))
    else:
        setSymbol = None

    allCards, flavorNames = loadCards(decklistPath)
    images = [
        makeImage(card, setSymbol, flavorNames=flavorNames, useColor=args.color)
        for card in tqdm(allCards)
    ]

    drawUtil.savePages(images, deckName)
