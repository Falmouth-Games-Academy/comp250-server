import flask
import subprocess
import os
import urllib
import json
import random
import re
from urllib.parse import urlparse

from config import config
from worker import WorkerThread
from server import app
from db import db
import statistics
from sample_bots import sample_bots


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
            return False, '\n'.join(output)

    return True, '\n'.join(output)


def is_github_url(url):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc.split('.')
    return len(netloc) >= 2 and netloc[-2] == "github" and netloc[-1] == "com"


def authenticate(bot):
    if not is_github_url(bot["repository"]["clone_url"]):
        return False, "Cannot clone from a non-GitHub URL"
    
    if bot["repository"]["owner"]["name"] != "Falmouth-Games-Academy":
        from db import allowed_users
        if not any(u for u in allowed_users if u["login"].lower() == bot["repository"]["owner"]["name"].lower()):
            print(bot["repository"]["owner"]["name"], "is not an allowed user")
            return False, bot["repository"]["owner"]["name"] + " is not an allowed user"

    return True, ""


def delete_matches(bot_id):
    # Search for matches where the player name begins with "{bot_id}+"
    regex = "^" + re.escape(bot_id) + r"\+"

    result = db.match_queue.delete_many({"players": {"$regex": regex}})
    print("Deleted", result.deleted_count, "queued matches")

    result = db.match_history.delete_many({"players": {"$regex": regex}})
    print("Deleted", result.deleted_count, "historical matches")
    
    statistics.reset_stats()
    

def generate_matches(bot_id):
    from db import maps

    bot = db.bots.find_one({"_id": bot_id})
    other_bots = list(db.bots.find({"_id": {"$ne": bot_id}}))

    pairings = []
    
    # Matches between classes within the bot
    for class_a in bot["class_names"]:
        for class_b in bot["class_names"]:
            if class_a != class_b:
                pairings.append((bot_id + '+' + class_a, bot_id + '+' + class_b))

    # Matches between different bots
    for class_a in bot["class_names"]:
        for bot_b in other_bots:
            for class_b in bot_b["class_names"]:
                pairings.append((bot_id + '+' + class_a, bot_b["_id"] + '+' + class_b))
                pairings.append((bot_b["_id"] + '+' + class_b, bot_id + '+' + class_a))

    from pprint import pprint
    pprint(pairings)
    
    for pairing in pairings:
        for map_name in maps:
            match = {
                "players": list(pairing),
                "map": map_name,
                "random": random.random()
            }
            db.match_queue.insert_one(match)

    db.match_queue.create_index("random")
    db.match_queue.create_index("players")


def pull_and_build(bot):
    delete_matches(bot["_id"])

    clone_path = os.path.join(config.tournament_dir_path, bot["_id"])

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
            ["git", "reset", "--hard", bot["head"]],
            ["git", "submodule", "update", "--init", "--recursive"]
        ]

    jar_name = bot["_id"] + "+" + bot["head"][:10] + ".jar"

    commands += [
        ["ant", "-buildfile", "bot", "clean", "build", "jar"],
        ["cp", "-v", os.path.join("bot", "bot.jar"),
            os.path.join("..", jar_name)]
    ]

    success, build_log = run_commands(clone_path, commands)
    class_names = []

    if success:
        command = ["java", "-cp", "microrts.jar:lib/*", "comp250.ListTournamentAIsInJar",
                   os.path.join(config.tournament_dir_path, jar_name)]
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

    if success:
        generate_matches(bot["_id"])

    print("pull_and_build finished")
    return success


if config.enable_webhook:
    @app.route("/hook", methods=['POST'])
    def hook():
        request_json = flask.request.get_json()
        
        if "zen" in request_json: # ping
            return "pong"
        
        if request_json["ref"] == "refs/heads/master":
            success, log = authenticate(request_json)
        
            if success:
                bot_id = request_json["repository"]["full_name"].replace('/', '+')
                existing_bot = db.bots.find_one({"_id": bot_id})
        
                if existing_bot is None:
                    existing_bot = {"_id": bot_id}
        
                existing_bot["repository"] = request_json["repository"]
                existing_bot["head"] = request_json["after"]
                existing_bot["status"] = "building"
        
                db.bots.replace_one({"_id": bot_id}, existing_bot, upsert=True)
        
                worker.enqueue(pull_and_build, existing_bot)
            else:
                print(log)
    
        return ""


@app.route("/rerun_sample_bots")
def rerun_sample_bots():
    delete_matches(sample_bots["_id"])
    generate_matches(sample_bots["_id"])
    return "OK"


@app.route("/rerun_all_bots")
def rerun_all_bots():
    db.match_queue.drop()
    db.match_history.drop()
    
    for bot in db.bots.find({}):
        generate_matches(bot["_id"])

    return "OK"


def update_all_bots():
    db.bots.replace_one({"_id": sample_bots["_id"]}, sample_bots, upsert=True)
    
    if config.enable_git:
        for bot in db.bots.find({}):
            if bot["_id"] == sample_bots["_id"]:
                continue
    
            clone_path = os.path.join(config.tournament_dir_path, bot["_id"])
            if not os.path.exists(clone_path):
                print("Forcing update for", bot["_id"])
                pull_and_build(bot)
            else:
                try:
                    branch_url = bot["repository"]["branches_url"].replace("{/branch}", "/master")
                    print("Fetching", branch_url)
                    with urllib.request.urlopen(branch_url) as resp:
                        branch = json.load(resp)
                    if branch["commit"]["sha"] != bot["head"]:
                        print("Updating", bot["_id"])
                        bot["head"] = branch["commit"]["sha"]
                        db.bots.replace_one({"_id": bot["_id"]}, bot)
                        pull_and_build(bot)
                    else:
                        print(bot["_id"], "is up to date")
                except Exception as e:
                    print("Error updating", bot["_id"])
                    print(e)
