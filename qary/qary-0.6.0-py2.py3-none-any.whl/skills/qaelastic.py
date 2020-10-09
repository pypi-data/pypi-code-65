""" Transformer based chatbot dialog engine for answering questions with ElasticSearch of Wikipedia"""

import logging
from qary.skills.qa import Skill

log = logging.getLogger(__name__)


def test_reply():
    bot = Skill()
    answers = bot.reply('What is natural language processing?')
    print(answers)
