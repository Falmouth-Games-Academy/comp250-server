import pymongo
import os
import shutil
import subprocess

DB_NAME = 'comp250_grading'
client = pymongo.MongoClient()
client.drop_database(DB_NAME)
db = client[DB_NAME]

TOURNAMENT_PATH = '../tournament_grading'

for dir in os.listdir(TOURNAMENT_PATH):
    if dir == 'matches' or dir == 'broken':
        continue
    
    dirpath = os.path.join(TOURNAMENT_PATH, dir)
    if not os.path.isdir(dirpath):
        continue
    
    print("=" * 80)
    print(dirpath)
    print("=" * 80)

    # Copy MicroRTS
    dest = os.path.join(dirpath, "microrts")
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree("../comp250-microrts", dest)
    
    # Build
    subprocess.check_call(["ant", "-buildfile", "bot", "clean", "build", "jar"], cwd=dirpath)
    bot_id = dir + "+submission"
    # run_matches.py expects bot_id + '+' + bot["head"][:10] + '.jar'
    jar_path = os.path.join(TOURNAMENT_PATH, bot_id + "+0000000000.jar")
    shutil.copyfile(os.path.join(dirpath, "bot", "bot.jar"), jar_path)
    
    # Find class names
    class_names = subprocess.check_output(
        ["java", "-cp", "microrts.jar:lib/*", "comp250.ListTournamentAIsInJar", jar_path],
        cwd="../comp250-microrts",
        encoding="utf-8"
    )
    
    class_names = [name for name in class_names.split('\n') if name != ""]
    print(class_names)
    
    if len(class_names) != 1:
        raise Exception("Multiple bot classes are defined")
    
    bot = {
        "_id": dir + "+submission",
        "head": "0" * 40,
        "status": "ready",
        "build_log": "",
        "class_names": class_names
    }
    
    db.bots.insert_one(bot)
    