from gmrs.model.property import Property


class WorldMap:
    def __init__(self, args):
        for arg in args:
            map['poi1']['poi2'] = Property('distrance', args['distance'][0], args['distance'][1])

    def getDistance(self, poi1, poi2):
        return self[poi1][poi2]


def create_map(args):
    return WorldMap(args)
