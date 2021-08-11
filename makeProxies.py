from mtgsdk import Card
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
import sys
import pickle
import textwrap
import re
import os

import drawUtil


def loadCards(fileLoc, deckName):

    cacheLoc = "cardcahe/cardcache.p"

    if os.path.exists(cacheLoc):
        with open(cacheLoc, "rb") as p:
            cardCache = pickle.load(p)
    else:
        cardCache = {}

    with open(fileLoc) as f:
        cardsInDeck = []

        for line in tqdm(f):
            line = line.strip()
            cardCount = re.findall("^([0-9]+)x?", line)
            cardName = line.split(cardCount[0])[1].strip()

            if cardName in cardCache:
                cardDat = cardCache[cardName]

            else:
                print("{} not in cache. searching...".format(cardName))
                searchResults = Card.where(name=cardName).all()

                if len(searchResults) > 0:
                    if (searchSupertypes := searchResults[0].supertypes
                        ) is not None and "Basic" in searchSupertypes:
                        print(
                            "{} will not be printed. use the basic land generator (check readme) instead"
                            .format(cardName))
                    else:
                        if cardCount[0] != "1":
                            print(
                                "warning! BWProxy is singleton only for now. one {} will be printed"
                                .format(cardName))

                        cardDat = searchResults[0]
                        cardCache[cardName] = cardDat
                else:
                    print("warning! {} not found in search".format(cardName))
                    cardDat = None

            cardsInDeck.append(cardDat)

    os.makedirs(os.path.dirname(cacheLoc), exist_ok=True)
    with open(cacheLoc, "wb") as p:
        pickle.dump(cardCache, p)

    return [card for card in cardsInDeck if card is not None]


def makeImage(card, setSymbol):
    cardImg, pen = drawUtil.blankCard()

    # mana cost TODO cleanup and fix phyrexian
    costFont = ImageFont.truetype("MagicSymbols2008.ttf", 60)
    phyrexianFont = ImageFont.truetype("matrixb.ttf", 60)
    xPos = 675
    if card.mana_cost is not None:
        fmtCost = "".join(
            list(filter(lambda c: c not in "{} ", card.mana_cost)))

        for c in fmtCost[::-1]:
            if c in "/P":
                pen.text((xPos, 75),
                         c,
                         font=phyrexianFont,
                         fill="black",
                         anchor="ra")
            else:
                pen.text((xPos, 60),
                         c,
                         font=costFont,
                         fill="black",
                         anchor="ra")
            xPos -= 0 if c == "/" else 20 if c == "P" else 40
    #575 default width for name, default font 60
    nameFont = drawUtil.fitOneLine("matrixb.ttf", card.name, xPos - 100, 60)
    pen.text((70, 85), card.name, font=nameFont, fill="black", anchor="lm")

    # 600 width for typeline with symbol, default font 60
    typeLine = drawUtil.makeTypeLine(card.supertypes, card.types,
                                     card.subtypes)
    typeFont = drawUtil.fitOneLine("matrixb.ttf", typeLine, 540, 60)
    pen.text((70, 530), typeLine, font=typeFont, fill="black", achor="lm")

    if setSymbol is not None:
        cardImg.paste(setSymbol, (620, 520), setSymbol)

    fmtText, textFont = drawUtil.fitMultiLine("MPLANTIN.ttf", card.text, 600,
                                              300, 40)
    pen.text((70, 625), fmtText, font=textFont, fill="black")

    if "Creature" in typeLine or "Planeswalker" in typeLine:
        pen.rectangle([550, 930, 675, 1005],
                      outline="black",
                      fill="white",
                      width=5)

        if "Creature" in typeLine:
            # TODO two-digit p/t
            pt = "{}/{}".format(card.power, card.toughness)
            ptFont = drawUtil.fitOneLine("MPLANTIN.ttf", pt, 85, 60)
            pen.text((570, 970), pt, font=ptFont, fill="black", anchor="lm")

        else:
            loyaltyFont = ImageFont.truetype("MPLANTIN.ttf", 60)
            pen.text((595, 940), card.loyalty, font=loyaltyFont, fill="black")

    proxyFont = ImageFont.truetype("matrixb.ttf", 30)
    pen.text((70, 945),
             "v{}".format(drawUtil.VERSION),
             font=proxyFont,
             fill="black")

    brushFont = ImageFont.truetype("MagicSymbols2008.ttf", 20)
    pen.text((70, 970), "L", font=brushFont, fill="black")

    credFont = ImageFont.truetype("MPLANTIN.ttf", 25)
    pen.text((120, 967), "a11ce.com/BWProxy", font=credFont, fill="black")

    return (card.name, cardImg)


if __name__ == "__main__":
    #print(deckName)
    deckName = sys.argv[1].split(".")[0]
    setSymbol = Image.open(sys.argv[2]).convert("RGBA").resize(
        (60, 60)) if len(sys.argv) > 2 else None

    allCards = loadCards(sys.argv[1], deckName)

    images = [makeImage(card, setSymbol) for card in tqdm(allCards)]

    print(images)
    drawUtil.savePages(images, deckName)
