from __future__ import annotations
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate printable MTG proxies")
    parser.add_argument(
        "decklistPath",
        metavar="decklist_path",
        help="location of decklist file",
    )
    parser.add_argument(
        "--symbol-path",
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
    parser.add_argument(
        "--no-text-symbols",
        action="store_false",
        dest="useTextSymbols",
        help="print cards with {W} instead of the corresponding symbol",
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
        drawUtil.drawCard(
            card=card,
            symbol=setSymbol,
            flavorNames=flavorNames,
            isColored=args.color,
            useTextSymbols=args.useTextSymbols,
        )
        for card in tqdm(allCards)
    ]

    drawUtil.savePages(images, deckName)
