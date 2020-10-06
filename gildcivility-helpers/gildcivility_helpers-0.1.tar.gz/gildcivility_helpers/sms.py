from twilio.rest import Client
import json
from twilio.twiml.messaging_response import MessagingResponse
import os
from .civility_db import CivilityDB


class Twilio:
    twilio_auth = json.loads(os.environ.get("TWILIO"))
    twilio_client = Client(twilio_auth["account_sid"], twilio_auth["auth_token"])

    @staticmethod
    def notification(trigger, flag):
        sep = "\n==========\n"
        return_id = "First, paste the above into your response on its own line:"
        body = return_id + sep + "Flagged for Civlity:\n" + flag.body + sep + "Flagged by:\n" + trigger.body
        for msg in [str(trigger.id), body]:
            message = Twilio.twilio_client.messages.create(
                from_=os.environ.get("TWILIO_FROM"),
                body=msg,
                to=os.environ.get("TWILIO_TO")
            )
        print("Poem Prompter sent:", message.sid)
        return message.sid

    @staticmethod
    def poem_return(response):
        # Get the poem the user sent our Twilio number
        body = response
        trigger_id = body.split('\n')[0]
        reddit_bot_id, reddit_flag_id = CivilityDB.find_comment(trigger_id)

        poem = '  \n'.join(body.split('\n')[1:])

        resp = MessagingResponse()
        resp.message("Thank you for your contribution!")

        return poem, reddit_bot_id, reddit_flag_id
