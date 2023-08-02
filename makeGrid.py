import ujson
import time
import requests
from PIL import Image
from io import BytesIO
import urllib.request
import math
import pathlib
import random
import pathlib
import json
import traceback
import sys
import argparse

import urllib.parse

'''
response = requests.get("https://mtgjson.com/api/v5/AllIdentifiers.json")
jsonData = ujson.loads(response.content)
mapping = dict()
for k in jsonData['data'].keys():
    name = jsonData['data'][k]['name']
    setCode = jsonData['data'][k]['setCode'].lower()
    scryfallId = jsonData['data'][k]['identifiers']['scryfallId']
    if not name in mapping:
        mapping[name] = {}
    if not setCode in mapping[name]:
        mapping[name][setCode] = []
    mapping[name][setCode].append(scryfallId)
    
f = open("mapping.json", "w")
ujson.dump(mapping, f)
f.close()
'''

f = open("mapping.json", "r")
mapping = ujson.load(f)
f.close()



LANDTYPES = ['Island', 'Mountain', 'Forest', 'Plains', 'Swamp']
f = open("landIds.json", "r")
landIds = json.load(f)
f.close()
'''
staticLands = {}
for cardName in LANDTYPES:
    landDir = 'lands/' + cardName.lower()
    
    lands = []
    for p in pathlib.Path(landDir).iterdir():
        if p.is_file():
            lands.append(p)
            
    landDir += "/" + 'fullart'
    fullartlands = []
    for p in pathlib.Path(landDir).iterdir():
        if p.is_file():
            fullartlands.append(p)
    staticLands[cardName] = lands
    staticLands[cardName + "/fullart"] = fullartlands
 
landIds = {} 

for k,v in staticLands.items():
    newArr = []
    for p in v:
        key = p.parts[-1][:-4]
        if not key in jsonData['data']:
            newArr.append(key)
        else:
            newArr.append(jsonData['data'][key]['identifiers']['scryfallId'])
    landIds[k] = newArr

f = open("landIds.json", "w")
json.dump(landIds, f)
f.close()
'''
'''
for landType in ['Island', 'Mountain', 'Forest', 'Plains', 'Swamp']:
    pathlib.Path(landType).mkdir(parents=True, exist_ok=True)
    pathlib.Path(landType + "/fullart").mkdir(parents=True, exist_ok=True)
    for key in landIds[landType]:
        response = requests.get("https://api.scryfall.com/cards/" + key + "?format=image")
        Image.open(BytesIO(response.content)).save(landType + "/" + key + ".png")
        time.sleep(0.2)
    for key in landIds[landType + "/fullart"]: 
        response = requests.get("https://api.scryfall.com/cards/" + key + "?format=image")
        Image.open(BytesIO(response.content)).save(landType + "/fullart" + "/" + key + ".png")
        time.sleep(0.2)
'''
'''
# Default land mappings
defaultKeys = {
    'Island': '9c0f350d-13ec-4e13-9c4c-1d6bfb9aa0b3',
    'Mountain': '961dcc35-a282-4d40-93b3-1cc7fa5221f5',
    'Swamp': '48f7492c-67f2-4ba3-848b-7a6a8df7e88b',
    'Forest': 'aea5c36b-c107-4daf-bedb-507b4cd64724',
    'Plains': '5fc26aa1-58b9-41b5-95b4-7e9bf2309b54'
}

for k,v in defaultKeys.items():
    mapping[k].remove(v)
    mapping[k].insert(0, v)
'''

#mapping = dict([(jsonData['data'][k]['name'], jsonData['data'][k]['identifiers']['scryfallId']) for k in jsonData['data'].keys()])
response = None


def downloadIntoDirectory(ids, directory):
    for k in ids:
        response = requests.get("https://api.scryfall.com/cards/" + jsonData['data'][k]['identifiers']['scryfallId'] + "?format=image")
        Image.open(BytesIO(response.content)).save(directory + "/" + k + ".png")
        time.sleep(0.2)

def getFullArtLands(landName):
    for k in jsonData['data'].keys():
        if jsonData['data'][k]['name'] == landName and 'isFullArt' in jsonData['data'][k] and jsonData['data'][k]['isFullArt']:
            yield k

def getNonFullArtLands(landName):
    for k in jsonData['data'].keys():
        if jsonData['data'][k]['name'] == landName and ((not ('isFullArt' in jsonData['data'][k])) or (not jsonData['data'][k]['isFullArt'])):
            yield k
            
def getScryfallImage(cardName):
    return list(mapping[cardName].values())[0][0]
    
def getScryfallIdsWithSet(cardName, set):
    if not cardName in mapping:
        raise Exception("Could not find card with name " + cardName)
    elif cardName in mapping and not set.lower().strip() in mapping[cardName]:
        raise Exception("Could not find print of card " + cardName + " in set " + set)
    return mapping[cardName][set.lower().strip()]

def getScryfallIds(cardName):
    allIds = []
    for set, ids in mapping[cardName].items():
        allIds += ids
    return allIds
    
def resizeImage(image):
    width, height = image.size
    return image.resize((width//2,height//2), Image.ANTIALIAS)
    
def getScryfallImages(cardName, num, set=None, landconfig=None, lang='en'):
    if cardName in LANDTYPES and landconfig in ['basic', 'full']:
        images = []
        print(cardName)
        for i in range(num):
            if landconfig == 'full':
                scryfallId = random.choice(landIds[cardName + "/fullart"])
            else:
                scryfallId = random.choice(landIds[cardName])
            time.sleep(0.2) # rate limit
            response = requests.get("https://api.scryfall.com/cards/" + scryfallId + "?format=image")
            images.append(resizeImage(Image.open(BytesIO(response.content))))
        return images
    else:
        try:
            print(cardName)
            if set is None:
                scryfallIds = getScryfallIds(cardName)
            else:
                scryfallIds = getScryfallIdsWithSet(cardName, set)
            
            numNeeded = 1
            if landconfig == 'iter' and cardName in LANDTYPES:
                numNeeded = num
            
            idsMatchingLang = []
            for id in scryfallIds:
                time.sleep(0.2) # rate limit
                cardLang = requests.get("https://api.scryfall.com/cards/" + id + "?format=json").json()['lang'].lower().strip()
                if lang != cardLang:
                    print("incorrect language, trying next print")
                else:
                    idsMatchingLang.append(id)
                if len(idsMatchingLang) >= numNeeded: break
            
            if len(idsMatchingLang) == 0:
                print("could find no cards with name " + cardName + " with set " + str(set) + " in language " + lang + " using fallback")
                idsMatchingLang.append(scryfallIds[0])

            
            images = []
            cachedImages = [None for _ in range(len(idsMatchingLang))]
            for i in range(num):
                index = i % len(idsMatchingLang)
                image = cachedImages[index]
                if image is None:
                    id = idsMatchingLang[index]
                    time.sleep(0.2) # rate limit
                    response = requests.get("https://api.scryfall.com/cards/" + id + "?format=image")
                    image = resizeImage(Image.open(BytesIO(response.content)))
                    cachedImages[index] = image
                images.append(image)
                    
            return images
        except Exception as e:
            print(str(e))
            #print(traceback.format_exc())
            print("Using scryfall search")
            time.sleep(0.2) # rate limit
            try:
                results = ujson.loads(requests.get("https://api.scryfall.com/cards/search?q=" + urllib.parse.quote_plus(cardName)).content)['data']
                foundCard = None
                # neccessary because, for example, "sol ring" will return solemn offering (note sol ring is in that text)
                for card in results:
                    print(card['name'])
                    if card['name'].lower().strip() == cardName.lower().strip():
                        print("found card", cardName, "in set", card['set'])
                        foundCard = card
                if foundCard is None:
                    raise KeyError()
                imageUrl = foundCard['image_uris']['large']
            except KeyError:
                raise Exception("Scryfall search failed for card", cardName, "are you sure it is real?")
            response = requests.get(imageUrl)
            return [resizeImage(Image.open(BytesIO(response.content)))]*num
    
    
def makeGrid(fileText, numPerRow, landconfig, lang='en'):
    lines = [line.strip() for line in fileText.split("\n")]
    images = []
    
    
    for i, line in enumerate(lines):
        ind = line.find("\t")
        if ind == -1:
            ind = line.find(" ")
        if ind != -1:
            progress = i/max(1, len(lines)-1)
            num = int(line[:ind])
            cardName = line[ind+1:].strip()
            lastPosOfOpenParen = cardName.rfind("(")
            lastPosOfCloseParen = cardName.rfind(")")
            # set not specified, use default
            if lastPosOfOpenParen == -1 or lastPosOfCloseParen == -1:
                scryfallImages = getScryfallImages(cardName, num, landconfig=landconfig, lang=lang)
                images += scryfallImages
                #if cardName in ['Island', 'Mountain', 'Swamp', 'Plains', 'Forest']:
                #    
                #else:
            else:
                actualCardName = cardName[:lastPosOfOpenParen].strip()
                set = cardName[lastPosOfOpenParen+1:lastPosOfCloseParen]
                number = cardName[lastPosOfCloseParen+1:]
                scryfallImages = getScryfallImages(actualCardName, num, set=set, landconfig=landconfig, lang=lang)
                images += scryfallImages
            yield False, progress
    
            
    widths, heights = zip(*(i.size for i in images))
    max_width = max(widths)
    max_height = max(heights)
    width = max_width*numPerRow
    rows = int(math.ceil(len(images)/numPerRow))
    height = max_height*rows
    new_im = Image.new('RGB', (width, height))
    
    curImage = 0
    for row in range(rows):
        for col in range(numPerRow):
            x_offset = col*max_width
            y_offset = row*max_height
            im = images[curImage]
            new_im.paste(im, (x_offset,y_offset))
            curImage += 1
            if curImage >= len(images):
                break
        if curImage >= len(images):
            break

    yield True, new_im
            

if __name__ == "__main__":
  
  parser = argparse.ArgumentParser(
    prog='MTGSpritesheet',
    description='MTG Spritesheet maker')
  
  parser.add_argument('cardsfile')
  parser.add_argument('numrows') 
  parser.add_argument('landconfig', type=str, choices=['full', 'basic', 'iter', 'other'])  
  parser.add_argument('outfile')   
  parser.add_argument('--language', dest='language', default='en')   
  
  args = parser.parse_args()
  print(args)
  f = open(args.cardsfile, 'r')
  lines = f.read()
  f.close()
  try:
    for isDone, progress in makeGrid(lines, numPerRow=int(args.numrows), landconfig=args.landconfig, lang=args.language):
      if isDone:
        progress.save(args.outfile)
  except:
    print("You may need to run 'python updateMapping.py' if the missing card is in a new set")
    raise