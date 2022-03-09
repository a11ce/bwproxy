from typing import Tuple, List, Match, Union, Optional, TypeVar
from PIL import Image, ImageDraw, ImageFont, ImageColor
from tqdm import tqdm
import os
import re

from . import projectConstants as C
from .projectTypes import Card, Deck, Flavor, XY, Box, Layout  # type: ignore

RgbColor = Union[Tuple[int, int, int], Tuple[int, int, int, int]]

DEF_BORDER_COLOR = C.FRAME_COLORS["default"]
DEF_BORDER_RGB = ImageColor.getrgb(DEF_BORDER_COLOR)

# Text formatting

specialTextRegex = re.compile(r"\{.+?\}")


def replFunction(m: Match[str]):
    """
    Replaces a {abbreviation} with the corresponding code point, if available.
    To be used in re.sub
    """
    t = m.group().upper()
    if t in C.FONT_CODE_POINT:
        return C.FONT_CODE_POINT[t]
    return t


S = TypeVar("S", str, None)


def printSymbols(text: S) -> S:
    """
    Substitutes all {abbreviation} in text with the corresponding code points
    """
    if text is None:
        return text
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
) -> Tuple[str, ImageFont.FreeTypeFont]:
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


def calcTopValue(font: ImageFont.FreeTypeFont, text: str, upperBorder: int, spaceSize: int) -> int:
    """
    Calculate the vertical value for top anchor in order to center text vertically.
    See https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html#text-anchors
    for explanation about font terms

    Middle of the space is at upperBorder + spaceSize // 2,
    and text is vsize // 2 over the text middle.
    So if we want space middle and text middle to align,
    we set top to space middle - vsize // 2 (remember that (0, 0) is top left)
    """
    # using getbbox because getsize does get the size :/
    (_, _, _, vsize) = font.getbbox(text, anchor="lt")
    return upperBorder + (spaceSize - vsize) // 2


# Black frame


def makeFrameAll(
    image: Image.Image,
    layout: Layout,
    rotate: bool = False,
    flip: bool = False,
    hasPTL: bool = False,
    isFuse: bool = False,
) -> Image.Image:
    """
    Draws the frame based on layout and various other options.
    All necessary dimensions are included in the layout
    """

    if rotate:
        image = image.transpose(Image.ROTATE_90)
    elif flip:
        image = image.transpose(Image.ROTATE_180)

    pen = ImageDraw.Draw(image)

    for cardSection in ["ILLUSTRATION", "TYPE_LINE", "RULES_BOX", "OTHER", "BOTTOM"]:
        pen.rectangle(
            (
                (layout.BORDER.LEFT, layout.BORDER.TITLE),
                (layout.BORDER.RIGHT, layout.BORDER[cardSection]),
            ),
            outline=DEF_BORDER_COLOR,
            width=5,
        )

    if hasPTL:
        pen.rectangle(
            (
                layout.BORDER.PTL_BOX_LEFT,
                layout.BORDER.PTL_BOX_TOP,
                layout.BORDER.PTL_BOX_RIGHT,
                layout.BORDER.PTL_BOX_BOTTOM,
            ),
            outline=DEF_BORDER_COLOR,
            fill=C.WHITE,
            width=5,
        )

    if isFuse:
        # Using 0 and CARD_V, unfortunately
        pen.rectangle(
            ((0, layout.BORDER.FUSE), (C.CARD_V, layout.BORDER.OTHER)),
            outline=DEF_BORDER_COLOR,
            fill=C.WHITE,
            width=5,
        )

    if rotate:
        image = image.transpose(Image.ROTATE_270)
    elif flip:
        image = image.transpose(Image.ROTATE_180)

    return image


def makeFrame(card: Card, image: Image.Image) -> Image.Image:
    """
    Creates a frame on which we can draw the card,
    and draws the basic card parts on it (black only)
    Color, if needed, will be added later
    """

    if card.layout in [C.SPLIT, C.FUSE]:
        isFuse = card.layout == C.FUSE
        image = makeFrameAll(
            image=image,
            layout=C.SPLIT_LAYOUT_LEFT,
            rotate=True,
            isFuse=isFuse,
        )
        image = makeFrameAll(
            image=image,
            layout=C.SPLIT_LAYOUT_RIGHT,
            rotate=True,
            isFuse=isFuse,
        )
    elif card.layout == C.AFTER:
        image = makeFrameAll(
            image=image,
            layout=C.AFTERMATH_LAYOUT,
        )
        image = makeFrameAll(
            image=image,
            layout=C.SPLIT_LAYOUT_RIGHT,
            rotate=True,
        )
    elif card.layout == C.ADV:
        image = makeFrameAll(
            image=image,
            layout=C.STD_LAYOUT,
            hasPTL=card.card_faces[0].hasPTL(),
        )
        image = makeFrameAll(
            image=image,
            layout=C.ADVENTURE_LAYOUT,
        )
    elif card.layout == C.FLIP:
        image = makeFrameAll(
            image=image,
            layout=C.FLIP_LAYOUT,
            hasPTL=card.card_faces[0].hasPTL(),
        )
        image = makeFrameAll(
            image=image,
            layout=C.FLIP_LAYOUT,
            flip=True,
            hasPTL=card.card_faces[1].hasPTL(),
        )
    elif card.isBasicLand():
        image = makeFrameAll(
            image=image,
            layout=C.LAND_LAYOUT,
        )
    elif card.isTextlessToken():
        # TOKEN_LAYOUT is for textless tokens (only color remainder)
        image = makeFrameAll(
            image=image,
            layout=C.TOKEN_LAYOUT,
        )
    elif card.isToken() or card.isEmblem():
        # EMBLEM_LAYOUT is for tokens with text and emblems
        image = makeFrameAll(
            image=image,
            layout=C.EMBLEM_LAYOUT,
        )
    else:
        image = makeFrameAll(
            image=image,
            layout=C.STD_LAYOUT,
            hasPTL=card.hasPTL(),
        )
    return image


# Colored frame utility function


def interpolateColor(color1: RgbColor, color2: RgbColor, weight: float) -> RgbColor:
    return tuple(int(a + (weight * (b - a))) for a, b in zip(color1, color2))


def coloredTemplateSimple(card: Card, size: XY) -> Image.Image:
    """
    Create a new image of specified size that is completely colored.
    If monocolor, colorless or pentacolor the color is uniform,
    otherwise there's a gradient effect for all the card colors
    """
    coloredTemplate = Image.new("RGB", size=size, color=C.WHITE)
    colors = card.colors

    pen = ImageDraw.Draw(coloredTemplate)

    imgColors = []
    if len(colors) == 0:
        multicolor = False
        imgColor = ImageColor.getrgb(C.FRAME_COLORS["C"])
    elif len(colors) == 1:
        multicolor = False
        imgColor = ImageColor.getrgb(C.FRAME_COLORS[colors[0]])
    elif len(colors) == 5:
        multicolor = False
        imgColor = ImageColor.getrgb(C.FRAME_COLORS["M"])
    else:
        multicolor = True
        imgColor = ImageColor.getrgb(C.FRAME_COLORS["M"])
        imgColors = [ImageColor.getrgb(C.FRAME_COLORS[c]) for c in colors]

    if not multicolor:
        for idx in range(size[0]):
            pen.line(
                [(idx, 0), (idx, size[1])],
                imgColor,
                width=1,
            )
        return coloredTemplate

    n = len(imgColors) - 1
    segmentLength = size[0] // n
    # imgColors.append(imgColors[-1]) # Necessary line in order not to crash

    for idx in range(size[0]):
        i = idx // segmentLength
        pen.line(
            [(idx, 0), (idx, size[1])],
            interpolateColor(
                imgColors[i], imgColors[i + 1], (idx % segmentLength) / segmentLength
            ),
            width=1,
        )

    return coloredTemplate


def colorHalf(
    card: Card, image: Image.Image, layout: Layout, rotate: bool = False
) -> Image.Image:
    if rotate:
        image = image.transpose(Image.ROTATE_90)
    size = XY(layout.SIZE.H, layout.SIZE.V)
    halfImage = coloredTemplateSimple(card=card, size=size)
    image.paste(halfImage, box=(layout.BORDER.LEFT, layout.BORDER.TITLE))
    if rotate:
        image = image.transpose(Image.ROTATE_270)
    return image


def coloredBlank(card: Card) -> Image.Image:
    """
    Creates a template for two-colored card frames,
    with a color shift from the first color to the second
    This template is then used to set the colors in the real frame
    """
    coloredTemplate = Image.new("RGB", size=C.CARD_SIZE, color=C.WHITE)

    if card.layout in [C.SPLIT, C.FUSE]:
        # breakpoint()
        faces = card.card_faces
        coloredTemplate = colorHalf(
            card=faces[0],
            image=coloredTemplate,
            layout=C.SPLIT_LAYOUT_LEFT,
            rotate=True,
        )
        coloredTemplate = colorHalf(
            card=faces[1],
            image=coloredTemplate,
            layout=C.SPLIT_LAYOUT_RIGHT,
            rotate=True,
        )
        return coloredTemplate
    elif card.layout == C.AFTER:
        faces = card.card_faces
        coloredTemplate = colorHalf(
            card=faces[0], image=coloredTemplate, layout=C.AFTERMATH_LAYOUT
        )
        coloredTemplate = colorHalf(
            card=faces[1],
            image=coloredTemplate,
            layout=C.SPLIT_LAYOUT_RIGHT,
            rotate=True,
        )
        return coloredTemplate
    # Flip does not have multicolored cards, so I'm ignoring it
    # Adventure for now is monocolored or both parts are the same color
    else:
        return coloredTemplateSimple(card=card, size=C.CARD_SIZE)


def colorBorders(card: Card, image: Image.Image) -> Image.Image:
    coloredTemplate = coloredBlank(card=card)
    for idx in range(C.CARD_H):
        for idy in range(C.CARD_V):
            if image.getpixel((idx, idy)) == DEF_BORDER_RGB:
                image.putpixel((idx, idy), coloredTemplate.getpixel((idx, idy)))  # type: ignore
    return image


# Symbol


def resizeSetIcon(setIcon: Image.Image) -> Image.Image:
    iconSize = setIcon.size
    scaleFactor = max(iconSize[0] / C.SET_ICON_SIZE, iconSize[1] / C.SET_ICON_SIZE)
    setIcon = setIcon.resize(
        size=(int(iconSize[0] / scaleFactor), int(iconSize[1] / scaleFactor))
    )
    return setIcon


def correctSetIconPosition(setIcon: Image.Image, position: XY) -> XY:
    iconSize: XY = XY(setIcon.size)
    setIconSizeXY: XY = XY(C.SET_ICON_SIZE, C.SET_ICON_SIZE)
    return position + (setIconSizeXY - iconSize).scale(0.5)


def pasteSetIcon(card: Card, image: Image.Image, setIcon: Image.Image) -> Image.Image:

    if card.layout in [C.SPLIT, C.FUSE]:
        image = image.transpose(Image.ROTATE_90)
        position = C.SPLIT_SET_ICON_POSITION[0]
    elif card.layout == C.AFTER:
        position = C.AFTERMATH_SET_ICON_POSITION
    elif card.layout == C.FLIP:
        position = C.FLIP_SET_ICON_POSITION
    elif card.isBasicLand():
        position = C.LAND_SET_ICON_POSITION
    elif card.isTextlessToken():
        position = C.TOKEN_SET_ICON_POSITION
    elif card.isTokenOrEmblem():
        position = C.EMBLEM_SET_ICON_POSITION
    else:
        position = C.STD_SET_ICON_POSITION
    image.paste(
        im=setIcon,
        box=correctSetIconPosition(setIcon=setIcon, position=position).tuple(),
    )

    if card.layout in [C.SPLIT, C.FUSE]:
        position = C.SPLIT_SET_ICON_POSITION[1]
    elif card.layout == C.AFTER:
        image = image.transpose(Image.ROTATE_90)
        position = C.SPLIT_SET_ICON_POSITION[1]
    elif card.layout == C.FLIP:
        image = image.transpose(Image.ROTATE_180)
        position = C.FLIP_SET_ICON_POSITION
    else:
        return image

    image.paste(
        im=setIcon,
        box=correctSetIconPosition(setIcon=setIcon, position=position).tuple(),
    )

    if card.layout in [C.SPLIT, C.FUSE, C.AFTER]:
        image = image.transpose(Image.ROTATE_270)
    elif card.layout == C.FLIP:
        image = image.transpose(Image.ROTATE_180)

    return image


def drawIllustrationSymbol(card: Card, image: Image.Image) -> Image.Image:

    if card.isBasicLand():
        illustrationSymbolName = card.name.split()[-1]
        position = C.LAND_MANA_SYMBOL_POSITION.tuple()
    elif card.isEmblem():
        illustrationSymbolName = "Emblem"
        position = C.EMBLEM_SYMBOL_POSITION.tuple()
    else:
        return image

    illustrationSymbol = Image.open(
        f"{C.BACK_CARD_SYMBOLS_LOC}/{illustrationSymbolName}.png"
    )
    image.paste(
        illustrationSymbol,
        box=position,
        mask=illustrationSymbol,
    )
    return image


# Text


def getLayoutInfoAndRotation(card: Card) -> Tuple[Layout, bool, bool]:
    try:
        layoutName = card.layout
    except:
        layoutName = card.face_type

    if card.isBasicLand():
        layoutName = C.LAND
    elif card.isTextlessToken():
        layoutName = C.TOKEN
    elif card.isTokenOrEmblem():
        layoutName = C.EMBLEM

    layoutInfoList = C.LAYOUTS[layoutName]

    if layoutName in C.TWO_PARTS_LAYOUTS:
        layoutInfo = layoutInfoList[card.face_num]
    else:
        layoutInfo = layoutInfoList[0]

    rotate = layoutName in [C.SPLIT, C.FUSE] or (
        layoutName == C.AFTER and card.face_num == 1
    )

    flip = layoutName == C.FLIP and card.face_num == 1

    return (layoutInfo, rotate, flip)


def drawText(
    card: Card,
    image: Image.Image,
    flavorNames: Flavor = {},
    useTextSymbols: bool = True,
    fullArtLands: bool = False,
    hasSetIcon: bool = True,
) -> Image.Image:

    if card.layout in C.TWO_PARTS_LAYOUTS:
        faces = card.card_faces
    else:
        faces = [card]

    for face in faces:
        if face.face_type == C.ADV and face.face_num == 1:
            hasSetIcon = False
        image = drawTitleLine(card=face, image=image, flavorNames=flavorNames)
        if not fullArtLands:
            image = drawIllustrationSymbol(card=card, image=image)
        image = drawTypeLine(card=face, image=image, hasSetIcon=hasSetIcon)
        image = drawTextBox(card=face, image=image, useTextSymbols=useTextSymbols)
        image = drawPTL(card=face, image=image)
        image = drawOther(card=face, image=image)
    return image


def drawTitleLine(
    card: Card,
    image: Image.Image,
    flavorNames: Flavor = {},
) -> Image.Image:
    """
    Draw mana cost. name and flavor name (if present) for a card
    """
    (layoutInfo, rotate, flip) = getLayoutInfoAndRotation(card)

    manaCornerRight = layoutInfo.BORDER.RIGHT - C.BORDER
    alignNameLeft = layoutInfo.BORDER.LEFT + C.BORDER
    alignNameAnchor = "lt"

    if rotate:
        image = image.transpose(Image.ROTATE_90)
    elif flip:
        image = image.transpose(Image.ROTATE_180)

    pen = ImageDraw.Draw(image)

    if card.isTokenOrEmblem():
        # Token and Emblems have no mana cost, and have a centered title
        alignNameLeft = layoutInfo.BORDER.LEFT + layoutInfo.SIZE.H // 2
        alignNameAnchor = "mt"
        maxNameWidth = layoutInfo.SIZE.H - 2 * C.BORDER
    else:
        manaCost = printSymbols(card.mana_cost)
        maxManaWidth = max(layoutInfo.SIZE.H // 2, C.CARD_H // 16 * len(manaCost))

        # This fitOneLine was born for Oakhame Ranger // Bring Back, which has
        # 4 hybrid mana symbols on the adventure part, making the title unreadable
        # So we force the mana cost to a dimension such that 8 mana symbols
        # occupy at the minimum 1/2 of the horizontal dimension
        # (we don't want the mana symbols to be too small)
        # and the dimension can grow up to half the card length,
        # if it has not already overflown.
        #
        # It also helps with cards like Progenitus or Emergent Ultimatum
        manaFont = fitOneLine(
            fontPath=C.SERIF_FONT,
            text=manaCost,
            maxWidth=maxManaWidth,
            fontSize=C.TITLE_FONT_SIZE,
        )
        # Test for easier mana writing
        pen.text(
            (
                manaCornerRight,
                calcTopValue(
                    font=manaFont,
                    text=manaCost,
                    upperBorder=layoutInfo.BORDER.TITLE,
                    spaceSize=layoutInfo.SIZE.TITLE
                )
            ),
            text=manaCost,
            font=manaFont,
            fill=C.BLACK,
            anchor="rt",
        )
        xPos = manaCornerRight - manaFont.getsize(manaCost)[0]
        # Mana was written in reverse, could be useful for colored hybrid or something
        # xPos = manaCornerRight
        # for c in manaCost[::-1]:
        #     pen.text(
        #         (xPos, manaCornerAscendant), text=c, font=manaFont, fill="black", anchor="ra"
        #     )
        #     xPos -= manaFont.getsize(c)[0]
        maxNameWidth = xPos - alignNameLeft - C.BORDER

    displayName = flavorNames[card.name] if card.name in flavorNames else card.name

    # Section for card indicator at left of the name (dfc and flip)
    # It is separated from title because we want it always at max size
    if card.face_type in C.DFC_LAYOUTS or card.face_type == C.FLIP:
        faceSymbolFont = ImageFont.truetype(C.SERIF_FONT, size=C.TITLE_FONT_SIZE)
        faceSymbol = f"{C.FONT_CODE_POINT[card.face_symbol]} "
        pen.text(
            (
                alignNameLeft,
                calcTopValue(
                    font=faceSymbolFont,
                    text=faceSymbol,
                    upperBorder=layoutInfo.BORDER.TITLE,
                    spaceSize=layoutInfo.SIZE.TITLE
                ),
            ),
            text=faceSymbol,
            font=faceSymbolFont,
            fill=C.BLACK,
            anchor="lt",
        )
        faceSymbolSpace = faceSymbolFont.getsize(faceSymbol)[0]
        alignNameLeft += faceSymbolSpace
        maxNameWidth -= faceSymbolSpace

    nameFont = fitOneLine(
        fontPath=C.SERIF_FONT,
        text=displayName,
        maxWidth=maxNameWidth,
        fontSize=C.TITLE_FONT_SIZE,
    )
    pen.text(
        (
            alignNameLeft,
            calcTopValue(
                font=nameFont,
                text=displayName,
                upperBorder=layoutInfo.BORDER.TITLE,
                spaceSize=layoutInfo.SIZE.TITLE
            )
        ),
        text=displayName,
        font=nameFont,
        fill=C.BLACK,
        anchor=alignNameAnchor,
    )

    # Writing oracle name, if card has also a flavor name
    # Card name goes at the top of the illustration, centered.
    if card.name in flavorNames and card.face_type not in [
        C.SPLIT,
        C.FUSE,
        C.AFTER,
        C.FLIP,
    ]:
        trueNameFont = ImageFont.truetype(font=C.SERIF_FONT, size=C.TEXT_FONT_SIZE)
        pen.text(
            (
                (layoutInfo.BORDER.LEFT + layoutInfo.BORDER.RIGHT) // 2,
                layoutInfo.BORDER.ILLUSTRATION + C.BORDER,
            ),
            card.name,
            font=trueNameFont,
            fill=C.BLACK,
            anchor="mt",
        )

    if rotate:
        image = image.transpose(Image.ROTATE_270)
    elif flip:
        image = image.transpose(Image.ROTATE_180)

    return image


def drawTypeLine(
    card: Card,
    image: Image.Image,
    hasSetIcon: bool = True,
) -> Image.Image:
    """
    Draws the type line, leaving space for set icon (if present)
    """

    (layoutInfo, rotate, flip) = getLayoutInfoAndRotation(card)

    alignTypeLeft = layoutInfo.BORDER.LEFT + C.BORDER
    setIconMargin = (C.BORDER + C.SET_ICON_SIZE) if hasSetIcon else 0
    maxWidth = layoutInfo.SIZE.H - 2 * C.BORDER - setIconMargin

    if rotate:
        image = image.transpose(Image.ROTATE_90)
    elif flip:
        image = image.transpose(Image.ROTATE_180)

    pen = ImageDraw.Draw(image)

    typeFont = fitOneLine(
        fontPath=C.SERIF_FONT,
        text=card.type_line,
        maxWidth=maxWidth,
        fontSize=C.TYPE_FONT_SIZE,
    )
    pen.text(
        (
            alignTypeLeft,
            calcTopValue(
                font=typeFont,
                text=card.type_line,
                upperBorder=layoutInfo.BORDER.TYPE_LINE,
                spaceSize=layoutInfo.SIZE.TYPE_LINE
            )
        ),
        text=card.type_line,
        font=typeFont,
        fill=C.BLACK,
        anchor="lt",
    )

    if rotate:
        image = image.transpose(Image.ROTATE_270)
    elif flip:
        image = image.transpose(Image.ROTATE_180)

    return image


def drawTextBox(
    card: Card,
    image: Image.Image,
    useTextSymbols: bool = True,
) -> Image.Image:
    """
    Draw rules text box.
    Adding a rule for color indicator, if present
    """

    if card.isBasicLand():
        return image

    (layoutInfo, rotate, flip) = getLayoutInfoAndRotation(card)

    cardText = f"{card.color_indicator_reminder_text}{card.oracle_text}".strip()
    if useTextSymbols:
        cardText = printSymbols(cardText)

    alignRulesTextLeft = layoutInfo.BORDER.LEFT + C.BORDER
    maxWidth = layoutInfo.SIZE.H - 2 * C.BORDER

    # Adventure main face only has half the space for rules text
    # I feel so dirty doing this here, but I see no choice
    if card.face_type == C.ADV and card.face_num == 0:
        alignRulesTextLeft = layoutInfo.BORDER.LEFT + layoutInfo.SIZE.H // 2 + C.BORDER
        maxWidth = layoutInfo.SIZE.H // 2 - 2 * C.BORDER

    alignRulesTextAscendant = layoutInfo.BORDER.RULES_BOX + C.BORDER

    if card.face_type == C.FUSE:
        maxHeight = layoutInfo.SIZE.RULES_BOX_FUSE - 2 * C.BORDER
    else:
        maxHeight = layoutInfo.SIZE.RULES_BOX - 2 * C.BORDER

    if rotate:
        image = image.transpose(Image.ROTATE_90)
    elif flip:
        image = image.transpose(Image.ROTATE_180)

    pen = ImageDraw.Draw(image)

    (fmtText, textFont) = fitMultiLine(
        fontPath=C.MONOSPACE_FONT,
        cardText=cardText,
        maxWidth=maxWidth,
        maxHeight=maxHeight,
        fontSize=C.TEXT_FONT_SIZE,
    )
    pen.text(
        (alignRulesTextLeft, alignRulesTextAscendant),
        text=fmtText,
        font=textFont,
        fill=C.BLACK,
        anchor="la",
    )

    if rotate:
        image = image.transpose(Image.ROTATE_270)
    elif flip:
        image = image.transpose(Image.ROTATE_180)

    return image


def drawFuseText(card: Card, image: Image.Image) -> Image.Image:
    if not card.layout == C.FUSE:
        return image

    image = image.transpose(Image.ROTATE_90)
    pen = ImageDraw.Draw(image)

    fuseTextFont = fitOneLine(
        fontPath=C.MONOSPACE_FONT,
        text=card.fuse_text,
        maxWidth=C.CARD_V - 2 * C.BORDER,
        fontSize=C.TEXT_FONT_SIZE,
    )
    # Using SPLIT_LAYOUT_LEFT because it's indistinguishable from SPLIT_LAYOUT_RIGHT
    pen.text(
        (
            C.BORDER,
            calcTopValue(
                font=fuseTextFont,
                text=card.fuse_text,
                upperBorder=C.SPLIT_LAYOUT_LEFT.BORDER.FUSE,
                spaceSize=C.SPLIT_LAYOUT_LEFT.SIZE.FUSE
            )
        ),
        text=card.fuse_text,
        font=fuseTextFont,
        fill=C.BLACK,
        anchor="lt",
    )

    image = image.transpose(Image.ROTATE_270)

    return image


def drawPTL(card: Card, image: Image.Image) -> Image.Image:
    """
    Draws Power / Toughness or Loyalty (if present) on the PTL box
    """

    (layoutInfo, rotate, flip) = getLayoutInfoAndRotation(card)

    if card.hasPT():
        ptl = f"{card.power}/{card.toughness}"
    elif card.hasL():
        ptl = card.loyalty
    else:
        return image

    if rotate:
        image = image.transpose(Image.ROTATE_90)
    elif flip:
        image = image.transpose(Image.ROTATE_180)

    pen = ImageDraw.Draw(image)

    ptlFont = fitOneLine(
        fontPath=C.MONOSPACE_FONT,
        text=ptl,
        maxWidth=layoutInfo.SIZE.PTL_BOX_H - 2 * C.BORDER,
        fontSize=C.TITLE_FONT_SIZE,
    )

    pen.text(
        (layoutInfo.FONT_MIDDLE.PTL_H, layoutInfo.FONT_MIDDLE.PTL_V),
        text=ptl,
        font=ptlFont,
        fill=C.BLACK,
        anchor="mm",
    )

    if rotate:
        image = image.transpose(Image.ROTATE_270)
    elif flip:
        image = image.transpose(Image.ROTATE_180)

    return image


def drawOther(card: Card, image: Image.Image) -> Image.Image:
    """
    Draws other information in the bottom section (site and version)
    """

    (layoutInfo, rotate, flip) = getLayoutInfoAndRotation(card)

    alignOtherLeft = layoutInfo.BORDER.LEFT + C.BORDER

    if card.face_type == C.ADV and card.face_num == 1:
        return image

    if rotate:
        image = image.transpose(Image.ROTATE_90)
    elif flip:
        image = image.transpose(Image.ROTATE_180)

    pen = ImageDraw.Draw(image)

    credFont = ImageFont.truetype(C.MONOSPACE_FONT, size=C.OTHER_FONT_SIZE)
    pen.text(
        (
            alignOtherLeft,
            calcTopValue(
                font=credFont,
                text=C.CREDITS,
                upperBorder=layoutInfo.BORDER.OTHER,
                spaceSize=layoutInfo.SIZE.OTHER
            )
        ),
        text=C.CREDITS,
        font=credFont,
        fill=C.BLACK,
        anchor="lt",
    )
    credLength = pen.textlength(text=C.CREDITS + "   ", font=credFont)

    proxyFont = ImageFont.truetype(C.SERIF_FONT, size=C.OTHER_FONT_SIZE * 4 // 3)
    pen.text(
        (
            alignOtherLeft + credLength,
            calcTopValue(
                font=proxyFont,
                text=C.VERSION,
                upperBorder=layoutInfo.BORDER.OTHER,
                spaceSize=layoutInfo.SIZE.OTHER
            )
        ),
        text=C.VERSION,
        font=proxyFont,
        fill=C.BLACK,
        anchor="lt",
    )

    if rotate:
        image = image.transpose(Image.ROTATE_270)
    elif flip:
        image = image.transpose(Image.ROTATE_180)

    return image


# Draw card from beginning to end


def drawCard(
    card: Card,
    isColored: bool = False,
    setIcon: Optional[Image.Image] = None,
    flavorNames: Flavor = {},
    useTextSymbols: bool = True,
    fullArtLands: bool = False,
) -> Image.Image:
    """
    Takes card info and external parameters, producing a complete image.
    """

    image = Image.new("RGB", size=C.CARD_SIZE, color=C.WHITE)
    pen = ImageDraw.Draw(image)
    # Card border
    pen.rectangle(((0, 0), C.CARD_SIZE), outline=DEF_BORDER_COLOR, width=5)

    image = makeFrame(card=card, image=image)
    if isColored:
        image = colorBorders(card=card, image=image)
    if setIcon is not None:
        image = pasteSetIcon(card=card, image=image, setIcon=setIcon)
    image = drawText(
        card=card,
        image=image,
        flavorNames=flavorNames,
        useTextSymbols=useTextSymbols,
        fullArtLands=fullArtLands,
        hasSetIcon=setIcon is not None
    )

    return image


# Paging


def batchSpacing(
    n: int,
    batchSize: Tuple[int, int],
    pageSize: XY,
    cardSize: XY,
    noCardSpace: bool = False,
):
    CARD_H = cardSize[0]
    CARD_V = cardSize[1]
    CARD_DISTANCE = 1 if noCardSpace else C.CARD_DISTANCE
    maxH = pageSize[0] - (CARD_DISTANCE + (CARD_H + CARD_DISTANCE) * batchSize[0])
    maxV = pageSize[1] - (CARD_DISTANCE + (CARD_V + CARD_DISTANCE) * batchSize[1])
    return (
        maxH // 2 + CARD_DISTANCE + (CARD_H + CARD_DISTANCE) * (n % batchSize[0]),
        maxV // 2 + CARD_DISTANCE + (CARD_V + CARD_DISTANCE) * (n // batchSize[0]),
    )


def savePages(
    images: List[Image.Image],
    deckName: str,
    small: bool = False,
    pageFormat: C.PageFormat = C.A4_FORMAT,
    noCardSpace: bool = False,
):
    os.makedirs(os.path.dirname(f"pages/{deckName}/"), exist_ok=True)
    pageHoriz = False
    cardSize = C.CARD_SIZE
    if not small:
        batchSize = (3, 3)
    else:
        batchSize = (4, 4)

    batchNum = batchSize[0] * batchSize[1]

    if pageFormat == C.A4_FORMAT:
        pageSize = C.A4_PAPER
    elif pageFormat == C.LETTER_FORMAT:
        pageSize = C.LETTER_PAPER
    else:
        raise Exception(f"Unknown parameter: {pageFormat}")

    if small:
        cardSize = C.SMALL_CARD_SIZE
        images = [image.resize(cardSize) for image in images]

    if pageHoriz:
        pageSize = pageSize.transpose()

    for i in tqdm(
        range(0, len(images), batchNum),
        desc="Pagination progress: ",
        unit="page",
    ):
        batch = images[i : i + batchNum]
        page = Image.new("RGB", size=pageSize, color="white")
        for n in range(len(batch)):
            page.paste(
                batch[n],
                batchSpacing(
                    n,
                    batchSize=batchSize,
                    pageSize=pageSize,
                    cardSize=cardSize,
                    noCardSpace=noCardSpace,
                ),
            )

        page.save(f"pages/{deckName}/{i // batchNum + 1:02}.png", "PNG")
