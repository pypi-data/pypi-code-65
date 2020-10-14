import logging.config
from datetime import datetime, timedelta

from dateutil.rrule import rrule, MONTHLY

from XOTweet.core.scrap import scrapper
from XOTweet.core.settings import LOGGING_CONFIG
from XOTweet.input import parse_args


def main():
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    print("""
         _  _  _____     ____  _    _  ____  ____  ____ 
        ( \/ )(  _  )___(_  _)( \/\/ )( ___)( ___)(_  _)
         )  (  )(_)((___) )(   )    (  )__)  )__)   )(  
        (_/\_)(_____)    (__) (__/\__)(____)(____) (__) 
        """)

    # Parsing Input Arguments
    arguments, unknown = parse_args()
    # Dividing the date into months
    if arguments.From_Date:
        start = arguments.From_Date
        end = datetime.now() + timedelta(weeks=+4)
        dates = [dt for dt in rrule(MONTHLY, dtstart=start, until=end)]
    else:
        start = datetime(2019, 1, 1).date()
        end = datetime.now().date() + timedelta(weeks=+4)
        dates = [dt.date() for dt in rrule(MONTHLY, dtstart=start, until=end)]

    final_list = scrapper(arguments.Keyword, arguments.Exclude, dates, arguments.Threads)

    return final_list


if __name__ == "__main__":
    main()
