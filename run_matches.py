import pymongo
import time
import random
import os
import zipfile
import json
import subprocess
import datetime

from db import db
import stats


def play_match(match):
	command = ["java", "-cp", "microrts.jar:lib/*", "comp250.PlaySingleMatch"]
	
	for player in match["players"]:
		author, bot_id, class_name = player.split('+')
		bot_id = author + '+' + bot_id
		bot = db.bots.find_one({"_id": bot_id})
		jar_name = bot_id + '+' + bot["head"][:10] + '.jar'
		jar_path = os.path.join("..", "tournament", jar_name)
		command.append(jar_path)
		command.append(class_name)
	
	command.append(match["map"])
	
	zip_name = str(match["_id"]) + ".zip"
	zip_path = os.path.join("..", "tournament", "matches", zip_name)
	command.append(zip_path)

	working_dir = os.path.join("..", "comp250-microrts")
	
	print(command)

	start_time = datetime.datetime.now()
	result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", cwd=working_dir)
	end_time = datetime.datetime.now()
	
	with zipfile.ZipFile(zip_path, 'a') as zf:
		with zf.open('result.json', 'r') as json_file:
			result_json = json.load(json_file)
			print(result_json)
			match["result"] = result_json
		with zf.open('stdout.txt', 'w') as stdout_file:
			stdout_file.write(result.stdout.encode('utf8'))
		if "stackTrace" in result_json:
			with zf.open('stack_trace.txt', 'w') as stack_trace_file:
				stack_trace_file.write(result_json["stackTrace"].encode('utf8'))
			
	
	match["zip"] = zip_name
	match["start_time"] = start_time
	match["end_time"] = end_time
	
	db.match_history.insert_one(match)
	db.match_history.create_index("players")
	
	stats.update_stats(match)


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

