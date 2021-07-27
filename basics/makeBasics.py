from PIL import Image, ImageDraw, ImageFont
import sys
sys.path.append('../')
import drawUtil


def makeBlankLand(cardName):

    cardImg = Image.new('RGB', size=(750, 1050), color=(255, 255, 255, 0))
    pen = ImageDraw.Draw(cardImg)
    pen.rectangle([50, 50, 700, 1000], outline="black", width=5)
    pen.rectangle([50, 50, 700, 135], outline="black", width=5)
    pen.rectangle([50, 50, 700, 215], outline="black", width=5)
    pen.rectangle([50, 50, 700, 940], outline="black", width=5)

    #500 width for name, default font 60
    nameFont = drawUtil.fitOneLine("matrixb.ttf", cardName, 500, 60)
    pen.text((70, 70), cardName, font=nameFont, fill="black")

    typeLine = "Basic Land - {}".format(cardName)
    typeFont = drawUtil.fitOneLine("matrixb.ttf", typeLine, 600, 40)
    pen.text((70, 170), typeLine, font=typeFont, fill="black", anchor="lm")

    proxyFont = ImageFont.truetype("matrixb.ttf", 30)
    pen.text((70, 945),
             "v{}".format(drawUtil.VERSION),
             font=proxyFont,
             fill="black")

    brushFont = ImageFont.truetype("MagicSymbols2008.ttf", 20)
    pen.text((70, 970), "L", font=brushFont, fill="black")

    credFont = ImageFont.truetype("../MPLANTIN.ttf", 25)
    pen.text((120, 967), "a11ce.com/BWProxy", font=credFont, fill="black")

    return pen, cardImg


def makeSymbolLand(cardName):
    pen, img = makeBlankLand(cardName)
    symbol = Image.open(
        "symbols/{}.png".format(cardName))  #.resize((600, 600))

    img.paste(symbol, (75, 260), symbol)

    return img


if __name__ == "__main__":

    cards = [(land, makeSymbolLand(land))
             for land in ["Forest", "Mountain", "Swamp", "Island", "Plains"]
             for _ in range(8)]

    drawUtil.savePages(cards, "symbolLands")

    cards = [(land, makeBlankLand(land)[1])
             for land in ["Forest", "Mountain", "Swamp", "Island", "Plains"]
             for _ in range(8)]

    drawUtil.savePages(cards, "blankLands")
