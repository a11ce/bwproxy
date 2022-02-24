from __future__ import annotations
from typing import overload
from scrython import Named, ScryfallError
from PIL import Image
from tqdm import tqdm
import pickle
import re
import os
import argparse

import drawUtil
import projectConstants as C
from projectTypes import Card, Deck, Flavor


specialTextRegex = re.compile(r"\{.+?\}")


def replFunction(m: re.Match[str]):
    t = m.group()
    if t in C.FONT_CODE_POINT:
        return C.FONT_CODE_POINT[t]
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

    if os.path.exists(C.CACHE_LOC):
        with open(C.CACHE_LOC, "rb") as p:
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

        for line in tqdm(f):
            line = doubleSpacesRegex.sub(" ", line.strip())

            cardCountMatch = cardCountRegex.search(line)
            cardCount = int(cardCountMatch.groups()[0]) if cardCountMatch else 1

            flavorNameMatch = flavorNameRegex.search(line)

            cardNameMatch = cardNameRegex.search(line)

            if cardNameMatch:
                cardName = cardNameMatch.groups()[0]
            else:
                raise Exception(f"No card name found in line {line}")

            if flavorNameMatch:
                flavorName = flavorNameMatch.groups()[0]
                flavorNames[cardName] = flavorName

            if cardName in C.BASIC_LANDS:
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

            if cardData.layout in C.DFC_LAYOUTS:
                facesData = cardData.card_faces
                for _ in range(cardCount):
                    cardsInDeck.append(facesData[0])
                    cardsInDeck.append(facesData[1])
            else:
                for _ in range(cardCount):
                    cardsInDeck.append(cardData)

    os.makedirs(os.path.dirname(C.CACHE_LOC), exist_ok=True)
    with open(C.CACHE_LOC, "wb") as p:
        pickle.dump(cardCache, p)

    return (cardsInDeck, flavorNames)


def makeImage(
    card: Card,
    setSymbol: Image.Image | None,
    flavorNames: Flavor = {},
    useColor: bool = False,
    useTextSymbols: bool = True,
):
    # cardName: str = card.name
    cardColors: list[C.MTG_COLORS] = card.colors
    cardManaCost: str = printSymbols(card.mana_cost)

    # Temp handler for flip / split / fuse cards
    try:
        cardText: str = card.oracle_text
    except KeyError:
        cardText: str = card.card_faces[0].oracle_text
    # Add text replacing the color indicator (if present)
    cardText = card.color_indicator_reminder_text + cardText

    # cardTypeLine: str = card.type_line
    # cardLayout: str = card.layout

    if useTextSymbols:
        cardText = printSymbols(cardText)

    if useColor:
        if not cardColors:
            frameColor = C.FRAME_COLORS["C"]
        elif len(cardColors) == 1:
            frameColor = C.FRAME_COLORS[cardColors[0]]
        else:
            frameColor = [C.FRAME_COLORS[col] for col in cardColors]
    else:
        frameColor = C.FRAME_COLORS["default"]

    cardImg, pen = drawUtil.blankCard(
        frameColor=frameColor, card=card, setSymbol=setSymbol
    )

    if isinstance(frameColor, list):
        if len(frameColor) > 2:
            frameColor = C.FRAME_COLORS["M"]
        else:
            frameColor = C.FRAME_COLORS["default"]

    drawUtil.drawTitleLine(
        pen=pen, card=card, manaCost=cardManaCost, flavorNames=flavorNames
    )
    drawUtil.drawTypeLine(pen=pen, card=card)
    drawUtil.drawTextBox(pen=pen, card=card, cardText=cardText)
    drawUtil.drawPTL(pen=pen, card=card)
    drawUtil.drawOther(pen=pen)

    return cardImg


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate printable MTG proxies")
    parser.add_argument(
        "decklistPath",
        metavar="decklist_path",
        help="location of decklist file",
    )
    parser.add_argument(
        "--symbol_path",
        # metavar="set_symbol_path",
        help="location of set symbol file (optional)",
    )
    parser.add_argument(
        "--color",
        action="store_true",
        help="print card frames and mana symbols in color",
    )
    parser.add_argument(
        "--page",
        default=C.PAGE_FORMAT[0],
        choices=C.PAGE_FORMAT,
        help="printing page format (optional)",
    )
    parser.add_argument(
        "--small",
        action="store_true",
        help="print cards at 80%% in size, allowing to fit more in one page",
    )

    args = parser.parse_args()

    page: C.PageFormat = args.page
    decklistPath: str = args.decklistPath

    deckName = decklistPath.split(".")[0]
    if args.symbol_path:
        setSymbol = drawUtil.resizeSetSymbol(
            Image.open(args.symbol_path).convert("RGBA")
        )
    else:
        setSymbol = None

    allCards, flavorNames = loadCards(decklistPath)
    images = [
        makeImage(
            card=card, setSymbol=setSymbol, flavorNames=flavorNames, useColor=args.color
        )
        for card in tqdm(allCards)
    ]

    drawUtil.savePages(images, deckName)
