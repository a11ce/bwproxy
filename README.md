# BWProxy

> Grayscale MTG proxy generators 

## What is this?

A program which generates test card-style grayscale proxies for Magic cards. You can cut them out, draw your own art, and sleeve them in front of real cards!

## How to use


Currently, the only way to use BWProxy is through the command line. If you don't know how to do that, I'll be releasing a website with the same functionality soon.

### Download

1. Get dependencies with `python3 -m pip install mtgsdk pillow tqdm` 
2. Download with `git clone https://github.com/a11ce/bwproxy.git`

### Make some cards!

1. Save your decklist as a .txt in the format `1 Cardname` or `1x Cardname`, one card per line. Currently only singleton formats are supported.
2. Optionally, put a grayscale/transparent png in `icons/`. You can use this in place of a set icon to indicate what cube or deck the cards are part of.
3. Run `python3 makeProxies.py yourDeck.txt` (or `python3 makeProxies.py yourDeck.txt icons/yourIcon.png` if you want a set icon).
4. Print each page in `pages/yourDeck/` at full size/fit to page and cut just outside the border of each card.

## Make some lands! (WIP)

If you're sleeving your BWProxies, you can just use real basic lands. But if you want aesthetic consistency (or to play with just paper cards), you can also generate basics.

1. Run `python3 makeBasics.py` in `basics/`.
2. Within `basics/pages/`
    - `symbolLands` will contain lands with a big mana symbol. These are very distinguishable even without color, and perfect for sleeving.
    - `blankLands` will contain blank full-art-frame lands. These are good for quickly testing a deck without sleeving because the large symbols are often visible through the back of the paper. You can also draw your own art!
3. Print however many you need at full size/fit to page and cut just outside the border or each card.


--- 

All contributions are welcome by pull request or issue.

BWProxy is licensed under GNU General Public License v3.0. See [LICENSE](../master/LICENSE) for full text. Fonts and mana symbols are excluded.
