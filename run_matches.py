import pymongo
import time
import random
import os
import zipfile
import json
import subprocess

client = pymongo.MongoClient()
db = client.comp250


def play_match(match):
	command = ["java", "-cp", "microrts.jar:lib/*", "comp250.PlaySingleMatch"]
	
	for player in ["player1", "player2"]:
		jar_name = match[player]["bot"].replace('/', '+') + '+' + match[player]["head"][:10] + '.jar'
		jar_path = os.path.join("..", "tournament", jar_name)
		command.append(jar_path)
		command.append(match[player]["class_name"])
	
	command.append(match["map"])
	
	zip_name = str(match["_id"]) + ".zip"
	zip_path = os.path.join("..", "tournament", "matches", zip_name)
	command.append(zip_path)

	working_dir = os.path.join("..", "comp250-microrts")
	
	print(command)
	result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", cwd=working_dir)
	
	try:
		with zipfile.ZipFile(zip_path, 'r') as zf:
			with zf.open('result.json', 'r') as json_file:
				result_json = json.load(json_file)
				print(result_json)
				match["result"] = result_json
	except Exception as e:
		match["result"] = str(e)
	
	match["zip"] = zip_name
	match["stdout"] = result.stdout
	
	db.match_history.insert_one(match)


def main():
	while True:
		match = db.match_queue.find_one_and_delete({}, sort=[("random", pymongo.ASCENDING)])
		if match is not None:
			play_match(match)
		else:
			print("Waiting for matches")
			time.sleep(1)


if __name__ == '__main__':
	main()

