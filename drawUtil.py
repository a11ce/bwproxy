from typing import overload
from PIL import Image, ImageDraw, ImageFont, ImageColor
from tqdm import tqdm
import os
import re

import projectConstants as C
from projectTypes import Card, Deck, Flavor, XY, Box  # type: ignore

RgbColor = tuple[int, int, int] | tuple[int, int, int, int]

DEF_BORDER_COLOR = C.FRAME_COLORS["default"]
DEF_BORDER_RGB = ImageColor.getrgb(DEF_BORDER_COLOR)

# Text formatting

specialTextRegex = re.compile(r"\{.+?\}")


def replFunction(m: re.Match[str]):
    t = m.group()
    if t in C.FONT_CODE_POINT:
        return C.FONT_CODE_POINT[t]
    return t


@overload
def printSymbols(text: str) -> str:
    ...


@overload
def printSymbols(text: None) -> None:
    ...


def printSymbols(text: str | None) -> str | None:
    if text is None:
        return None
    # First − is \u2212, which is not in the font but is used in Planeswalker abilities
    # The second is \u002d, the ASCII one
    return specialTextRegex.sub(replFunction, text).replace("−", "-")


def fitOneLine(fontPath: str, text: str, maxWidth: int, fontSize: int):
    """
    Function that tries to fit one line of text in the specified width.
    It starts with the specified font size, and if the text is too long
    it reduces the font size by one and tries again.
    """
    font = ImageFont.truetype(fontPath, fontSize)
    while font.getsize(text)[0] > maxWidth:
        fontSize -= 1
        font = ImageFont.truetype(fontPath, fontSize)
    return font


def fitMultiLine(
    fontPath: str, cardText: str, maxWidth: int, maxHeight: int, fontSize: int
) -> tuple[str, ImageFont.FreeTypeFont]:
    """
    Recursive function that tries to fit multiple lines of text in the specified box.
    It starts with the specified font size, chops the text based on the max width,
    and if the text overflows vertically it reduces the font size by one and tries again.
    """
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
        return (fmtText, font)


# Black frame


def makeFrameStandard(image: Image.Image, hasPTL: bool = False) -> Image.Image:

    pen = ImageDraw.Draw(image)

    STD_BORDER = C.STD_LAYOUT.BORDER
    # Illustration upper border
    pen.rectangle(
        ((0, 0), (C.CARD_H, STD_BORDER.ILLUSTRATION)), outline=DEF_BORDER_COLOR, width=5
    )
    # Type line upper border
    pen.rectangle(
        ((0, 0), (C.CARD_H, STD_BORDER.TYPE_LINE)), outline=DEF_BORDER_COLOR, width=5
    )
    # Rules box upper border
    pen.rectangle(
        ((0, 0), (C.CARD_H, STD_BORDER.RULES_BOX)), outline=DEF_BORDER_COLOR, width=5
    )
    # Other info upper border
    pen.rectangle(
        ((0, 0), (C.CARD_H, STD_BORDER.OTHER)), outline=DEF_BORDER_COLOR, width=5
    )

    if hasPTL:
        pen.rectangle(C.STD_PTL_BOX, outline=DEF_BORDER_COLOR, fill="white", width=5)
    return image


def makeFrameSplit(
    image: Image.Image, isRightSide: bool = False, isFuse: bool = False
) -> Image.Image:

    image = image.transpose(Image.ROTATE_90)
    pen = ImageDraw.Draw(image)
    hstart = C.CARD_V // 2 if isRightSide else 0
    hend = C.CARD_V if isRightSide else C.CARD_V // 2
    # Card border
    pen.rectangle(((hstart, 0), (hend, C.CARD_H)), outline=DEF_BORDER_COLOR, width=5)
    SPLIT_BORDERS = C.SPLIT_LAYOUT.BORDER
    # Illustration upper border
    pen.rectangle(
        ((hstart, 0), (hend, SPLIT_BORDERS.ILLUSTRATION)),
        outline=DEF_BORDER_COLOR,
        width=5,
    )
    # Type line upper border
    pen.rectangle(
        ((hstart, 0), (hend, SPLIT_BORDERS.TYPE_LINE)),
        outline=DEF_BORDER_COLOR,
        width=5,
    )
    # Rules box upper border
    pen.rectangle(
        ((hstart, 0), (hend, SPLIT_BORDERS.RULES_BOX)),
        outline=DEF_BORDER_COLOR,
        width=5,
    )
    # Other info upper border
    pen.rectangle(
        ((hstart, 0), (hend, SPLIT_BORDERS.OTHER)), outline=DEF_BORDER_COLOR, width=5
    )

    # Fuse rectangle
    if isFuse:
        pen.rectangle(
            ((0, SPLIT_BORDERS.FUSE), (C.CARD_V, SPLIT_BORDERS.OTHER)),
            outline=DEF_BORDER_COLOR,
            fill="white",
            width=5,
        )
    return image.transpose(Image.ROTATE_270)


def makeFrameAdventure(image: Image.Image) -> Image.Image:
    pen = ImageDraw.Draw(image)

    ADV_BORDER = C.ADVENTURE_LAYOUT.BORDER
    # Middle divisor
    pen.rectangle(
        ((0, ADV_BORDER.TITLE), (C.CARD_H // 2, C.STD_LAYOUT.BORDER.OTHER)),
        outline=DEF_BORDER_COLOR,
        width=5,
    )
    # Type line (also including Title and rules box)
    pen.rectangle(
        ((0, ADV_BORDER.TYPE_LINE), (C.CARD_H // 2, ADV_BORDER.RULES_BOX)),
        outline=DEF_BORDER_COLOR,
        width=5,
    )
    return image

def makeFrameAftermath(image: Image.Image) -> Image.Image:

    pen = ImageDraw.Draw(image)

    AFT_BORDER = C.AFTERMATH_LAYOUT.BORDER
    # Illustration upper border
    pen.rectangle(
        ((0, 0), (C.CARD_H, AFT_BORDER.ILLUSTRATION)), outline=DEF_BORDER_COLOR, width=5
    )
    # Type line upper border
    pen.rectangle(
        ((0, 0), (C.CARD_H, AFT_BORDER.TYPE_LINE)), outline=DEF_BORDER_COLOR, width=5
    )
    # Rules box upper border
    pen.rectangle(
        ((0, 0), (C.CARD_H, AFT_BORDER.RULES_BOX)), outline=DEF_BORDER_COLOR, width=5
    )
    # Other info upper border
    pen.rectangle(
        ((0, 0), (C.CARD_H, AFT_BORDER.OTHER)), outline=DEF_BORDER_COLOR, width=5
    )
    pen.rectangle(
        ((0, 0), (C.CARD_H, C.CARD_V // 2)), outline=DEF_BORDER_COLOR, width=5
    )

    return image

def makeFrameFlip(image: Image.Image, hasPTL: bool = False) -> Image.Image:

    pen = ImageDraw.Draw(image)

    FLIP_BORDER = C.FLIP_LAYOUT.BORDER
    # Type line upper border
    pen.rectangle(
        ((0, 0), (C.CARD_H, FLIP_BORDER.TYPE_LINE)), outline=DEF_BORDER_COLOR, width=5
    )
    # Rules box upper border
    pen.rectangle(
        ((0, 0), (C.CARD_H, FLIP_BORDER.RULES_BOX)), outline=DEF_BORDER_COLOR, width=5
    )
    # Other info upper border
    pen.rectangle(
        ((0, 0), (C.CARD_H, FLIP_BORDER.OTHER)), outline=DEF_BORDER_COLOR, width=5
    )
    # Illustration upper border
    pen.rectangle(
        ((0, 0), (C.CARD_H, FLIP_BORDER.ILLUSTRATION)), outline=DEF_BORDER_COLOR, width=5
    )
    
    if hasPTL:
        pen.rectangle(C.FLIP_PTL_BOX, outline=DEF_BORDER_COLOR, fill="white", width=5)

    return image


def makeFrame(card: Card, image: Image.Image) -> Image.Image:
    """
    Creates a frame on which we can draw the card,
    and draws the basic card parts on it (one color only)
    """

    if card.layout in ["split", "fuse"]:
        isFuse = card.layout == "fuse"
        image = makeFrameSplit(image=image, isRightSide=False, isFuse=isFuse)
        image = makeFrameSplit(image=image, isRightSide=True, isFuse=isFuse)
    elif card.layout == "aftermath":
        image = makeFrameAftermath(image=image)
        image = makeFrameSplit(image=image, isRightSide=True, isFuse=False)
    elif card.layout == "adventure":
        image = makeFrameStandard(image=image, hasPTL=card.card_faces[0].hasPTL())
        image = makeFrameAdventure(image=image)
    elif card.layout == "flip":
        image = makeFrameFlip(image=image, hasPTL=card.card_faces[0].hasPTL())
        image = image.transpose(Image.ROTATE_180)
        image = makeFrameFlip(image=image, hasPTL=card.card_faces[1].hasPTL())
        image = image.transpose(Image.ROTATE_180)
    else:
        image = makeFrameStandard(image=image, hasPTL=card.hasPTL())
    return image


# Colored frame utility function


def interpolateColor(color1: RgbColor, color2: RgbColor, weight: float) -> RgbColor:
    return tuple(int(a + (weight * (b - a))) for a, b in zip(color1, color2))


def multicolorBlank(colors: list[str], vertical: bool = False) -> Image.Image:
    """
    Creates a template for two-colored card frames,
    with a color shift from the first color to the second
    This template is then used to set the colors in the real frame
    """
    if vertical:
        cardImg = Image.new("RGB", size=C.CARD_SIZE_H, color=C.WHITE)
    else:
        cardImg = Image.new("RGB", size=C.CARD_SIZE, color=C.WHITE)
    pen = ImageDraw.Draw(cardImg)
    imgColors = [ImageColor.getrgb(x) for x in colors]
    if vertical:
        for idx in range(C.CARD_V):
            pen.line(
                [(idx, 0), (idx, C.CARD_H)],
                tuple(interpolateColor(imgColors[0], imgColors[1], idx / C.CARD_V)),
                width=1,
            )
    else:
        for idx in range(C.CARD_H):
            pen.line(
                [(idx, 0), (idx, C.CARD_V)],
                tuple(interpolateColor(imgColors[0], imgColors[1], idx / C.CARD_H)),
                width=1,
            )

    return cardImg


def colorBorders(card: Card, image: Image.Image):
    return image  # TODO
    coloredTemplate = multicolorBlank(card=card)
    (x, y) = CARD_SIZE
    for idx in range(x):
        for idy in range(y):
            if image.getpixel((idx, idy)) == DEF_BORDER_RGB:
                image.putpixel((idx, idy), coloredTemplate.getpixel((idx, idy)))  # type: ignore
    return
    if not isinstance(frameColor, list):
        frameBlank, pen = makeFrame(frameColor=frameColor, card=card)
    elif len(frameColor) > 2:
        frameBlank, pen = makeFrame(frameColor=C.FRAME_COLORS["M"], card=card)
    else:
        frameBlank, pen = makeFrame(frameColor=DEF_BORDER, card=card)
        vertical = card.layout in ["split", "fuse"]
        multiBlank = multicolorBlank(frameColor, vertical=vertical)


# Symbol


def resizeSetSymbol(symbol: Image.Image) -> Image.Image:
    symSize = symbol.size
    scaleFactor = max(symSize[0] / C.SYMBOL_SIZE, symSize[1] / C.SYMBOL_SIZE)
    symbol = symbol.resize(
        size=(int(symSize[0] / scaleFactor), int(symSize[1] / scaleFactor))
    )
    return symbol


def correctSymbolPosition(symbol: Image.Image, position: XY) -> XY:
    symbolSize: XY = symbol.size
    return (
        position[0] + (C.SYMBOL_SIZE - symbolSize[0]) // 2,
        position[1] + (C.SYMBOL_SIZE - symbolSize[1]) // 2,
    )


def pasteSetSymbol(card: Card, image: Image.Image, symbol: Image.Image) -> Image.Image:

    if card.layout in ["split", "fuse"]:
        image = image.transpose(Image.ROTATE_90)
        position = C.SPLIT_SYMBOL_POSITION[0]
    elif card.layout == "aftermath":
        position = C.AFTERMATH_SYMBOL_POSITION
    elif card.layout == "flip":
        position = C.FLIP_SYMBOL_POSITION
    else:
        position = C.STD_SYMBOL_POSITION
    image.paste(
        im=symbol,
        box=correctSymbolPosition(symbol=symbol, position=position),
        mask=symbol,
    )

    if card.layout not in ["split", "fuse", "aftermath", "flip"]:
        return image
    if card.layout in ["split", "fuse"]:
        position = C.SPLIT_SYMBOL_POSITION[1]
    elif card.layout == "aftermath":
        image = image.transpose(Image.ROTATE_90)
        position = C.SPLIT_SYMBOL_POSITION[1]
    elif card.layout == "flip":
        image = image.transpose(Image.ROTATE_180)
        position = C.FLIP_SYMBOL_POSITION

    image.paste(
        im=symbol,
        box=correctSymbolPosition(symbol=symbol, position=position),
        mask=symbol,
    )

    if card.layout in ["split", "fuse", "aftermath"]:
        image = image.transpose(Image.ROTATE_270)
    elif card.layout == "flip":
        image = image.transpose(Image.ROTATE_180)
    return image


# Text
def drawText(
    card: Card,
    image: Image.Image,
    flavorNames: Flavor = {},
    useTextSymbols: bool = True,
) -> Image.Image:

    if card.layout in ["split", "fuse"]:
        isDouble = True
        faceTemplate = "split"
        faces = card.card_faces
        if card.layout == "fuse":
            image = drawFuseText(card=card, image=image)
    elif card.layout == "aftermath":
        isDouble = True
        faceTemplate = "aftermath"
        faces = card.card_faces
    elif card.layout == "adventure":
        isDouble = True
        faceTemplate = "adventure"
        faces = card.card_faces
    elif card.layout == "flip":
        isDouble = True
        faceTemplate = "flip"
        faces = card.card_faces
    else:
        isDouble = False
        faceTemplate = "standard"
        faces = [card]

    faceDistinguisher = ["A", "B"]
    if isDouble:
        for i in range(2):
            face = faces[i]
            faceType = faceTemplate + faceDistinguisher[i]
            image = drawTitleLine(card=face, image=image, type=faceType)
            image = drawTypeLine(card=face, image=image, type=faceType)
            image = drawTextBox(
                card=face, image=image, type=faceType, useTextSymbols=useTextSymbols
            )
            image = drawPTL(card=face, image=image, type=faceType)
            image = drawOther(card=face, image=image, type=faceType)
    else:
        image = drawTitleLine(card=card, image=image, flavorNames=flavorNames, type="standard")
        image = drawTypeLine(card=card, image=image, type="standard")
        image = drawTextBox(
            card=card, image=image, type="standard", useTextSymbols=useTextSymbols
        )
        image = drawPTL(card=card, image=image, type="standard")
        image = drawOther(card=card, image=image, type="standard")
    return image


def drawTitleLine(
    card: Card, image: Image.Image, flavorNames: Flavor = {}, type: str = ""
) -> Image.Image:
    """
    Creates a frame on which we can draw the card,
    and draws the basic card parts on it (one color only)
    """
    if type == "splitA":
        manaAlignRight = C.CARD_V // 2 - C.BORDER
        manaAlignVertical = C.BORDER
        titleAlignLeft = C.BORDER
        titleAlignVertical = C.SPLIT_LAYOUT.FONT_MIDDLE.TITLE
        image = image.transpose(Image.ROTATE_90)
    elif type in ["splitB", "aftermathB"]:
        manaAlignRight = C.CARD_V - C.BORDER
        manaAlignVertical = C.BORDER
        titleAlignLeft = C.CARD_V // 2 + C.BORDER
        titleAlignVertical = C.SPLIT_LAYOUT.FONT_MIDDLE.TITLE
        image = image.transpose(Image.ROTATE_90)
    elif type == "adventureB":
        manaAlignRight = C.CARD_H // 2 - C.BORDER
        manaAlignVertical = C.ADVENTURE_LAYOUT.BORDER.TITLE + C.BORDER
        titleAlignLeft = C.BORDER
        titleAlignVertical = C.ADVENTURE_LAYOUT.FONT_MIDDLE.TITLE
    else:
        manaAlignRight = C.CARD_H - C.BORDER
        manaAlignVertical = C.BORDER
        titleAlignLeft = C.BORDER
        titleAlignVertical = C.STD_LAYOUT.FONT_MIDDLE.TITLE

    if type == "flipB":
        image = image.transpose(Image.ROTATE_180)

    pen = ImageDraw.Draw(image)
    titleFont = ImageFont.truetype(font="MPLANTIN.ttf", size=C.TITLE_FONT_SIZE)
    xPos = manaAlignRight
    manaCost = printSymbols(card.mana_cost)
    for c in manaCost[::-1]:
        pen.text(
            (xPos, manaAlignVertical), text=c, font=titleFont, fill="black", anchor="ra"
        )
        xPos -= titleFont.getsize(c)[0]

    displayName = flavorNames[card.name] if card.name in flavorNames else card.name
    if card.layout in ["transform", "modal_dfc"]:
        displayName = f"{C.FONT_CODE_POINT[card.face]} {displayName}"

    nameFont = fitOneLine(
        fontPath="matrixb.ttf",
        text=displayName,
        maxWidth=xPos - titleAlignLeft - 2 * C.BORDER,
        fontSize=C.TITLE_FONT_SIZE,
    )
    pen.text(
        (
            titleAlignLeft,
            titleAlignVertical,
        ),
        text=displayName,
        font=nameFont,
        fill="black",
        anchor="lm",
    )
    if card.name in flavorNames and card.layout not in [
        "split",
        "fuse",
        "aftermath",
        "flip",
    ]:
        trueNameFont = ImageFont.truetype(font="matrixb.ttf", size=C.TEXT_FONT_SIZE)
        pen.text(
            (C.CARD_H // 2, C.STD_LAYOUT.BORDER.ILLUSTRATION + C.BORDER),
            card.name,
            font=trueNameFont,
            fill="black",
            anchor="ma",
        )

    if type in ["splitA", "splitB", "aftermathB"]:
        image = image.transpose(Image.ROTATE_270)
    elif type == "flipB":
        image = image.transpose(Image.ROTATE_180)

    return image


def drawTypeLine(card: Card, image: Image.Image, type: str = "") -> Image.Image:
    if type == "splitA":
        alignLeft = C.BORDER
        alignVertical = C.SPLIT_LAYOUT.FONT_MIDDLE.TYPE_LINE
        maxWidth = C.CARD_V // 2 - 3 * C.BORDER - C.SYMBOL_SIZE
        image = image.transpose(Image.ROTATE_90)
    elif type in ["splitB", "aftermathB"]:
        alignLeft = C.CARD_V // 2 + C.BORDER
        alignVertical = C.SPLIT_LAYOUT.FONT_MIDDLE.TYPE_LINE
        maxWidth = C.CARD_V // 2 - 3 * C.BORDER - C.SYMBOL_SIZE
        image = image.transpose(Image.ROTATE_90)
    elif type == "adventureB":
        alignLeft = C.BORDER
        alignVertical = C.ADVENTURE_LAYOUT.FONT_MIDDLE.TYPE_LINE
        maxWidth = C.CARD_H // 2 - 2 * C.BORDER
    elif type == "aftermathA":
        alignLeft = C.BORDER
        alignVertical = C.AFTERMATH_LAYOUT.FONT_MIDDLE.TYPE_LINE
        maxWidth = C.CARD_H - 3 * C.BORDER - C.SYMBOL_SIZE
    elif type in ["flipA", "flipB"]:
        alignLeft = C.BORDER
        alignVertical = C.FLIP_LAYOUT.FONT_MIDDLE.TYPE_LINE
        maxWidth = C.CARD_H - 3 * C.BORDER - C.SYMBOL_SIZE
    else:
        alignLeft = C.BORDER
        alignVertical = C.STD_LAYOUT.FONT_MIDDLE.TYPE_LINE
        maxWidth = C.CARD_H - 3 * C.BORDER - C.SYMBOL_SIZE

    if type == "flipB":
        image = image.transpose(Image.ROTATE_180)

    pen = ImageDraw.Draw(image)

    typeFont = fitOneLine(
        fontPath="matrixb.ttf",
        text=card.type_line,
        maxWidth=maxWidth,
        fontSize=C.TYPE_FONT_SIZE,
    )
    pen.text(
        (alignLeft, alignVertical),
        text=card.type_line,
        font=typeFont,
        fill="black",
        anchor="lm",
    )

    if type in ["splitA", "splitB", "aftermathB"]:
        image = image.transpose(Image.ROTATE_270)
    elif type == "flipB":
        image = image.transpose(Image.ROTATE_180)

    return image


def drawTextBox(
    card: Card, image: Image.Image, type: str = "", useTextSymbols: bool = True
) -> Image.Image:
    cardText = f"{card.color_indicator_reminder_text}{card.oracle_text}"
    if useTextSymbols:
        cardText = printSymbols(cardText)

    if type == "splitA":
        alignLeft = C.BORDER
        alignVertical = C.SPLIT_LAYOUT.BORDER.RULES_BOX + C.BORDER
        maxWidth = C.CARD_V // 2 - 2 * C.BORDER
        maxHeight = (
            C.SPLIT_LAYOUT.SIZE.RULES_BOX_FUSE
            if card.layout == "fuse"
            else C.SPLIT_LAYOUT.SIZE.RULES_BOX - 2 * C.BORDER
        )
        image = image.transpose(Image.ROTATE_90)
    elif type in ["splitB", "aftermathB"]:
        alignLeft = C.CARD_V // 2 + C.BORDER
        alignVertical = C.SPLIT_LAYOUT.BORDER.RULES_BOX + C.BORDER
        maxWidth = C.CARD_V // 2 - 2 * C.BORDER
        maxHeight = (
            C.SPLIT_LAYOUT.SIZE.RULES_BOX_FUSE
            if card.layout == "fuse"
            else C.SPLIT_LAYOUT.SIZE.RULES_BOX
        ) - 2 * C.BORDER
        image = image.transpose(Image.ROTATE_90)
    elif type == "adventureA":
        alignLeft = C.CARD_H // 2 + C.BORDER
        alignVertical = C.STD_LAYOUT.BORDER.RULES_BOX + C.BORDER
        maxWidth = C.CARD_H // 2 - 2 * C.BORDER
        maxHeight = C.STD_LAYOUT.SIZE.RULES_BOX - 2 * C.BORDER
    elif type == "adventureB":
        alignLeft = C.BORDER
        alignVertical = C.ADVENTURE_LAYOUT.BORDER.RULES_BOX + C.BORDER
        maxWidth = C.CARD_H // 2 - 2 * C.BORDER
        maxHeight = C.ADVENTURE_LAYOUT.SIZE.RULES_BOX - 2 * C.BORDER
    elif type == "aftermathA":
        alignLeft = C.BORDER
        alignVertical = C.AFTERMATH_LAYOUT.BORDER.RULES_BOX + C.BORDER
        maxWidth = C.CARD_H - 2 * C.BORDER
        maxHeight = C.AFTERMATH_LAYOUT.SIZE.RULES_BOX - 2 * C.BORDER
    elif type in ["flipA", "flipB"]:
        alignLeft = C.BORDER
        alignVertical = C.FLIP_LAYOUT.BORDER.RULES_BOX + C.BORDER
        maxWidth = C.CARD_H - 2 * C.BORDER
        maxHeight = C.FLIP_LAYOUT.SIZE.RULES_BOX - 2 * C.BORDER
    else:
        alignLeft = C.BORDER
        alignVertical = C.STD_LAYOUT.BORDER.RULES_BOX + C.BORDER
        maxWidth = C.CARD_H - 2 * C.BORDER
        maxHeight = C.STD_LAYOUT.SIZE.RULES_BOX - 2 * C.BORDER

    if type == "flipB":
        image = image.transpose(Image.ROTATE_180)

    pen = ImageDraw.Draw(image)

    (fmtText, textFont) = fitMultiLine(
        fontPath="MPLANTIN.ttf",
        cardText=cardText,
        maxWidth=maxWidth,
        maxHeight=maxHeight,
        fontSize=C.TEXT_FONT_SIZE,
    )
    pen.text(
        (alignLeft, alignVertical),
        text=fmtText,
        font=textFont,
        fill="black",
        anchor="la",
    )

    if type in ["splitA", "splitB", "aftermathB"]:
        image = image.transpose(Image.ROTATE_270)
    elif type == "flipB":
        image = image.transpose(Image.ROTATE_180)

    return image


def drawFuseText(card: Card, image: Image.Image) -> Image.Image:
    if not card.layout == "fuse":
        return image
    image = image.transpose(Image.ROTATE_90)
    pen = ImageDraw.Draw(image)

    typeFont = fitOneLine(
        fontPath="MPLANTIN.ttf",
        text=card.fuse_text,
        maxWidth=C.CARD_V - 2 * C.BORDER,
        fontSize=C.TEXT_FONT_SIZE,
    )
    pen.text(
        (C.BORDER, C.SPLIT_LAYOUT.FONT_MIDDLE.FUSE),
        text=card.fuse_text,
        font=typeFont,
        fill="black",
        anchor="lm",
    )
    
    image = image.transpose(Image.ROTATE_270)

    return image


def drawPTL(card: Card, image: Image.Image, type: str = "") -> Image.Image:
    if card.hasPT():
        ptl = f"{card.power}/{card.toughness}"
    elif card.hasL():
        ptl = card.loyalty
    else:
        return image

    if type in ["flipA", "flipB"]:
        ptlBox = C.FLIP_PTL_BOX
    else:
        ptlBox = C.STD_PTL_BOX

    if type == "flipB":
        image = image.transpose(Image.ROTATE_180)

    pen = ImageDraw.Draw(image)

    ptlFont = fitOneLine(
        fontPath="MPLANTIN.ttf",
        text=ptl,
        maxWidth=ptlBox[1][0] - ptlBox[0][0] - 2 * C.BORDER,
        fontSize=C.TITLE_FONT_SIZE,
    )

    pen.text(
        C.ptlTextPosition(ptlBox), text=ptl, font=ptlFont, fill="black", anchor="mm"
    )

    if type == "flipB":
        image = image.transpose(Image.ROTATE_180)

    return image


def drawOther(card: Card, image: Image.Image, type: str = "") -> Image.Image:

    if type == "splitA":
        alignLeft = C.BORDER
        alignVertical = C.CARD_H - C.STD_LAYOUT.SIZE.OTHER // 2
        image = image.transpose(Image.ROTATE_90)
    elif type in ["splitB", "aftermathB"]:
        alignLeft = C.CARD_V // 2 + C.BORDER
        alignVertical = C.CARD_H - C.STD_LAYOUT.SIZE.OTHER // 2
        image = image.transpose(Image.ROTATE_90)
    elif type == "adventureB":
        return image
    elif type == "aftermathA":
        alignLeft = C.BORDER
        alignVertical = C.CARD_V // 2 - C.STD_LAYOUT.SIZE.OTHER // 2
    elif type in ["flipA", "flipB"]:
        alignLeft = C.BORDER
        alignVertical = C.FLIP_LAYOUT.BORDER.OTHER + C.FLIP_LAYOUT.SIZE.OTHER // 2
    else:
        alignLeft = C.BORDER
        alignVertical = C.CARD_V - C.STD_LAYOUT.SIZE.OTHER // 2

    if type == "flipB":
        image = image.transpose(Image.ROTATE_180)

    pen = ImageDraw.Draw(image)

    credFont = ImageFont.truetype("MPLANTIN.ttf", size=C.OTHER_FONT_SIZE)
    pen.text(
        (alignLeft, alignVertical),
        text=C.CREDITS,
        font=credFont,
        fill="black",
        anchor="lm",
    )
    credLength = pen.textlength(text=C.CREDITS + "   ", font=credFont)

    proxyFont = ImageFont.truetype("matrixb.ttf", size=C.OTHER_FONT_SIZE * 4 // 3)
    pen.text(
        (alignLeft + credLength, alignVertical - 5),
        text=f"v{C.VERSION}",
        font=proxyFont,
        fill="black",
        anchor="lm",
    )
    

    if type in ["splitA", "splitB", "aftermathB"]:
        image = image.transpose(Image.ROTATE_270)
    elif type == "flipB":
        image = image.transpose(Image.ROTATE_180)

    return image


# Draw card from beginning to end


def drawCard(
    card: Card,
    isColored: bool = False,
    symbol: Image.Image | None = None,
    flavorNames: Flavor = {},
    useTextSymbols: bool = True,
) -> Image.Image:
    """
    Creates the card frame, and gives it the color gradient effect if it is two colors
    """

    image = Image.new("RGB", size=C.CARD_SIZE, color=C.WHITE)
    pen = ImageDraw.Draw(image)
    # Card border
    pen.rectangle(((0, 0), C.CARD_SIZE), outline=DEF_BORDER_COLOR, width=5)

    image = makeFrame(card=card, image=image)
    if isColored:
        image = colorBorders(card=card, image=image)
    if symbol is not None:
        image = pasteSetSymbol(card=card, image=image, symbol=symbol)
    image = drawText(
        card=card, image=image, flavorNames=flavorNames, useTextSymbols=useTextSymbols
    )

    return image
    if not isinstance(frameColor, list):
        frameBlank, pen = makeFrame(frameColor=frameColor, card=card)
    elif len(frameColor) > 2:
        frameBlank, pen = makeFrame(frameColor=C.FRAME_COLORS["M"], card=card)
    else:
        frameBlank, pen = makeFrame(frameColor=DEF_BORDER, card=card)
        vertical = card.layout in ["split", "fuse"]
        multiBlank = multicolorBlank(frameColor, vertical=vertical)

        (x, y) = CARD_SIZE_H if vertical else CARD_SIZE
        for idx in range(x):
            for idy in range(y):
                if frameBlank.getpixel((idx, idy)) == DEF_BORDER_RGB:
                    frameBlank.putpixel((idx, idy), multiBlank.getpixel((idx, idy)))  # type: ignore

    return frameBlank, pen


# Paging


def batchSpacing(n: int, batchSize: tuple[int, int], pageSize: tuple[int, int]):
    maxH = pageSize[0] - (C.CARD_DISTANCE + (C.CARD_H + C.CARD_DISTANCE) * batchSize[0])
    maxV = pageSize[1] - (C.CARD_DISTANCE + (C.CARD_V + C.CARD_DISTANCE) * batchSize[1])
    return (
        maxH // 2 + C.CARD_DISTANCE + (C.CARD_H + C.CARD_DISTANCE) * (n % batchSize[0]),
        maxV // 2
        + C.CARD_DISTANCE
        + (C.CARD_V + C.CARD_DISTANCE) * (n // batchSize[0]),
    )


def savePages(images: list[Image.Image], deckName: str):
    os.makedirs(os.path.dirname(f"pages/{deckName}/"), exist_ok=True)
    batchSize = (3, 3)
    batchNum = batchSize[0] * batchSize[1]

    for i in tqdm(range(0, len(images), batchNum)):
        pageSize = C.LETTER_PAPER
        batch = images[i : i + batchNum]
        page = Image.new("RGB", size=pageSize, color="white")
        for n in range(len(batch)):
            page.paste(batch[n], batchSpacing(n, batchSize, pageSize))

        page.save(f"pages/{deckName}/{i // batchNum}.png", "PNG")
