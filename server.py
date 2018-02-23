import flask
import pymongo

from db import db
import stats

app = flask.Flask(__name__)

@app.route("/")
def leaderboard():
	stats = list(db.stats.find({}, sort=[("elo", pymongo.DESCENDING)]))
	
	return flask.render_template("index.html", stats=stats)


@app.route("/bot/<bot_id>")
def bot_info(bot_id):
	bot = db.bots.find_one({"_id": bot_id})
	
	if bot is not None:
		bot_stats = [stats.get_stats({"bot": bot_id, "class_name": class_name}) for class_name in bot["class_names"]]
		bot_stats.sort(key = lambda s: s["elo"], reverse = True)
		return flask.render_template("bot_info.html", bot=bot, stats=bot_stats)
	else:
		return flask.render_template("error.html", message="No bot named '%s'" % bot_id)


@app.route("/static/<path:path>")
def static_file(path):
	return flask.send_from_directory("static", path)


# Import other app routes
import webhook

