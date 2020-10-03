"""
@author: RealStickman
"""
import configparser
import multiprocessing
import sys
import praw
import prawcore
import requests
import os
from datetime import date
import argparse
from pathlib import Path
from PIL import Image

#put this into a third python file
def readconf():
    print("Reading Config file")
    config.read('grab.ini')
    global lim
    lim = int(config['CONFIG']['limit'])
    global category
    category = config['CONFIG']['category']
    global subl
    subl = config['CONFIG']['subs']
    global sublist
    sublist = subl.replace('.empty.', '')
    global sublf
    sublf = list(filter(None, sublist.split(';')))
    global path
    path = config['CONFIG']['path']
    global seltheme
    seltheme = config['CONFIG']['theme']

#Write the configuration file
def writeconf():
    print("Writing config file")
    config['CONFIG'] = {'limit': lim,
                        'category': category,
                        'subs': sublist,
                        'path': path,
                        'theme': seltheme}
    with open('grab.ini', 'w') as configfile:
        config.write(configfile)

###########
#variables#
###########

#colors for terminal output
CRED = '\033[91m'
CYEL = '\033[33m'
CGRE = '\033[92m'
CEND = '\033[0m'
#define config and read subs
config = configparser.ConfigParser()
#choose default path
pathdef = str(os.path.join(Path.home(), "Downloads", "grab-bot"))

############
#Initialise#
############

try:
    config.read('grab.ini')
    config['CONFIG']['category']
    # #read subs into list
    # subl = config['CONFIG']['subs']
    # sublist = subl.replace('.empty.', '')
    # sublf = list(filter(None, sublist.split(';')))
    # #reads limit
    # lim = int(config['CONFIG']['limit'])
    # #category
    # category = config['CONFIG']['category']
    # #read path
    # path = config['CONFIG']['path']
except KeyError:
    config['CONFIG'] = {'limit': '10',
                        'category': 'hot',
                        'subs': '.empty.;',
                        'path': pathdef,
                        'theme': 'light'}
    with open('grab.ini', 'w') as configfile:
        config.write(configfile)
    print("Created default configuration file")
    # print(CRED + "Please create a grab.ini file by launching gui.py first." + CEND)
    # sys.exit(1)
finally:
    readconf()

#################
#Argument parser#
#################

parser = argparse.ArgumentParser(description='CLI-options for grab.py.', formatter_class=argparse.RawDescriptionHelpFormatter)
g = parser.add_argument_group(title='information options',
description =
'''-s, -sub <subreddit>        Add subreddits (Multiple allowed)   
-l, --lim <limit>           Set the limit of posts  
-c, --category <category>   Set the category
-p, --path <path>           Set the download path''')

parser.add_help
g.add_argument("-s", "--sub", dest="subreddit", type=str, nargs='+', required=False, help=argparse.SUPPRESS)
g.add_argument("-l", "--lim", dest="limit", type=int, required=False, help=argparse.SUPPRESS)
g.add_argument("-c", "--category", dest="category", type=str, required=False, help=argparse.SUPPRESS)
g.add_argument("-p", "--path", dest="path", type=str, required=False, help=argparse.SUPPRESS)

args = parser.parse_args()
# print(args.subreddits)

argsubs = args.subreddit
#try getting an argument and add that to the list
if argsubs is not None:
    for s in range(len(argsubs)):
        try:
            #reddit stuff
            reddit = praw.Reddit(client_id="48VCokBQkKDsEg",
                                 client_secret=None,
                                 user_agent="grab, a Reddit download bot by /u/RealStickman_")

            subreddit = reddit.subreddit(argsubs[s])
            subreddit.title

            #add entered subreddit
            sublist += subreddit.display_name + ";"
            #that's were we're gonna put it
            print("Added " + subreddit.display_name)
        #if the subreddit can't be found
        except prawcore.exceptions.Redirect:
            print("Wrong Subreddit", subreddit.display_name + " does not exist")

    #recreate a string from the list
    #sublist = ";"+ ';'.join(sublf) + ";"
    # print("sublist " + sublist)
    #writeconf()
else:
    print("No subreddit given")

# print(sublf)

arglim = args.limit
#try getting a limit
if arglim is not None:
    lim = args.limit
else:
    print("No limit given")

argcategory = args.category
#try getting a category
if argcategory is not None:
    category = args.category
else:
    print("No category given")

argpath = args.path
#try getting a path
if argpath is not None:
    path = args.path
else:
    print("No path given")

writeconf()

readconf()

#number of subreddits that have been specified in the config
numsubs = len(sublf)
#date for folder creation
date = str(date.today())

def dl(subvar):
    # make path choosable
    pathdl = str(os.path.join(path, subvar, date))
    if not os.path.exists(pathdl):
        os.makedirs(pathdl)
    pathtxt = str(os.path.join(path, subvar))
    os.chdir(pathtxt)

    reddit = praw.Reddit(client_id="48VCokBQkKDsEg",
                         client_secret=None,
                         user_agent="grab, a Reddit download bot by /u/RealStickman_")

    # setting subreddit and variable for the first few posts in the hot category of it
    subreddit = reddit.subreddit(subvar)

    if category == 'controversial':
        print(category)
        posts = subreddit.controversial(limit=lim)
    elif category == 'gilded':
        print(category)
        posts = subreddit.gilded(limit=lim)
    elif category == 'hot':
        print(category)
        posts = subreddit.hot(limit=lim)
    elif category == 'new':
        print(category)
        posts = subreddit.new(limit=lim)
    elif category == 'rising':
        print(category)
        posts = subreddit.rising(limit=lim)
    elif category == 'top':
        print(category)
        posts = subreddit.top(limit=lim)
    else:
        print('This category is not implemented or does not exist')

    #test whether the subreddit exists
    try:
        subreddit.title
    except prawcore.exceptions.Redirect:
        print(CRED + subreddit.display_name + " is no subreddit" + CEND)
        return
    
    #creates downloaded.txt in the subreddit's directory
    try:
        downloaded = open("downloaded.txt")
        print("File exists")
        print("Downloading from " + subreddit.display_name)
    except IOError:
        print("Creating file")
        downloaded = open("downloaded.txt", "w")
        downloaded.write("")
        print("Downloading from " + subreddit.display_name)
    finally:
        downloaded.close()

    #searches the specified number of posts
    for post in posts:
        url = post.url
        filename = post.author.name + " - " + post.title + ".png"
        filetest = post.title
        downloaded = open("downloaded.txt", "r")
        string = str(downloaded.read())
        downloaded.close()
        if filetest not in string:
            print(CGRE + filename + CEND)
            reddit = requests.get(url)
            #download files from reddit
            os.chdir(pathdl)
            try:
                with open(filename, "wb") as file:
                    file.write(reddit.content)
                try:
                    Image.open(filename)
                except:
                    os.remove(filename)
                    print("Removed " + filename + ", because it is not an image.")
            except IOError:
                print("Couldn't find any picture, skipping.")
            #appends the filenames
            os.chdir(pathtxt)
            with open("downloaded.txt", "a") as downloaded:
                downloaded.write(post.title)
                downloaded.write(" ")
        else:
            print(CYEL + filename + " is already present in downloaded.txt" + CEND)

def main():
    global numsubs
    global dl
    global sublf

    #creates a pool of processes
    try:
        p = multiprocessing.Pool(numsubs)
        #processes are started with the arguments contained in the list
        p.map(dl, sublf)
    except ValueError:
        print(CRED + "Please specify a subreddit." + CEND)
    exit(0)

if __name__ == '__main__':
    main()
