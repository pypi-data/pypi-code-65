import telegram
import feedparser
from telegram import ParseMode
import html2text
import random
import schedule
import time

def autoposting():
    with open('rss_feeds.txt') as file:
        list = file.readlines()

    feedlist = [list[i].rstrip() for i in range(len(list))]
    Feed = feedparser.parse(random.choice(feedlist))
    rands = random.randint(0, len(Feed.entries)-1)
    print(len(Feed.entries), rands)
    entry = Feed.entries[rands]
    print(entry.link)
    bot = telegram.Bot(token=TELEGRAM['bot_token'])
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    h.images_to_alt = True
    h.ignore_emphasis = True
    text = h.handle(entry.summary)
    msg = "\n\n"
    msg += '<b> {} </b>'.format(entry.title) + '\n\n' + '{}'.format(text)
    msg += "Read More:" + ' [<a href="'+ entry.link +'"> Source </a>]'
    msg += ' \n\n' + '#articles' + '\n\n' + 'Follow: @theTuringMachine'
    status = bot.send_message(chat_id=TELEGRAM['channel_name'], text = msg ,caption=msg, parse_mode=ParseMode.HTML)
    print('Posted!')
