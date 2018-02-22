import flask
import pymongo
import subprocess
import os
import urllib
import json
from urllib.parse import urlparse

from worker import WorkerThread

app = flask.Flask(__name__)

client = pymongo.MongoClient()
db = client.comp250

worker = WorkerThread()
worker.daemon = True
worker.start()

def run_commands(working_dir, commands):
	output = []
	
	for command in commands:
		print(command)
		output.append('-' * 80)
		output.append(working_dir + '> ' + ' '.join(command))
		
		result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", cwd=working_dir)
		output.append(result.stdout)
		print(result.stdout)
		
		if result.returncode != 0:
			output.append('-' * 80)
			output.append("Failed with error code {}".format(result.returncode))
			return (False, '\n'.join(output))
	
	return (True, '\n'.join(output))

def is_github_url(url):
	parsed_url = urlparse(url)
	netloc = parsed_url.netloc.split('.')
	return len(netloc) >= 2 and netloc[-2] == "github" and netloc[-1] == "com"

def authenticate(bot):
	if not is_github_url(bot["repository"]["clone_url"]):
		return False, "Cannot clone from a non-GitHub URL"
	
	orgs_url = bot["repository"]["owner"]["organizations_url"]
	if not is_github_url(orgs_url):
		return False, "You are not a member of Falmouth-Games-Academy"

	with urllib.request.urlopen(orgs_url) as resp:
		orgs = json.load(resp)
	
	if not any(o["login"] == "Falmouth-Games-Academy" for o in orgs):
		return False, "You are not a member of Falmouth-Games-Academy"
	
	return True, ""

def pull_and_build(bot):
	clone_path = os.path.join("..", "tournament", bot["_id"].replace("/", "+"))
	commands = []
	
	if not os.path.exists(clone_path):
		os.mkdir(clone_path)
		commands = [
			["git", "init"],
			["git", "remote", "add", "origin", bot["repository"]["clone_url"]],
			["git", "fetch"],
			["git", "reset", "--hard", bot["head"]],
			["git", "submodule", "update", "--init", "--recursive"]
		]
	else:
		commands = [
			["git", "clean", "-fdx"],
			["git", "fetch"],
			["git", "reset", "--hard", bot["head"]]
		]
	
	jar_name = bot["_id"].replace("/", "+") + "+" + bot["head"][:10] + ".jar"

	commands += [
		["ant", "-buildfile", "bot", "clean", "build", "jar"],
		["cp", "-v", os.path.join("bot", "bot.jar"),
			os.path.join("..", jar_name)]
	]

	success, build_log = run_commands(clone_path, commands)

	if success:
		command = ["java", "-cp", "microrts.jar:lib/*", "comp250.ListTournamentAIsInJar",
			os.path.join("..", "tournament", jar_name)]
		working_dir = os.path.join("..", "comp250-microrts")
		
		result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", cwd=working_dir)
		if result.returncode == 0:
			class_names = [name for name in result.stdout.split('\n') if name != ""]
			print(class_names)
		else:
			class_names = []
			build_log += '-' * 80
			build_log += "\nListTournamentAIsInJar failed:\n"
			build_log += result.stderr
			print(result.stderr)
			success = False
		
	status = "ready" if success else "error"
	
	db.bots.update_one(
		{"_id": bot["_id"]},
		{"$set": {
			"status": status,
			"build_log": build_log,
			"class_names": class_names
		}
	})

	print("pull_and_build finished")
	return success

@app.route("/")
def hello():
	print("hhmm")
	return "Hello World!"

@app.route("/hook", methods=['POST'])
def hook():
	json = flask.request.get_json()
	
	success, log = authenticate(json)

	if success:
		repo_name = json["repository"]["full_name"]
		existing_bot = db.bots.find_one({"_id": repo_name})
		
		if existing_bot is None:
			existing_bot = {"_id": repo_name}
		
		existing_bot["repository"] = json["repository"]
		existing_bot["head"] = json["after"]
		existing_bot["status"] = "building"
		
		db.bots.replace_one({"_id": repo_name}, existing_bot, upsert=True)
		
		worker.enqueue(pull_and_build, existing_bot)
	else:
		print(log)
	
	return ""
