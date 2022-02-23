from typing import Optional, overload
from mtgsdk.card import Card
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
import sys
import pickle
import textwrap
import re
import os
import argparse

import drawUtil, constants

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
                cardDat = cardCache[cardName]
            else:
                print(f"{cardName} not in cache. searching...")
                searchResults: Deck = Card.where(name=cardName).all()

                if len(searchResults) == 0:
                    print(f"Warning! {cardName} not found in search")
                    continue

                cardNames: list[str] = [c.name for c in searchResults]
                if len(set(cardNames)) == 1:
                    # Search yielded only one result
                    pass
                elif any([c == cardName for c in cardNames]):
                    searchResults = [
                        card for card in searchResults if card.name == cardName
                    ]
                else:
                    filterRe = re.compile(f"(?:^{cardName} //|// {cardName}$)")
                    cardNames = list(
                        filter(lambda n: filterRe.search(n) is not None, cardNames)
                    )
                    if len(set(cardNames)) == 1:
                        searchResults = list(
                            filter(
                                lambda c: filterRe.search(c.name) is not None,
                                searchResults,
                            )
                        )
                    else:
                        print(
                            f"Warning! {cardName} does not uniquely identify a card, skipping"
                        )
                        continue

                cardDat = searchResults[0]
                cardCache[cardName] = cardDat

            for _ in range(cardCount):
                cardsInDeck.append(cardDat)

    os.makedirs(os.path.dirname(constants.CACHE_LOC), exist_ok=True)
    with open(constants.CACHE_LOC, "wb") as p:
        pickle.dump(cardCache, p)

    return (cardsInDeck, flavorNames)


def makeImage(
    card: Card,
    setSymbol: Image.Image | None,
    flavorNames: Flavor = {},
    useColor: bool = False,
):

    cardColors: Optional[list[constants.MTG_COLORS]] = card.colors
    cardManaCost: str | None = card.mana_cost
    cardName: str = card.name
    cardText: str | None = printSymbols(card.text)  # type: ignore

    if useColor:
        if not cardColors:
            frameColor = constants.FRAME_COLORS["Colorless"]
        elif len(cardColors) == 1:
            frameColor = constants.FRAME_COLORS[cardColors[0]]
        else:
            frameColor = [constants.FRAME_COLORS[col] for col in cardColors]
    else:
        frameColor = "black"

    cardImg, pen = drawUtil.blankCard(frameColor=frameColor)
    if isinstance(frameColor, list):
        if len(frameColor) > 2:
            frameColor = constants.FRAME_COLORS["Gold"]
        else:
            frameColor = "black"

    # mana cost TODO cleanup and fix phyrexian
    costFont = ImageFont.truetype("MPLANTIN.ttf", 60)
    xPos = 685

    if cardManaCost is not None:
        fmtCost = printSymbols(cardManaCost)

        for c in fmtCost[::-1]:
            pen.text((xPos, 65), c, font=costFont, fill="black", anchor="ra")
            xPos -= 55

    # 575 default width for name, default font 60
    if cardName in flavorNames:
        nameFont = drawUtil.fitOneLine(
            "matrixb.ttf", flavorNames[cardName], xPos - 100, 60
        )
        pen.text(
            (70, 85), flavorNames[cardName], font=nameFont, fill="black", anchor="lm"
        )
    else:
        nameFont = drawUtil.fitOneLine("matrixb.ttf", cardName, xPos - 100, 60)
        pen.text((70, 85), cardName, font=nameFont, fill="black", anchor="lm")

    # 600 width for typeline with symbol, default font 60
    typeLine: str = card.type
    typeFont = drawUtil.fitOneLine("matrixb.ttf", typeLine, 540, 60)
    pen.text((70, 540), typeLine, font=typeFont, fill="black", anchor="lm")

    if setSymbol is not None:
        cardImg.paste(setSymbol, (620, 520), setSymbol)

    fmtText, textFont = drawUtil.fitMultiLine("MPLANTIN.ttf", cardText, 600, 350, 40)
    pen.text((70, 600), fmtText, font=textFont, fill="black")

    if "Creature" in typeLine or "Planeswalker" in typeLine or "Vehicle" in typeLine:
        pen.rectangle([550, 930, 675, 1005], outline=frameColor, fill="white", width=5)

        if "Creature" in typeLine or "Vehicle" in typeLine:
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
