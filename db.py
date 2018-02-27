import pymongo
import json

client = pymongo.MongoClient()
db = client.comp250

with open("maps.txt", "rt") as maps_file:
    maps = [name.strip() for name in maps_file if name.strip() != ""]

with open("allowed_users.json", "rt") as users_file:
    allowed_users = json.load(users_file)

