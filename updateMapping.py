import requests
import ujson

if True:
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