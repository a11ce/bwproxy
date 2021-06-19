from PIL import Image, ImageDraw, ImageFont


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
