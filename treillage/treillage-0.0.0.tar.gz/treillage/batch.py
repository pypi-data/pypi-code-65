import datetime


class BatchIndex:
    def __init__(self, headers):
        self.headers = headers
        self.sections = {}
        self.fields = {}
        for i, val in enumerate(headers):
            items = val.split(".")
            if len(items) > 1:
                if items[0] not in self.sections:
                    self.sections[items[0]] = []
                self.sections[items[0]].append(i)
                self.fields[i] = items[1]

    def __repr__(self):
        return "sections:\t{}\nfields:\t{}".format(self.sections, self.fields)


def serialize_helper(o=None):
    if isinstance(o, datetime.datetime):
        return o.__str__()
