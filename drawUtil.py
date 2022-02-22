from PIL import Image, ImageDraw, ImageFont, ImageColor
import os
from tqdm import tqdm

VERSION = "1.5"

"""
TODO: Split / Fuse / Flip / Adventure frames (Maybe also Class, Sagas and Leveler?)
Better Double-Faced card handler (front/back face symbols, add both to the file)
Better search functionality:
* searching "Likeness of the Seeker" results in "Azusa's Many Journeys"
* seaching "Alive" results in "Buried Alive" (should be "Alive // Well")
* searching "Endbringer" results in "Shauku, Endbringer"
Replace magic numbers (750, 1050...) with constants
Add options for A4 and letter paper
Better mana symbols, both in cost and in text
(should be in the new font file, only problem is Tamiyo, Compleated Sage)
Color indicator in text
Tested searching for Failure // Comply via api, Failure is the first result
"""

# MID basics plus similar yellow-white
FRAME_COLORS = {
    "White": "#fcf4a3",
    "Blue": "#127db4",
    "Black": "#692473",
    "Red": "#e13c32",
    "Green": "#0f7846",
    "Gold": "#d4af37"
}

RgbColor = tuple[int, int, int] | tuple[int, int, int, int]

# https://gist.github.com/weihanglo/1e754ec47fdd683a42fdf6a272904535
def interpolate(f_co, t_co, interval):
    det_co = [(t - f) / interval for f, t in zip(f_co, t_co)]
    for i in range(interval):
        yield [round(f + det * i) for f, det in zip(f_co, det_co)]


def interpolateColor(color1: RgbColor, color2: RgbColor, weight: float) -> RgbColor:
    return tuple(int(a + (weight * (b - a))) for a, b in zip(color1, color2))


def multicolorBlank(colors: list[str]) -> Image.Image:
    cardImg = Image.new('RGB', size=(750, 1050), color=(255, 255, 255, 0))
    imgColors = [ImageColor.getrgb(x) for x in colors]
    pen = ImageDraw.Draw(cardImg)
    for idx in range(750):
        pen.line(
            [(idx, 0), (idx, 1050)],
            tuple(interpolateColor(imgColors[0], imgColors[1], idx / 750)),
            width=1
        )

    return cardImg


def makeFrame(frameColor: str = "black") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    cardImg = Image.new('RGB', size=(750, 1050), color=(255, 255, 255, 0))
    pen = ImageDraw.Draw(cardImg)
    pen.rectangle((50, 50, 700, 1000), outline=frameColor, width=5)
    pen.rectangle((50, 50, 700, 135), outline=frameColor, width=5)
    pen.rectangle((50, 50, 700, 510), outline=frameColor, width=5)
    pen.rectangle((50, 50, 700, 590), outline=frameColor, width=5)
    pen.rectangle((50, 50, 700, 940), outline=frameColor, width=5)
    return cardImg, pen


def blankCard(frameColor: str | list[str] = "black"):

    if not isinstance(frameColor, list):
        return makeFrame(frameColor)

    if len(frameColor) > 2:
        return makeFrame(FRAME_COLORS["Gold"])

    frameBlank, pen = makeFrame("black")
    multiBlank = multicolorBlank(frameColor)

    for idx in range(750):
        for idy in range(1050):
            if frameBlank.getpixel((idx, idy)) == (0, 0, 0):
                frameBlank.putpixel((idx, idy), multiBlank.getpixel((idx, idy)))

    return frameBlank, pen


def fitOneLine(fontPath, text, maxWidth, fontSize):
    font = ImageFont.truetype(fontPath, fontSize)
    while font.getsize(text)[0] > maxWidth:
        fontSize -= 1
        font = ImageFont.truetype(fontPath, fontSize)
    return font


def makeTypeLine(supertypes: list[str] | None, types: list[str] | None, subtypes: list[str] | None) -> str:
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
        return fitMultiLine(fontPath, cardText, maxWidth, maxHeight, fontSize - 1)
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
