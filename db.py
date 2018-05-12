import pymongo
import json

from config import config

client = pymongo.MongoClient()
db = client[config.database_name]

maps = config.maps

with open("allowed_users.json", "rt") as users_file:
    allowed_users = json.load(users_file)

