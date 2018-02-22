import flask
import pymongo

from db import db

app = flask.Flask(__name__)

@app.route("/")
def leaderboard():
	stats = list(db.stats.find({}, sort=[("elo", pymongo.DESCENDING)]))
	
	for stat in stats:
		stat["author"], stat["repo_name"], stat["class_name"] = stat["_id"].split('+')
	
	return flask.render_template("index.html", stats=stats)

# Import other app routes
import webhook

