import time as tm


class Timer:

    def __init__(self):

        self.time_start = tm.time()

    def get_time(self):

        time_end = tm.time() - self.time_start

        return time_end

