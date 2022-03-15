# BWProxy

> Grayscale MTG proxy generators 

## What is this?

A program which generates test card-style grayscale proxies for Magic cards. You can cut them out, draw your own art, and sleeve them in front of real cards! 

[Click here for some examples from my fully-proxied illustrated Sai deck.](https://raw.githubusercontent.com/a11ce/bwproxy/main/docs/exampleCards.jpg)

## How to use

Currently, the only way to use BWProxy is through the command line. If you don't know how to do that, I'll be releasing a website with the same functionality soon. 

If something doesn't work, please [open an issue on GitHub](https://github.com/a11ce/bwproxy/issues/new/choose) or message me on Discord @a11ce#0027.

### Download

* Install [Python](https://www.python.org)
* Get dependencies with `python3 -m pip install scrython pillow tqdm` 
* Download with `git clone https://github.com/a11ce/bwproxy.git` or via the [Github link](https://github.com/a11ce/bwproxy/releases/latest)

## Make some cards!

1. Save your decklist as a .txt in the `input` folder in the format `Cardname`, `1 Cardname` or `1x Cardname`, one card per line.
    - Empty lines will be ignored;
    - You can add comments with #. Every character from the # until the end of the line will be ignored;
    - A line will also be considered a comment (and thus it will be ignored) if it *starts* with `//`;
    - If the card is a modal or transforming double-faced card, both faces will be printed: you don't need to list both. Meld cards still need to be included separately;
    - If you're searching for a flavor name (for example **Godzilla, King of the Monsters**), the flavor name will appear on the title, and the Oracle name will appear under the title;
    - Optionally, you can put a custom flavor name in square brackets after a card name. It will appear like the official flavor names. Custom flavor names currently are not supported for any non-standard card frames, including Double-faced, Adventure and Flip cards
    - If you want aesthetic consistency (or to play with just paper cards), you can also generate basic land cards. They will be printed with a big mana symbol, but there is an option to remove the symbol and leave them as blank full-art lands, useful for testing a deck without sleeving. It's also the best option for customisation!
1. Optionally, put a grayscale/transparent png in `icons/`. You can use this in place of a set icon to indicate what cube or deck the cards are part of;
1. Run `python3 makeProxies.py [options] input/yourDeck.txt`. The options are listed below:
    - Add `--icon-path icons/yourIcon.png` to add a set icon. If the argument is not passed to the program, the cards will not have a set icon;
    - Add `--page-format [format]` to specify the page format. Possible formats are `a4paper` and `letter` (default is `a4paper`);
    - Add `--color` to print the card borders in color. Colored mana symbols are WIP;
    - Add `--no-text-symbols` to have the rules text use the oracle text style for mana symbols (`{W}` instead of the white mana symbol, etc);
    - Add `--small` to print the cards at 75% scale. This lets you print more cards on a single page;
    - Add `--no-card-space` to print the cards without blank space between them.
    - Add `--full-art-lands` to print basic lands without the big mana symbol.
    - Add `--ignore-basic-lands` to ignore basic lands when generating proxies.
    - Add `--alternative-frames` to print flip cards as if they were double-faced cards and aftermath cards as if they were split cards.
1. Print each page in `pages/yourDeck/` at full size and cut just outside the border of each card.

## Add tokens and emblems

1. Inside your decklist, you can also include tokens and emblems. The format is `(token) Token`, or `(emblem) Planeswalker Name` (ex. `(emblem) Ajani, Adversary of Tyrants`);
1. You can specify a quantity in the same way as the other cards, so for example two **Marit Lage** tokens are written as `2x (token) Marit Lage`;
1. If the token or emblem name is unique in the Scryfall database, all relevant info will be fetched automatically and put in the card;
1. The tokens will have an arched top, to better distinguish them from normal cards, and the emblems will have the Planeswalker symbol on the illustration. The symbol can be disabled with the `--full-art-lands` flag. They will also have their names centered;
1. If the token you are searching is not uniquely identified by its name (or you want some custom token!), you can specify the token info in detail.
    - The format is `(token) Legendary; P/T; colors; Subtypes; Types; text rule 1; text rule 2; ... [Custom Name]`. This should (mostly) respect the order in which the attributes are listed on the token-making card;
    - Spacing around the semicolon does not matter;
    - If a token does not have subtypes or Power/Toughness, or is not Legendary, skip the field;
    - The color should be given as a sequence of official abbreviations: `W` for White, `U` for Blue, `B` for Black, `R` for Red, `G` for Green. Colorless can be either an empty field or `C`. These letters **must** be uppercase;
    - To insert symbols in the token text, enclose the symbol abbreviation in braces: two generic mana is `{2}`, tap is `{T}`, etc;
    - If a token does not have a custom name, the subtypes will be used;
    - Here are some examples:
        - The **Marit Lage** token can be specified as `(token) Legendary; 20/20; B; Avatar; Creature; Flying, indestructible [Marit Lage]`
        - **Tamiyo's Notebook** (from *Tamiyo, Compleated Sage*) can be specified as `(token) Legendary; ; Artifact; Spells you cas cost {2} less to cast; {T}: Draw a card [Tamiyo's Notebook]`
        - An **Inkling** token from *Strixhaven* can be specified as `(token) 2/1;WB;Inkling;Creature;Flying`
        - A **Treasure** token can be specified as `(token) C; Treasure; Artifact; {T}, Sacrifice this artifact: Add one mana of any color`

--- 

Source code is available [here](https://github.com/a11ce/bwproxy). All contributions are welcome by pull request or issue.

Minor version numbers represent (possible) changes to the appearence of generated cards. Patch version numbers represent changes to the functionality of card generation.

BWProxy is licensed under GNU General Public License v3.0. See [LICENSE](https://github.com/a11ce/bwproxy/blob/main/LICENSE) for full text.

All mana and card symbol images are copyright Wizards of the Coast (http://magicthegathering.com).

Mana symbol vector images come from the [Mana Project](http://mana.andrewgioia.com/), licensed under MIT Licence.
