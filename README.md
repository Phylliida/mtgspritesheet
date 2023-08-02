# mtgspritesheet
Makes a Sprite Sheet out of a MTG deck using Scryfall

If you want to do the same thing but in the web, try apnda's [Online Tool](https://ctrl-c.club/~apnda/mtg.html)

Install dependencies:

pip install -r requirements.txt

or

pip install ujson pillow requests

Example Usage:

python makeGrid.py "Be the Dragon.txt" 5 full out.png

5 id number of cards per row

full is for full art lands
basic is for non-full art lands
iter will give you lands from whatever set you specify (format is like "Island (iko)")

optionally you can pass --language ja

(or some other language)

to specify language, and it will try and find prints in that language
