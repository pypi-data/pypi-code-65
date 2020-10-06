import json
import praw
from .civility_db import CivilityDB
import datetime
from .tools import Tools
import os


class RedditCrawler:
    reddit_auth = json.loads(os.environ.get("REDDIT"))
    reddit = praw.Reddit(user_agent=reddit_auth["user_agent"],
                         client_id=reddit_auth["client_id"], client_secret=reddit_auth["client_secret"],
                         username=reddit_auth["username"], password=reddit_auth["password"])

    @staticmethod
    def get_history(post):
        comment = RedditCrawler.reddit.comment(id=post["reddit_id"])
        trigger, flag = comment.parent(), comment.parent().parent()
        CivilityDB.update(doc=post, collection="bot")
        return trigger, flag

    @staticmethod
    def check_new_score(r_id):
        return RedditCrawler.reddit.comment(id=r_id).score

    @staticmethod
    def find_bot_id(trigger_id):
        bot_posts = RedditPoster.reddit.redditor("gild_civility").comments.new(limit=None)
        for bot_post in bot_posts:
            if bot_post.parent_id.split("_")[1] == trigger_id:
                return bot_post.id
        return "bot_id_not_found"

    class CivilitySearch:
        @staticmethod
        def process_triggers(obj):
            # Determine whether a comment with '/u/Gild-Civility' meets the criteria to create a solicitation post
            rejection = []
            comment_age = datetime.datetime.utcnow() - datetime.datetime.strptime(obj["posted_at"],
                                                                                  "%Y-%m-%d %H:%M:%S")
            tools = CivilityDB.get_tools()
            if comment_age < datetime.timedelta(hours=tools["min_ages"][obj["subreddit"]]):
                rejection.append("age")

            if len("".join(obj["body"].split())) < 50:  # 50 letters minimum (average of ~10 words)
                rejection.append("length")

            if obj["forest_depth"] > 6:
                rejection.append("depth")

            if obj["score"] <= 1:
                rejection.append("score")

            if obj["forest_depth"] == 0:
                rejection.append("no_parent")
            now = Tools.now
            obj.update({"bot_ready": not(len(rejection)),
                        "rejection_reasons": rejection,
                        "created_at": now,
                        "updated_at": now,
                        "bot_id": None
                        })
            print("Civility Identified!!\n" + obj["reddit_id"])
            return obj


# Controller
class RedditPoster(RedditCrawler):
    @staticmethod
    def post_to_reddit(post, reddit_id):
        posts = CivilityDB.get_post_parts()
        trigger = RedditPoster.reddit.comment(id=reddit_id)
        header = posts["header"] + "  \n"
        footer = "  \n" + posts["footer"]
        full_post = header + post + footer
        # print(full_post)  # print for testing... reddit call in the future
        # bot_reddit_id = str(random.randint(1, 1000))  # Unit test

        try:
            trigger.reply(full_post)
        except Exception as error:
            if "deleted" in error.message:
                return "trigger_deleted"
            elif "history now; it's too late" in error.message:
                return "trigger_archived"
            else:
                return {"status_code": 429, "error": error}
                #  trigger.reply(full_post)

        bot_id_error = "bot_id_not_found"
        bot_reddit_id = RedditCrawler.find_bot_id(reddit_id)

        if bot_reddit_id == bot_id_error:
            print(bot_id_error)
        now = Tools.now
        doc = {"created_at": now,
               "updated_at": now,
               "initial_poem": {"header": header,
                                "body": post,
                                "footer": footer},
               "gilding_poem": None,
               "scores": [{"checked_at": now, "score": 1}],
               "reddit_id": bot_reddit_id}

        return CivilityDB.insert(payload=doc, collection="bot"), None
