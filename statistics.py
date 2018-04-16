from db import db
import pymongo


def average(seq):
    s = None
    n = 0
    
    for x in seq:
        if n == 0:
            s = x
        else:
            s += x
        n += 1
    
    if n > 0:
        return s / n
    else:
        return 0.0


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
    
    result["queued"] = db.match_queue.find({"players": player_id}).count()
    
    #result["average_match_time"] = average(m["end_time"] - m["start_time"] for m in db.match_history.find({"players": player_id}))
    
    return result


def set_stats(stats):
    db.stats.replace_one({"_id": stats["_id"]}, stats, upsert=True)


def update_stats(matches):
    touched_stats = {}
    
    for match in matches:
        for player in match["players"]:
            if player not in touched_stats:
                touched_stats[player] = get_stats(player)
        
        player_stats = [touched_stats[player] for player in match["players"]]
        
        winner = match["result"]["winner"]
    
        # Update elo and win/draw/loss counts
        # Elo calculation based on:
        # https://metinmediamath.wordpress.com/2013/11/27/how-to-calculate-the-elo-rating-including-example/
        rating = [10.0 ** (stat["elo"] / 400.0) for stat in player_stats]
    
        for i in range(len(player_stats)):
            expected = rating[i] / sum(rating)
            if winner == 0:
                player_stats[i]["drawn"] += 1
                actual = 0.5
            elif winner == i+1:
                player_stats[i]["won"] += 1
                actual = 1.0
            else:
                player_stats[i]["lost"] += 1
                actual = 0.0

            player_stats[i]["elo"] += 32 * (actual - expected)
    
        if "disqualified" in match["result"]:
            i = match["result"]["disqualified"] - 1
            player_stats[i]["lost"] -= 1
            player_stats[i]["disqualified"] += 1
    
    for stat in touched_stats.values():
        set_stats(stat)


def reset_stats():
    db.stats.drop()
    
    update_stats(db.match_history.find({}, sort=[("end_time", pymongo.ASCENDING)]))
    