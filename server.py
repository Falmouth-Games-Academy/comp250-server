import flask
import pymongo
import subprocess

from worker import WorkerThread

# Change these if necessary
JAVA_HOME = r"C:\Program Files\Java\jdk1.8.0_161"
ANT_HOME = os.path.abspath("..\..\apache-ant-1.10.1")

os.environ["JAVA_HOME"] = JAVA_HOME
os.environ["ANT_HOME"] = ANT_HOME
ANT_BAT = os.path.join(ANT_HOME, "bin", "ant.bat")

app = flask.Flask(__name__)

client = pymongo.MongoClient()
db = client.comp250

worker = WorkerThread()
worker.daemon = True
worker.start()

def run_commands(working_dir, commands):
	output = []
	
	for command in commands:
		output.append('-' * 80)
		output.append(working_dir + '> ' + ' '.join(command))
		
		result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", cwd=working_dir)
		output.append(result.stdout)
		
		if result.returncode != 0:
			output.append('-' * 80)
			output.append("Failed with error code {}".format(result.returncode))
			return (False, '\n'.join(output))
	
	return (True, '\n'.join(output))
	

def pull_and_build(bot):
	clone_path = os.path.join("..", "tournament", bot["_id"].replace("/", "+"))
	commands = []
	
	if not os.path.exists(clone_path):
		os.mkdir(clone_path)
		commands = [
			["git", "init"],
			["git", "remote", "add", "origin", bot["repository"]["clone_url"]]
		]
	else:
		commands = [
			["git", "clean", "-fdx"],
		]
	
	commands += [
		["git", "fetch"],
		["git", "reset", "--hard", bot["head"]],
		["git", "submodule", "update"],
		[ANT_BAT, "clean", "build", "jar"]
	]

	success, build_log = run_commands(clone_path, git_commands)
	
	status = "ready" if success else "error"
	
	db.bots.update_one(
		{"_id": bot["_id"]},
		{"$set": {
			"status": status,
			"build_log": build_log
		}
	})

	return success

@app.route("/")
def hello():
	print("hhmm")
	return "Hello World!"

@app.route("/hook", methods=['POST'])
def hook():
	json = Flask.request.get_json()
	
	repo_name = json["repository"]["full_name"]
	existing_bot = db.bots.find_one({"_id": repo_name})
	
	if existing_bot is None:
		existing_bot = {"_id": repo_name}
	
	existing_bot["repository"] = json["repository"]
	existing_bot["head"] = json["after"],
	existing_bot["status"] = "building"
	
	db.bots.replace_one({"_id": repo_name}, existing_bot, upsert=True)
	
	worker.enqueue(pull_and_build, existing_bot)
	
	return ""
