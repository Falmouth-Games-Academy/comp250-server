from db import db

def get_stats(player_id):
	result = db.stats.find_one({"_id": player_id})
	if result is None:
		result = {
			"_id": player_id,
			"elo": 1000.0,
			"won": 0,
			"lost": 0,
			"drawn": 0,
			"disqualified": 0
		}
	
	return result


def set_stats(stats):
	db.stats.replace_one({"_id": stats["_id"]}, stats, upsert=True)


def update_stats(match):
	stats = [get_stats(player) for player in match["players"]]
	
	winner = match["result"]["winner"]
	
	# Update elo and win/draw/loss counts
	# Elo calculation based on https://metinmediamath.wordpress.com/2013/11/27/how-to-calculate-the-elo-rating-including-example/
	rating = [10.0 ** (stat["elo"] / 400.0) for stat in stats]
	
	for i in range(len(stats)):
		expected = rating[i] / sum(rating)
		if winner == 0:
			stats[i]["drawn"] += 1
			actual = 0.5
		elif winner == i+1:
			stats[i]["won"] += 1
			actual = 1.0
		else:
			stats[i]["lost"] += 1
			actual = 0.0
		
		stats[i]["elo"] += 32 * (actual - expected)
	
	if "disqualified" in match["result"]:
		i = match["result"]["disqualified"] - 1
		stats[i]["lost"] -= 1
		stats[i]["disqualified"] += 1
	
	for stat in stats:
		set_stats(stat)
	

