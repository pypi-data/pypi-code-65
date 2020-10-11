import re
import classes

REGEX = re.compile(r'{\s*quote:\s*"([^"]*)"\s+author:\s*{\s*last_name:\s*"([^"]*)"\s+first_name:\s*"([^"]*)"\s*}\s+date:\s*({\s*year:\s*(\d{4})\s+month:\s*(\d{1,2})\s+day:\s*(\d{1,2})\s*})?(\s+context:\s*"([^"]*)")?\s*}')

def parse(filename):
    with open(filename,"r") as chris_file:
        groups = re.search(REGEX,chris_file.read())
        if groups:
            quote = groups.group(1)
            last_name = groups.group(2)
            first_name = groups.group(3)
            year = groups.group(5)
            month = groups.group(6)
            day = groups.group(7)
            context = groups.group(9)
            author = classes.Author(last_name,first_name)
            date = classes.Date(year,month,day)
            return classes.Chris(quote,author,date,context)
        else:
            raise Exception('InvalidFile')