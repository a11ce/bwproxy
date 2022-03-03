from __future__ import annotations
from typing import Dict
from scrython import Named, ScryfallError
from PIL import Image
from tqdm import tqdm
import pickle
import re
import os
import argparse

import bwproxy.drawUtil as drawUtil
import bwproxy.projectConstants as C
from bwproxy.projectTypes import Card, Deck, Flavor


def loadCards(fileLoc: str, ignoreBasicLands: bool = False) -> tuple[Deck, Flavor]:

    cardCache: Dict[str, Card]

    if os.path.exists(C.CACHE_LOC):
        with open(C.CACHE_LOC, "rb") as p:
            cardCache = pickle.load(p)
    else:
        cardCache = {}

    with open(fileLoc) as f:
        cardsInDeck: Deck = []
        flavorNames: Flavor = {}

        doubleSpacesRegex = re.compile(r" {2,}")
        removeCommentsRegex = re.compile(r"^//.*$|#.*$")
        cardCountRegex = re.compile(r"^([0-9]+)x?")
        flavorNameRegex = re.compile(r"\[(.*?)\]")
        cardNameRegex = re.compile(r"^(?:\d+x? )?(.*?)(?: \[.*?\])?$")

        for line in f:
            line = removeCommentsRegex.sub("", line)
            line = doubleSpacesRegex.sub(" ", line.strip())

            if line == "":
                continue

            cardCountMatch = cardCountRegex.search(line)
            cardCount = int(cardCountMatch.groups()[0]) if cardCountMatch else 1

            flavorNameMatch = flavorNameRegex.search(line)

            cardNameMatch = cardNameRegex.search(line)

            if cardNameMatch:
                cardName = cardNameMatch.groups()[0]
            else:
                raise Exception(f"No card name found in line {line}")

            if ignoreBasicLands and cardName in C.BASIC_LANDS:
                print(
                    f"You have requested to ignore basic lands. {cardName} will not be printed."
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
            
            if ignoreBasicLands and cardData.name in C.BASIC_LANDS:
                print(
                    f"You have requested to ignore basic lands. {cardName} will not be printed."
                )
                continue

            if cardData.has_flavor_name():
                flavorNames[cardData.name] = cardData.flavor_name

            if flavorNameMatch:
                flavorName = flavorNameMatch.groups()[0]
                flavorNames[cardData.name] = flavorName

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
        "--icon-path", "-i",
        metavar="icon_path",
        dest="setIconPath",
        help="location of set icon file",
    )
    parser.add_argument(
        "--page-format", "-p",
        default=C.PAGE_FORMAT[0],
        choices=C.PAGE_FORMAT,
        dest="pageFormat",
        help="printing page format",
    )
    parser.add_argument(
        "--color", "-c",
        action="store_true",
        help="print card frames and mana symbols in color",
    )
    parser.add_argument(
        "--no-text-symbols",
        action="store_false",
        dest="useTextSymbols",
        help="print cards with e.g. {W} instead of the corresponding symbol",
    )
    parser.add_argument(
        "--small", "-s",
        action="store_true",
        help="print cards at 75%% in size, allowing to fit more in one page",
    )
    parser.add_argument(
        "--no-card-space",
        action="store_true",
        dest="noCardSpace",
        help="print cards without space between them",
    )
    parser.add_argument(
        "--full-art-lands",
        action="store_true",
        dest="fullArtLands",
        help="print full art basic lands instead of big symbol basic lands",
    )
    parser.add_argument(
        "--ignore-basic-lands", "--ignore-basics",
        action="store_true",
        dest="ignoreBasicLands",
        help="skip basic lands when generating images",
    )

    args = parser.parse_args()

    decklistPath: str = args.decklistPath
    
    deckName = decklistPath.split("/")[-1].split("\\")[-1].split(".")[0]
    if args.setIconPath:
        setIcon = drawUtil.resizeSetIcon(
            Image.open(args.setIconPath).convert("RGBA")
        )
    else:
        setIcon = None

    allCards, flavorNames = loadCards(decklistPath, ignoreBasicLands=args.ignoreBasicLands)
    images = [
        drawUtil.drawCard(
            card=card,
            setIcon=setIcon,
            flavorNames=flavorNames,
            isColored=args.color,
            useTextSymbols=args.useTextSymbols,
            fullArtLands=args.fullArtLands,
        )
        for card in tqdm(
            allCards,
            desc="Card drawing progress: ",
            unit="card",
        )
    ]
    drawUtil.savePages(
        images=images,
        deckName=deckName,
        small=args.small,
        pageFormat=args.pageFormat,
        noCardSpace=args.noCardSpace,
    )
