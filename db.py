import pymongo

client = pymongo.MongoClient()
db = client.comp250

with open("maps.txt", "rt") as maps_file:
    maps = [name.strip() for name in maps_file if name.strip() != ""]


