from mtgsdk import Card
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
import sys
import pickle
import textwrap


def loadCards(fileLoc):
    with open(fileLoc) as f:
        allCards = []
        for line in tqdm(f):
            cardName = line[1:].strip()
            print("searching {}".format(cardName))
            searchResults = Card.where(name=cardName).all()
            if len(searchResults) > 0:
                allCards.append(searchResults[0])
            else:
                print("Card not found: {}!".format(cardName))
    return allCards


def makeImage(card):
    cardImg = Image.new('RGB', size=(750, 1050), color=(255, 255, 255, 0))
    pen = ImageDraw.Draw(cardImg)
    pen.rectangle([50, 50, 700, 1000], outline="black", width=5)
    pen.rectangle([50, 50, 700, 135], outline="black", width=5)
    pen.rectangle([50, 50, 700, 510], outline="black", width=5)
    pen.rectangle([50, 50, 700, 590], outline="black", width=5)
    pen.rectangle([50, 50, 700, 940], outline="black", width=5)
    #50
    nameFontSize = 60
    nameFont = ImageFont.truetype("matrixb.ttf", nameFontSize)
    #500 width for name
    while nameFont.getsize(card.name)[0] > 500:
        nameFontSize -= 10
        nameFont = ImageFont.truetype("matrixb.ttf", nameFontSize)
    costFont = ImageFont.truetype("MagicSymbols2008.ttf", 60)
    pen.text((70, 70), card.name, font=nameFont, fill="black")

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

    typeLine = (" ".join(card.supertypes) +
                " ") if card.supertypes is not None else ""
    typeLine += " ".join(card.types)
    if card.subtypes is not None:
        typeLine += (" - " + " ".join(card.subtypes))

    typeFontSize = 60
    typeFont = ImageFont.truetype("matrixb.ttf", nameFontSize)
    #500 width for name
    while typeFont.getsize(typeLine)[0] > 600:
        typeFontSize -= 10
        typeFont = ImageFont.truetype("matrixb.ttf", typeFontSize)
    pen.text((70, 525), typeLine, font=typeFont, fill="black")

    fmtText = '\n\n'.join([
        '\n'.join(
            textwrap.wrap(line,
                          30,
                          break_long_words=False,
                          replace_whitespace=False))
        for line in card.text.splitlines() if line.strip() != ''
    ])

    textFontSize = 30
    textFont = ImageFont.truetype("LibMono.ttf", textFontSize)
    #500 width for name
    pen.text((70, 625), fmtText, font=textFont, fill="black")

    print(typeLine)

    if "Creature" in typeLine:
        pen.rectangle([550, 930, 675, 1005],
                      outline="black",
                      fill="white",
                      width=5)
        ptFont = ImageFont.truetype("MPLANTIN.ttf", 60)
        pen.text((570, 940), card.power, font=ptFont, fill="black")
        pen.text((600, 940), "/", font=ptFont, fill="black")
        pen.text((615, 940), card.toughness, font=ptFont, fill="black")

    proxyFont = ImageFont.truetype("matrixb.ttf", 30)
    pen.text((70, 950), "PROXY", font=proxyFont, fill="black")

    brushFont = ImageFont.truetype("MagicSymbols2008.ttf", 20)
    pen.text((70, 970), "L", font=brushFont, fill="black")

    credFont = ImageFont.truetype("matrixb.ttf", 30)
    pen.text((115, 970), "a11ce", font=credFont, fill="black")
    return (card.name, cardImg)


if __name__ == "__main__":
    allCards = [card for card in loadCards(sys.argv[1]) if card is not None]
    with open("{}.p".format(sys.argv[1].strip()), "wb") as p:
        pickle.dump(allCards, p)

    #with open("sailist.txt.p", "rb") as p:
    #    allCards = pickle.load(p)
    images = [makeImage(card) for card in allCards]

    #for name, im in images:
    #im.save("sai/{}.png".format(name), "PNG")

    for i in range(0, len(images), 8):
        batch = images[i:i + 8]
        page = Image.new("RGB", size=(3000, 2250), color="white")
        [page.paste(batch[n][1], (750 * n, 0)) for n in range(4)]
        for n in range(4, len(batch)):
            print(batch[n][0])
            page.paste(batch[n][1], (750 * (n - 4), 1125))
        page.save("pages/{}.png".format(i), "PNG")
