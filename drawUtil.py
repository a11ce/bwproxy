from PIL import Image, ImageDraw, ImageFont, ImageColor
import os
from tqdm import tqdm

import projectConstants as C
from projectTypes import Card, Deck, Flavor  # type: ignore

RgbColor = tuple[int, int, int] | tuple[int, int, int, int]

CARD_SIZE = C.MTG_CARD_SIZE
CARD_H = CARD_SIZE[0]
CARD_V = CARD_SIZE[1]
DEF_BORDER = C.FRAME_COLORS["default"]
DEF_BORDER_RGB = ImageColor.getrgb(DEF_BORDER)
CARD_DISTANCE = C.CARD_DISTANCE
BORDER = C.BORDER_DISTANCE
STD_SYM_SIZE = C.STD_LAYOUT.SIZE.SYMBOL


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


def resizeSetSymbol(setSymbol: Image.Image):
    STD_SYM_SIZE = C.STD_LAYOUT.SIZE.SYMBOL

    symSize = setSymbol.size
    scaleFactor = max(symSize[0] / STD_SYM_SIZE, symSize[1] / STD_SYM_SIZE)
    setSymbol = setSymbol.resize(
        size=(int(symSize[0] / scaleFactor), int(symSize[1] / scaleFactor))
    )
    return setSymbol


def interpolateColor(color1: RgbColor, color2: RgbColor, weight: float) -> RgbColor:
    return tuple(int(a + (weight * (b - a))) for a, b in zip(color1, color2))


def multicolorBlank(colors: list[str], vertical: bool = False) -> Image.Image:
    """
    Creates a template for two-colored card frames,
    with a color shift from the first color to the second
    This template is then used to set the colors in the real frame
    """
    cardImg = Image.new("RGB", size=C.MTG_CARD_SIZE, color=C.WHITE)
    pen = ImageDraw.Draw(cardImg)
    imgColors = [ImageColor.getrgb(x) for x in colors]
    if vertical:
        for idy in range(CARD_V):
            pen.line(
                [(0, idy), (CARD_H, idy)],
                tuple(interpolateColor(imgColors[0], imgColors[1], idy / CARD_V)),
                width=1,
            )
    else:
        for idx in range(CARD_H):
            pen.line(
                [(idx, 0), (idx, CARD_V)],
                tuple(interpolateColor(imgColors[0], imgColors[1], idx / CARD_H)),
                width=1,
            )

    return cardImg


def makeFrameStandard(
    pen: ImageDraw.ImageDraw, frameColor: str = DEF_BORDER, hasPTL: bool = False
) -> None:
    STD_BORDERS = C.STD_LAYOUT.BORDER
    # Illustration upper border
    pen.rectangle(
        ((0, 0), (CARD_H, STD_BORDERS.ILLUSTRATION)), outline=frameColor, width=5
    )
    # Type line upper border
    pen.rectangle(
        ((0, 0), (CARD_H, STD_BORDERS.TYPE_LINE)), outline=frameColor, width=5
    )
    # Rules box upper border
    pen.rectangle(
        ((0, 0), (CARD_H, STD_BORDERS.RULES_BOX)), outline=frameColor, width=5
    )
    # Other info upper border
    pen.rectangle(((0, 0), (CARD_H, STD_BORDERS.OTHER)), outline=frameColor, width=5)
    if hasPTL:
        pen.rectangle(C.STD_PT_BOX, outline=frameColor, fill="white", width=5)
    return


def makeFrame(frameColor: str, card: Card) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    """
    Creates a frame on which we can draw the card,
    and draws the basic card parts on it (one color only)
    """
    cardImg = Image.new("RGB", size=C.MTG_CARD_SIZE, color=C.WHITE)
    pen = ImageDraw.Draw(cardImg)
    # Card border
    pen.rectangle(((0, 0), CARD_SIZE), outline=frameColor, width=5)

    makeFrameStandard(pen, frameColor, card.hasPTL())
    return (cardImg, pen)


def blankCard(
    frameColor: str | list[str], card: Card, setSymbol: Image.Image | None = None
):
    """
    Creates the card frame, and gives it the color gradient effect if it is two colors
    """

    if not isinstance(frameColor, list):
        frameBlank, pen = makeFrame(frameColor=frameColor, card=card)
    elif len(frameColor) > 2:
        frameBlank, pen = makeFrame(frameColor=C.FRAME_COLORS["M"], card=card)
    else:
        frameBlank, pen = makeFrame(frameColor=DEF_BORDER, card=card)
        multiBlank = multicolorBlank(frameColor)

        for idx in range(CARD_H):
            for idy in range(CARD_V):
                if frameBlank.getpixel((idx, idy)) == DEF_BORDER_RGB:
                    frameBlank.putpixel((idx, idy), multiBlank.getpixel((idx, idy)))  # type: ignore

    if setSymbol is not None:
        symbolPosition = C.STD_SYMBOL_POSITION
        symbolSize = setSymbol.size
        symbolPosition = (
            symbolPosition[0] + (STD_SYM_SIZE - symbolSize[0]) // 2,
            symbolPosition[1] + (STD_SYM_SIZE - symbolSize[1]) // 2,
        )
        frameBlank.paste(setSymbol, symbolPosition, setSymbol)

    return frameBlank, pen


def drawTitleLine(
    pen: ImageDraw.ImageDraw, card: Card, manaCost: str, flavorNames: Flavor = {}
):
    font = ImageFont.truetype(font="MPLANTIN.ttf", size=C.TITLE_FONT_SIZE)
    xPos = CARD_H - BORDER
    for c in manaCost[::-1]:
        pen.text((xPos, BORDER), text=c, font=font, fill="black", anchor="ra")
        xPos -= font.getsize(c)[0]

    displayName = flavorNames[card.name] if card.name in flavorNames else card.name
    if card.layout in ["transform", "modal_dfc"]:
        displayName = f"{C.FONT_CODE_POINT[card.face]} {displayName}"

    nameFont = fitOneLine(
        fontPath="matrixb.ttf",
        text=displayName,
        maxWidth=xPos - 3 * BORDER,
        fontSize=C.TITLE_FONT_SIZE,
    )
    pen.text(
        (
            BORDER,
            C.STD_LAYOUT.FONT_MIDDLE.TITLE,
        ),
        text=displayName,
        font=nameFont,
        fill="black",
        anchor="lm",
    )
    if card.name in flavorNames:
        trueNameFont = ImageFont.truetype(font="matrixb.ttf", size=C.TEXT_FONT_SIZE)
        pen.text(
            (CARD_H // 2, C.STD_LAYOUT.BORDER.ILLUSTRATION + BORDER),
            card.name,
            font=trueNameFont,
            fill="black",
            anchor="ma",
        )


def drawTypeLine(pen: ImageDraw.ImageDraw, card: Card):
    # 600 width for typeline with symbol, default font 60
    typeFont = fitOneLine(
        "matrixb.ttf",
        card.type_line,
        CARD_H - 3 * BORDER - STD_SYM_SIZE,
        C.TITLE_FONT_SIZE,
    )
    pen.text(
        (BORDER, C.STD_LAYOUT.FONT_MIDDLE.TYPE_LINE),
        card.type_line,
        font=typeFont,
        fill="black",
        anchor="lm",
    )


def drawTextBox(pen: ImageDraw.ImageDraw, card: Card, cardText: str):
    (fmtText, textFont) = fitMultiLine(
        fontPath="MPLANTIN.ttf",
        cardText=cardText,
        maxWidth=CARD_H - 2 * BORDER,
        maxHeight=C.STD_LAYOUT.SIZE.RULES_BOX - 2 * BORDER,
        fontSize=C.TEXT_FONT_SIZE,
    )
    pen.text(
        (BORDER, C.STD_LAYOUT.BORDER.RULES_BOX + BORDER),
        fmtText,
        font=textFont,
        fill="black",
    )


def drawPTL(pen: ImageDraw.ImageDraw, card: Card):
    if card.hasPT():
        ptl = f"{card.power}/{card.toughness}"
    elif card.hasL():
        ptl = card.loyalty
    else:
        return
    ptlFont = fitOneLine(
        fontPath="MPLANTIN.ttf",
        text=ptl,
        maxWidth=C.STD_PT_BOX[1][0] - C.STD_PT_BOX[0][0],
        fontSize=C.TITLE_FONT_SIZE,
    )

    pen.text(C.STD_PT_TEXT_POSITION, text=ptl, font=ptlFont, fill="black", anchor="mm")


def drawOther(pen: ImageDraw.ImageDraw):

    proxyFont = ImageFont.truetype("matrixb.ttf", size=C.OTHER_FONT_SIZE)
    pen.text(
        (BORDER, C.STD_LAYOUT.BORDER.OTHER + BORDER * 2 // 3),
        f"v{C.VERSION}",
        font=proxyFont,
        fill="black",
        anchor="lt",
    )

    credFont = ImageFont.truetype("MPLANTIN.ttf", size=C.OTHER_FONT_SIZE)
    pen.text(
        (BORDER, CARD_V - BORDER * 2 // 3),
        f"{C.CREDITS}",
        font=credFont,
        fill="black",
        anchor="lb",
    )


def batchSpacing(n: int, batchSize: tuple[int, int], pageSize: tuple[int, int]):
    maxH = pageSize[0] - (CARD_DISTANCE + (CARD_H + CARD_DISTANCE) * batchSize[0])
    maxV = pageSize[1] - (CARD_DISTANCE + (CARD_V + CARD_DISTANCE) * batchSize[1])
    return (
        maxH // 2 + CARD_DISTANCE + (CARD_H + CARD_DISTANCE) * (n % batchSize[0]),
        maxV // 2 + CARD_DISTANCE + (CARD_V + CARD_DISTANCE) * (n // batchSize[0]),
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
