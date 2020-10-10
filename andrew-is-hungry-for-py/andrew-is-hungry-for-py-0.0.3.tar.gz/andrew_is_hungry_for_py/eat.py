from dateutil.parser import parse


def feedme(inputdate):
    datetime = parse(inputdate).date()
    day = datetime.day
    month = datetime.month

    if day == 31 and month == 10:
        return "Birthday Cake"

    if day == 1 and month == 11:
        return "Leftover Birthday Cake"

    return "Cake"
