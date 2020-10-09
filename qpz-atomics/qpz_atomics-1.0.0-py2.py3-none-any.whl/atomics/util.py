class Util:
    def __init__(self, _):
        def qrng() :

            """
            return random 0 or 1 via hadarmard gate
            param:
                location_strings: string, node where the q.h is happening, 'Alice' by default

            """
            q=_.PREP()
            _.H(q)
            number = _.MEAS()
            print('Outcome of the measure:', number)
            return number

        self.qrng = qrng


