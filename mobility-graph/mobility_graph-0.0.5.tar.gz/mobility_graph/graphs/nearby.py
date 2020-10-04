from .graph import Graph

class Nearby(Graph):
    """
        This class adapts OSM or OSRM walk routing

        And is going to be used for locations that are not in the vertices.
        Inspiration and source for some pieces of code:
        https://github.com/SAUSy-Lab/nearby-transit-trip-frequency/blob/0c38df7ef149291e8dbd3fad06db26b0de50dd17/nearby_stops.py
    """

    def __init__(self):
        """
        Initialize graph objects
        """
        Graph.__init__(self)

    def findNearby(self, gtfs, origin_x, origin_y, distance):
        """
        To find nearby stations
        Distance is an input that we can use to define a distance Threshold
        But we can also define a distance limit from the beginning
        or check the routing walking time and limit by walking time limit

        """

        walk_speed = 1.3

        stops = gtfs + "/stops.txt"

        # grab locations of all stops
        stop_locations = []
        with open(stops, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:

                xs = float(row["stop_lon"])
                ys = float(row["stop_lat"])

                if compute_HS(origin_x, origin_y, xs, ys) < distance * 3:
                    # some if for distance threshold

                    stop_id = row["stop_id"]
                    stop_locations.append([stop_id, xs, ys])

        # grab string of all the coordinates - for plugging into OSRM url
        coord_str = str(origin_x) + ',' + str(origin_y) + ';'
        for row in stop_locations:
            coord_str = coord_str + str(row[1]) + ',' + str(row[2]) + ';'
        coord_str = coord_str[:-1]

        # grab list of destinations IDs for URL string
        distr = ''
        di = 1
        while di <= len(stop_locations):
            distr = distr + str(di) + ';'
            di += 1
        distr = distr[:-1]

        # url for OSRM request
        url = 'http://localhost:5000/table/v1/walking/' + \
            coord_str + '?sources=0&destinations=' + distr

        # getting the data via request and loading json into a python dict
        page = requests.get(url)
        data = json.loads(page.content)

        if len(stop_locations) != len(data['durations'][0]):
            return "at least one stop failed"

        c = 0

        out_stop_ids = []
        while c < len(stop_locations):
            duration = data['durations'][0][c]
            distance_to_stop = float(duration) * walk_speed
            stop_id = stop_locations[c][0]
            if distance_to_stop <= distance:
                out_stop_ids.append(stop_id)
            c += 1

        return out_stop_ids

    def walk(self):
        """
        Walk to nearby station using OSRM Api
        """
