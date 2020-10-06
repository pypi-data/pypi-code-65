from pymongo import MongoClient
import os
from .tools import Tools
from bson import ObjectId
import time


class CivilityDB:
    mongo_auth = os.environ.get("MONGO")
    mongo = MongoClient(mongo_auth)
    trigger = mongo.civility.trigger
    flag = mongo.civility.flag
    bot = mongo.civility.bot
    post = mongo.civility.post

    @staticmethod
    def get_post_parts():
        posts = dict()
        for part in CivilityDB.mongo.civility.post.find(CivilityDB.posts_query):
            posts[part["type"]] = part["body"]
            print("Mongo: found", part)
        return posts

    @staticmethod
    def get_tools():
        tools = dict()
        for tool in CivilityDB.mongo.civility.post.find(CivilityDB.tools_query):
            tools[tool["type"]] = tool["body"]
            print("Mongo: found", tool)
        return tools

    posts_query = {"type": {"$in": ["length", "score", "no_parent", "good", "header", "footer"]}, "active": True}
    tools_query = {"type": {"$in": ["subreddits", "min_ages", "bot_reddit_uid"]}, "active": True}
    ready_for_gilder = {"status": "ready", "gilding_poem": None, "notif": {"$ne": None}}

    bot_eval_search_strings = {"ready": {"bot_ready": True, "bot_id": None},
                               "recheck": {"bot_ready": False, "$or": [
                                   {"rejection_reasons": ["age", "score"]},
                                   {"rejection_reasons": "age"}]},
                               "reject": {"$and": [
                                  {"bot_ready": False},
                                  {"bot_id": None},
                                  {"$and": [{"rejection_reasons": {"$ne": ["age", "score"]}},
                                            {"rejection_reasons": {"$ne": "age"}}]}]
                                  }
                               }

    @staticmethod
    def insert(payload, collection):
        # should receive collection as a class (extend enum class in python)
        if len(payload):

            if collection == "trigger":
                print(collection, "Initiating Mongo Dump! (Heh.) Total documents:", len(payload))
                CivilityDB.trigger.insert_many(payload)
            elif collection == "flag":
                print(collection, "Initiating Mongo Dump! (Heh.) Total documents:", len(payload))
                CivilityDB.flag.insert_many(payload)
            elif collection == "bot":
                print(collection, "Initiating Mongo Dump! (Heh.) Total documents: 1")
                bot_id = CivilityDB.bot.insert_one(payload).inserted_id
                CivilityDB.mongo.close()
                return ObjectId(bot_id)
            CivilityDB.mongo.close()

    @staticmethod
    def update(doc, collection, inp=None, new_score=None, poem=None, notification_sid=None, rejection_reasons=None):
        now = Tools.now
        if collection == "trigger":
            doc = CivilityDB.handle_trigger(inp=inp, new_score=new_score, doc=doc, now=now)
            return doc
        if collection == "bot":
            if inp == "notif":
                CivilityDB.handle_notif(doc=doc, notification_sid=notification_sid, now=now, new_score=new_score)
            if inp == "gilding":
                CivilityDB.handle_gilding(doc=doc, now=now, poem=poem)
            return doc

    @staticmethod
    def handle_trigger(doc, inp, new_score, now):
        # Used to determine which document to update
        trigger_id = doc["_id"]
        if inp and not new_score:
            if inp != "trigger_deleted":
                # run this code to add the bot id to the document, showing that it has already had a post made
                doc["bot_id"] = inp
            else:
                # run this code if there was an error during the bot post
                doc["rejection_reasons"].append(inp)
        elif not new_score:
            pass
        elif new_score > 1:
            try:
                doc["rejection_reasons"].remove("score")
            except ValueError:
                print("ERR:", doc["subreddit"], "has the wrong value mapped for min_age")
                pass
            doc["rejection_reasons"].remove("age")
            print("This score improved. " + doc["reddit_id"])
            doc["bot_ready"] = True
        elif new_score <= 1:
            # This function will only be called on documents that have already passed the age test
            doc["rejection_reasons"].remove("age")

        doc["updated_at"] = now

        try:
            CivilityDB.trigger.update_one({"_id": ObjectId(trigger_id)}, {"$set": doc})
        except MongoClient.errors.ServerSelectionTimeoutError:
            print("CivilityDB.errors.ServerSelectionTimeoutError")
            x = 2
            while x < 300:
                print("Write attempt failed for {}. Trying again in {} seconds".format(trigger_id, x))
                time.sleep(x)
                x *= 2
                try:
                    CivilityDB.trigger.update_one({"_id": ObjectId(trigger_id)}, {"$set": doc})
                    return doc
                except MongoClient.errors.ServerSelectionTimeoutError:
                    continue
            print("Database not responding.")

        return doc

    @staticmethod
    def handle_notif(doc, notification_sid, now, new_score):
        CivilityDB.bot.update_one(doc, {"$set":
                                            {"notif": notification_sid,
                                             "updated_at": now},
                                        "$push":
                                            {"scores":
                                                 {"$each":
                                                      [{"checked_at": now, "score": new_score}]
                                                  }
                                             }
                                        }
                                  )

    @staticmethod
    def handle_gilding(doc, poem, now):
        CivilityDB.bot.update_one({"reddit_id": doc},
                                  {"$set": {"status": "done", "gilding_poem": poem, "updated_at": now}})

    @staticmethod
    def find_comment(trigger_id):
        trigger = CivilityDB.trigger.find_one({"reddit_id": trigger_id})
        bot = CivilityDB.bot.find_one({"_id": ObjectId(trigger["bot_id"])})
        return bot["reddit_id"], trigger["flag_id"]
