from PIL import Image, ImageDraw, ImageFont
import os
from tqdm import tqdm

VERSION = "1.3"


def blankCard():
    cardImg = Image.new('RGB', size=(750, 1050), color=(255, 255, 255, 0))
    pen = ImageDraw.Draw(cardImg)
    pen.rectangle([50, 50, 700, 1000], outline="black", width=5)
    pen.rectangle([50, 50, 700, 135], outline="black", width=5)
    pen.rectangle([50, 50, 700, 510], outline="black", width=5)
    pen.rectangle([50, 50, 700, 590], outline="black", width=5)
    pen.rectangle([50, 50, 700, 940], outline="black", width=5)
    return cardImg, pen


def fitOneLine(fontPath, text, maxWidth, fontSize):
    font = ImageFont.truetype(fontPath, fontSize)
    while font.getsize(text)[0] > maxWidth:
        fontSize -= 1
        font = ImageFont.truetype(fontPath, fontSize)
    return font


def makeTypeLine(supertypes, types, subtypes):
    typeLine = (" ".join(supertypes) + " ") if supertypes is not None else ""
    typeLine += (" ".join(types)) if types is not None else ""
    typeLine += (" - " + " ".join(subtypes)) if subtypes is not None else ""
    return typeLine


def fitMultiLine(fontPath, cardText, maxWidth, maxHeight, fontSize):
    # the terminology here gets weird so to simplify:
    # a rule is a single line of oracle text.
    #       ex: Smuggler's Copter has 3 rules.
    # line means a printed line. a rule may have multiple lines.

    font = ImageFont.truetype(fontPath, fontSize)
    fmtRules = []

    for rule in cardText.split("\n"):
        ruleLines = []
        curLine = ""
        for word in rule.split(" "):
            if font.getsize(curLine + " " + word)[0] > maxWidth:
                ruleLines.append(curLine)
                curLine = word + " "
            else:
                curLine += word + " "
        ruleLines.append(curLine)
        fmtRules.append("\n".join(ruleLines))

    fmtText = "\n\n".join(fmtRules)

    if font.getsize(fmtText)[1] * len(fmtText.split("\n")) > maxHeight:
        return fitMultiLine(fontPath, cardText, maxWidth, maxHeight,
                            fontSize - 1)
    else:
        return fmtText, font


def savePages(images, deckName):
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
