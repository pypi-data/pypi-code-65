import feedparser

def setup():
    entries = feedparser.parse('http://feeds.bbci.co.uk/news/world/rss.xml')['entries']
    list = []
    for i in range(len(entries)):
        list.append(entries[i])
    return(list)

def title():
    list = []
    for i in range (len(setup())):
        list.append((setup()[i]['title']))
    return(list)

def description():
    list = []
    for i in range (len(setup())):
        list.append((setup()[i]['summary']))
    return(list)

def link():
    list = []
    for i in range (len(setup())):
        list.append((setup()[i]['links'][0]['href']))
    return(list)
