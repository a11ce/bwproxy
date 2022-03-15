from __future__ import annotations
from typing import Dict, List, Optional
from scrython import Named, Search, ScryfallError
from PIL import Image
from tqdm import tqdm
import pickle
import re
import os
import argparse

import bwproxy.drawUtil as drawUtil
import bwproxy.projectConstants as C
from bwproxy.projectTypes import Card, Deck, Flavor


def disambiguateTokenResults(query: str, results: List[Card]) -> List[Card]:
    singleFaced: List[Card] = []
    disambiguated: Dict[str, Card] = {}
    for card in results:
        try:
            singleFaced.extend(card.card_faces)
        except:
            singleFaced.append(card)
    for card in singleFaced:
        if (
            query.lower().replace(",", "") in card.name.lower().replace(",", "")
            and card.type_line != "Token"
            and card.type_line != ""
        ):
            index = f"{card.name}\n{card.type_line}\n{sorted(card.colors)}\n{card.oracle_text}"
            if card.hasPT():
                index += f"\n{card.power}/{card.toughness}"
            disambiguated[index] = card

    return list(disambiguated.values())


def searchToken(tokenName: str, tokenType: str = C.TOKEN) -> List[Card]:
    if tokenType == C.EMBLEM:
        exactName = f"{tokenName} Emblem"
    else:
        exactName = tokenName
    try:
        cardQuery = Search(q=f"type:{tokenType} !'{exactName}")
        results = [Card(cardData) for cardData in cardQuery.data()]  # type: ignore
    except ScryfallError:
        try:
            cardQuery = Search(q=f"type:{tokenType} {tokenName}")
            results = [Card(cardData) for cardData in cardQuery.data()]  # type: ignore
        except ScryfallError:
            results: List[Card] = []
    return disambiguateTokenResults(query=tokenName, results=results)


def parseToken(text: str, name: Optional[str] = None) -> Card:
    data = [line.strip() for line in text.split(";")]

    if data[0].lower() == "legendary":
        supertype = "Legendary "
        data.pop(0)
    else:
        supertype = ""

    if "/" in data[0].lower():
        pt = data[0].split("/")
        power = pt[0]
        toughness = pt[1]
        data.pop(0)
    else:
        power = None
        toughness = None

    colors = [color for color in data.pop(0) if color != "C"]
    subtypesString = data.pop(0)

    possibleTypes = [word.strip().title() for word in data[0].split()]
    if set(possibleTypes) <= set(C.CARD_TYPES):
        # There are subtypes
        types = f"{supertype}{' '.join(possibleTypes)}"
        data.pop(0)
        subtypes = " ".join([t.strip().title() for t in subtypesString.split()])
        name = name if name else subtypes
        type_line = f"Token {types} — {subtypes}"
    else:
        # No subtypes
        typesString = subtypesString
        possibleTypes = [word.strip().title() for word in typesString.split()]
        type_line = f"Token {supertype}{' '.join(possibleTypes)}"

    if name is None:
        raise Exception(f"Missing name for token without subtypes: {text}")
        
    jsonData = {
        "type_line": type_line,
        "name": name,
        "colors": colors,
        "layout": C.TOKEN,
        "mana_cost": "",
    }

    if "Creature" in jsonData["type_line"] or "Vehicle" in jsonData["type_line"]:
        try:
            assert power is not None
            assert toughness is not None
            jsonData["power"] = power
            jsonData["toughness"] = toughness
        except:
            raise Exception(f"Power/Toughness missing for token: {name}")
    
    text_lines = [line for line in data if line]
    jsonData["oracle_text"] = "\n".join(text_lines)
    return Card(jsonData)


def loadCards(
    fileLoc: str, ignoreBasicLands: bool = False, alternativeFrames: bool = False
) -> tuple[Deck, Flavor]:

    cardCache: Dict[str, Card]
    tokenCache: Dict[str, Card]

    if os.path.exists(C.CACHE_LOC):
        with open(C.CACHE_LOC, "rb") as p:
            cardCache = pickle.load(p)
    else:
        cardCache = {}

    if os.path.exists(C.TOKEN_CACHE_LOC):
        with open(C.TOKEN_CACHE_LOC, "rb") as p:
            tokenCache = pickle.load(p)
    else:
        tokenCache = {}

    with open(fileLoc) as f:
        cardsInDeck: Deck = []
        flavorNames: Flavor = {}

        tokenEmblemRegex = re.compile(r"^(?:\d+x )?\((token|emblem)\)", flags=re.I)
        if tokenEmblemRegex:
            pass
        doubleSpacesRegex = re.compile(r" {2,}")
        removeCommentsRegex = re.compile(r"^//.*$|#.*$")
        cardCountRegex = re.compile(r"^([0-9]+)x?")
        flavorNameRegex = re.compile(r"\[(.*?)\]")
        cardNameRegex = re.compile(
            r"^(?:\d+x? )?(?:\((?:token|emblem)\) )?(.*?)(?: \[.*?\])?$", flags=re.I
        )

        for line in f:
            line = removeCommentsRegex.sub("", line)
            line = doubleSpacesRegex.sub(" ", line.strip())

            if line == "":
                continue

            cardCountMatch = cardCountRegex.search(line)
            cardCount = int(cardCountMatch.groups()[0]) if cardCountMatch else 1

            flavorNameMatch = flavorNameRegex.search(line)
            cardNameMatch = cardNameRegex.search(line)
            tokenMatch = tokenEmblemRegex.search(line)

            if cardNameMatch:
                cardName = cardNameMatch.groups()[0]
            else:
                raise Exception(f"No card name found in line {line}")

            if ignoreBasicLands and cardName in C.BASIC_LANDS:
                print(
                    f"You have requested to ignore basic lands. {cardName} will not be printed."
                )
                continue

            if tokenMatch:
                tokenType = tokenMatch.groups()[0].lower()
                if ";" in cardName:
                    if flavorNameMatch:
                        tokenName = flavorNameMatch.groups()[0]
                    else:
                        tokenName = None
                    tokenData = parseToken(text=cardName, name=tokenName)
                elif cardName in tokenCache:
                    tokenData = tokenCache[cardName]
                else:
                    print(f"{cardName} not in cache. searching...")
                    tokenList = searchToken(tokenName=cardName, tokenType=tokenType)

                    if len(tokenList) == 0:
                        print(f"Skipping {cardName}. No corresponding tokens found")
                        continue
                    if len(tokenList) > 1:
                        print(
                            f"Skipping {cardName}. Too many tokens found. Consider specifying the token info in the input file"
                        )
                        continue
                    tokenData = tokenList[0]

                tokenCache[cardName] = tokenData
                for _ in range(cardCount):
                    cardsInDeck.append(tokenData)
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

                print(f"Card found! {cardData.name}")
                cardCache[cardName] = cardData

            if ignoreBasicLands and cardData.name in C.BASIC_LANDS:
                print(
                    f"You have requested to ignore basic lands. {cardName} will not be printed."
                )
                continue

            if cardData.hasFlavorName():
                flavorNames[cardData.name] = cardData.flavor_name

            if flavorNameMatch:
                flavorName = flavorNameMatch.groups()[0]
                flavorNames[cardData.name] = flavorName

            if cardData.layout in C.DFC_LAYOUTS or (
                cardData.layout == C.FLIP and alternativeFrames
            ):
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

    os.makedirs(os.path.dirname(C.TOKEN_CACHE_LOC), exist_ok=True)
    with open(C.TOKEN_CACHE_LOC, "wb") as p:
        pickle.dump(tokenCache, p)

    return (cardsInDeck, flavorNames)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate printable MTG proxies")
    parser.add_argument(
        "decklistPath",
        metavar="decklist_path",
        help="location of decklist file",
    )
    parser.add_argument(
        "--icon-path",
        "-i",
        metavar="icon_path",
        dest="setIconPath",
        help="location of set icon file",
    )
    parser.add_argument(
        "--page-format",
        "-p",
        default=C.PAGE_FORMAT[0],
        choices=C.PAGE_FORMAT,
        dest="pageFormat",
        help="printing page format",
    )
    parser.add_argument(
        "--color",
        "-c",
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
        "--small",
        "-s",
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
        "--ignore-basic-lands",
        "--ignore-basics",
        action="store_true",
        dest="ignoreBasicLands",
        help="skip basic lands when generating images",
    )
    parser.add_argument(
        "--alternative-frames",
        action="store_true",
        dest="alternativeFrames",
        help="print flip cards as DFC, aftermath as regular split",
    )

    args = parser.parse_args()

    decklistPath: str = args.decklistPath

    deckName = decklistPath.split("/")[-1].split("\\")[-1].split(".")[0]
    if args.setIconPath:
        setIcon = drawUtil.resizeSetIcon(Image.open(args.setIconPath).convert("RGBA"))
    else:
        setIcon = None

    allCards, flavorNames = loadCards(
        decklistPath,
        ignoreBasicLands=args.ignoreBasicLands,
        alternativeFrames=args.alternativeFrames,
    )
    images = [
        drawUtil.drawCard(
            card=card,
            setIcon=setIcon,
            flavorNames=flavorNames,
            isColored=args.color,
            useTextSymbols=args.useTextSymbols,
            fullArtLands=args.fullArtLands,
            alternativeFrames=args.alternativeFrames,
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
