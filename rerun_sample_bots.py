from sample_bots import sample_bots
import webhook

webhook.delete_matches(sample_bots["_id"])
webhook.generate_matches(sample_bots["_id"])

