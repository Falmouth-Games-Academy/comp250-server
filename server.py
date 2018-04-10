import flask
import os
import time

from db import db
import statistics

app = flask.Flask(__name__)


@app.template_filter('ctime')
def timectime(s):
    return time.ctime(s) # datetime.datetime.fromtimestamp(s)


@app.route("/")
def leaderboard():
    stats = [statistics.get_stats(bot["_id"] + '+' + class_name)
             for bot in db.bots.find({})
             for class_name in (bot.get("class_names") or [])]
    
    for stat in stats:
        author, bot_id, class_name = stat["_id"].split('+')
        stat["bot"] = db.bots.find_one({"_id": author + '+' + bot_id})
    
    stats.sort(key=lambda s: s["elo"], reverse=True)
    
    unready_bots = list(db.bots.find({"status": {"$ne": "ready"}}))
    
    matches_left = db.match_queue.find({}).count()
    if matches_left > 0:
        time_left = matches_left * statistics.average(m["end_time"] - m["start_time"] for m in db.match_history.find({}))
    else:
        time_left = None

    return flask.render_template("index.html", stats=stats, unready_bots=unready_bots, time_left=time_left)


@app.route("/bot/<bot_id>")
def bot_info(bot_id):
    bot = db.bots.find_one({"_id": bot_id})

    if bot is not None:
        bot_stats = [statistics.get_stats(bot_id + '+' + class_name) for class_name in bot["class_names"]]
        bot_stats.sort(key = lambda s: s["elo"], reverse = True)
        return flask.render_template("bot_info.html", bot=bot, stats=bot_stats)
    else:
        return flask.render_template("error.html", message="No bot named '%s'" % bot_id)


@app.route("/history/<bot_class_id>")
def history(bot_class_id):
    matches = list(db.match_history.find({"players": bot_class_id}))

    queued_matches = list(db.match_queue.find({"players": bot_class_id}))
    for match in queued_matches:
        match["is_queued"] = True

    matches += queued_matches

    for match in matches:
        match["map_short"] = os.path.splitext(os.path.basename(match["map"]))[0]
        match["this_player_index"] = match["players"].index(bot_class_id)

    return flask.render_template("history.html", matches=matches)


@app.route("/trace_dl/<zipname>")
def trace_download(zipname):
    return flask.send_from_directory("../tournament/matches", zipname)


@app.route("/static/<path:path>")
def static_file(path):
    return flask.send_from_directory("static", path)


# Import other app routes
import webhook


webhook.update_all_bots()
