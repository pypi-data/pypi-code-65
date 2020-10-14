class Machine:
    def __init__(self, id_machine, name=''):
        self._id = id_machine
        self._name = name

        # List of pairs when this machine is available.
        # If empty, this machine is always available
        self._availability = []

        # Schedule of tasks running on this machine
        self._machine_schedule = []

    def __str__(self):
        machine_str = 'Machine:\n\tId: ' + str(self._id) + '\n'
        if self._name:
            machine_str += '\tName: ' + str(self._name) + '\n'
        if self._availability:
            machine_str += '\tAvailability: ' + str(self._availability) + '\n'
        else:
            machine_str += '\tAvailability: always available\n'
        machine_str += '\tSchedule: ' + str(self._machine_schedule) + '\n'
        return machine_str

    def get_id(self):
        """
        Returns this machine's identifier.
        :return: this machine's identifier
        """
        return self._id

    def set_name(self, name):
        """
        Sets this machine's name
        :param name: the name to set
        :return: None
        """
        self._name = name

    def get_name(self):
        """
        Returns this machine's name.
        :return: This machine's name
        """
        return self._name

    def add_time_window_availability(self, start, end):
        """
        Adds the availability time window [start, end] for this machine.
        :param start: start time
        :param end: end time
        :return: None
        """
        if start < 0 or end < 0:
            raise Exception("Invalid time window: negative times")
        if end < start:
            raise Exception("Invalid time window: invalid bounds")
        self._availability.append([start, end])

    def remove_time_window_availability(self, start, end):
        """
        Removes the specified time window availability
        :param start: start time
        :param end: end time
        :return: None
        """
        ctr = 0
        found = False
        for tw in self._availability:
            if (tw[0] == start) and (tw[1] == end):
                found = True
                break
            ctr += 1
        if found:
            del self._availability[ctr]

    def get_time_window_availabilities(self):
        """
        Returns this machine time window availability
        :return: time window availabilities
        """
        return self._availability

    def get_schedule(self):
        """
        Returns the schedule of tasks running on this machine.
        :return: the schedule of tasks
        """
        return sorted(self._machine_schedule, key=lambda sl: sl[1])

    def reset_schedule(self):
        """
        Resets this machine's schedule.
        :return: None
        """
        del self._machine_schedule[:]

