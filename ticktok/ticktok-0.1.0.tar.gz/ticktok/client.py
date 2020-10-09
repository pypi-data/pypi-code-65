class ClockRegisterError(Exception):
    pass


class Ticktok:

    def schedule(self, name, schedule):
        raise ClockRegisterError()
