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

    pickleLoc = "cardcache/{}.p".format(deckName)

    if os.path.exists(pickleLoc):
        with open(pickleLoc, "rb") as p:
            allCards = pickle.load(p)
    else:
        with open(fileLoc) as f:
            allCards = []

            for line in tqdm(f):
                line = line.strip()
                cardCount = re.findall("^([0-9]+)x?", line)
                cardName = line.split(cardCount[0])[1].strip()

                print("searching {}".format(cardName))
                searchResults = Card.where(name=cardName).all()

                if len(searchResults) > 0:

                    if (searchSupertypes := searchResults[0].supertypes
                        ) is not None and "Basic" in searchSupertypes:
                        print(
                            "{} will not be printed. use the basic land generator (coming soon) instead!"
                            .format(cardName))

                    else:
                        if cardCount[0] != "1":
                            print(
                                "warning! only one {} will be printed".format(
                                    cardName))
                        allCards.append(searchResults[0])
                else:
                    print("Card not found: {}!".format(cardName))

        os.makedirs(os.path.dirname(pickleLoc), exist_ok=True)
        with open(pickleLoc, "wb") as p:
            pickle.dump(allCards, p)

    return [card for card in allCards if card is not None]


def makeImage(card):
    # TODO figure out sagas
    cardImg, pen = drawUtil.blankCard()

    #500 width for name, default font 60
    nameFont = drawUtil.fitOneLine("matrixb.ttf", card.name, 500, 60)
    pen.text((70, 70), card.name, font=nameFont, fill="black")

    # TODO dynamic name width for long names/costs
    # mana cost TODO cleanup and fix phyrexian
    costFont = ImageFont.truetype("MagicSymbols2008.ttf", 60)
    if card.mana_cost is not None:
        fmtCost = "".join(
            list(filter(lambda c: c not in "{} ", card.mana_cost)))
        xPos = 675
        for c in fmtCost[::-1]:
            if c in "/P":
                pen.text((xPos, 75),
                         c,
                         font=nameFont,
                         fill="black",
                         anchor="ra")
            else:
                pen.text((xPos, 60),
                         c,
                         font=costFont,
                         fill="black",
                         anchor="ra")
            xPos -= 0 if c == "/" else 20 if c == "P" else 40

    # 600 width for typeline, default font 60
    typeLine = drawUtil.makeTypeLine(card.supertypes, card.types,
                                     card.subtypes)
    typeFont = drawUtil.fitOneLine("matrixb.ttf", typeLine, 600, 60)
    pen.text((70, 525), typeLine, font=typeFont, fill="black")

    # TODO  proportional font
    fmtText, textFont = drawUtil.fitMultiLine("LibMono.ttf", card.text, 600,
                                              275, 30)
    pen.text((70, 625), fmtText, font=textFont, fill="black")

    # TODO planeswalker special cases
    if "Creature" in typeLine:
        pen.rectangle([550, 930, 675, 1005],
                      outline="black",
                      fill="white",
                      width=5)
        # TODO two-digit p/t
        ptFont = ImageFont.truetype("MPLANTIN.ttf", 60)
        pen.text((570, 940), card.power, font=ptFont, fill="black")
        pen.text((600, 940), "/", font=ptFont, fill="black")
        pen.text((615, 940), card.toughness, font=ptFont, fill="black")

    proxyFont = ImageFont.truetype("matrixb.ttf", 30)
    pen.text((70, 950), "BWPROXY 1.0", font=proxyFont, fill="black")

    brushFont = ImageFont.truetype("MagicSymbols2008.ttf", 20)
    pen.text((70, 970), "L", font=brushFont, fill="black")

    credFont = ImageFont.truetype("matrixb.ttf", 30)
    pen.text((115, 970), "a11ce", font=credFont, fill="black")

    return (card.name, cardImg)


def savePages(cardImages, deckName):
    os.makedirs(os.path.dirname("pages/{}/".format(deckName)), exist_ok=True)
    for i in tqdm(range(0, len(images), 8)):
        batch = images[i:i + 8]
        page = Image.new("RGB", size=(3000, 2250), color="white")
        [
            page.paste(batch[n][1], (750 * n, 0))
            for n in range(min(4, len(batch)))
        ]
        for n in range(4, len(batch)):
            #print(batch[n][0])
            page.paste(batch[n][1], (750 * (n - 4), 1125))

        page.save("pages/{}/{}.png".format(deckName, i), "PNG")


if __name__ == "__main__":
    #print(deckName)
    deckName = sys.argv[1].split(".")[0]

    allCards = loadCards(sys.argv[1], deckName)

    images = [makeImage(card) for card in tqdm(allCards)]

    savePages(images, deckName)
