class Task:
    """
    A Task is a single unit of work that can be performed on a machine.
    A task is part of a job.
    """

    def __init__(self, id_task=None):
        """
        Constructs a new task.
        :param id_task: unique identifier for this task.
                        If None is specified, a default one is used.
        """
        self._task_id = id_task
        if self._task_id is None:
            self._task_id = id(self)

        # Machine identifier on which this task should be executed
        self._machine_id = -1

        # Duration of this task
        self._duration = 0

        # Start time for this job = -1
        self._start_time = -1

    def __str__(self):
        task_str = 'Task:\n\tId: ' + str(self._task_id) + '\n'
        task_str += '\tRequired machine: ' + str(self._machine_id) + '\n'
        task_str += '\tDuration: ' + str(self._duration) + '\n'
        if self._start_time >= 0:
            task_str += '\tStart time: ' + str(self._start_time) + '\n'
            task_str += '\tEnd time: ' + str(self._start_time + self._duration) + '\n'
        else:
            task_str += '\tStart time: unknown\n'
        return task_str

    def get_id(self):
        return self._task_id

    def set_required_machine(self, machine_id):
        self._machine_id = machine_id

    def get_required_machine(self):
        return self._machine_id

    def set_duration(self, duration):
        if not isinstance(duration, int):
            raise Exception("Duration is not an integer value")
        if duration < 0:
            raise Exception("Duration is a negative number")
        self._duration = duration

    def get_duration(self):
        return self._duration

    def get_start_time(self):
        """
        Returns the start time on this task
        :return:
        """
        return self._start_time


class Job:
    def __init__(self, job_id, name=''):
        """
        Constructs a new job.
        :param job_id: job unique identifier
        :param name: job name
        """
        self._job_id = job_id
        self._name = name

        # List of tasks for this job.
        # Tasks are executed sequentially
        self._task_list = []

        # List of job dependencies
        self._dependency_list = []

    def __str__(self):
        job_str = 'Job:\n\tId: ' + str(self._job_id) + '\n'
        if self._name:
            job_str += '\tName: ' + str(self._name) + '\n'
        if self._dependency_list:
            job_str += '\tDependencies: ' + str(self._dependency_list) + '\n'
        for task in self._task_list:
            job_str += '\t' + str(task).replace('\t', '\t\t')
        return job_str

    def get_id(self):
        """
        Returns this job's unique identifier
        :return:
        """
        return self._job_id

    def set_name(self, name):
        """
        Sets this job's name
        :param name: the name to set
        :return: None
        """
        self._name = name

    def get_name(self):
        """
        Returns this job's name
        :return:
        """
        return self._name

    def add_dependency(self, job_id):
        """
        Adds a job in the dependency list of this job.
        This means that this job must be scheduled after the
        given dependency is completed.
        :param job_id: the identifier of the job depending on
        :return: None
        """
        if job_id not in self._dependency_list:
            self._dependency_list.append(job_id)

    def remove_dependency(self, job_id):
        """
        Removes the given dependency.
        :param job_id: identifier of the job to remove from the dependency list.
        :return: None
        """
        if job_id in self._dependency_list:
            self._dependency_list.remove(job_id)

    def get_dependency_list(self):
        """
        Returns the dependency list of this job.
        :return: the dependency list
        """
        return self._dependency_list

    def add_task(self, id_task=None):
        """
        Adds a new task to the task list and returns its reference.
        :param id_task: the id of the task to add
        :return: the reference to the added task
        """
        self._task_list.append(Task(id_task))
        return self._task_list[-1]

    def remove_task(self, id_task):
        """
        Removes the task with specified identifier from the list of tasks
        of this job.
        :param id_task: the task to remove
        :return: None
        """
        if id_task in self._task_list:
            self._task_list.remove(id_task)

    def get_task_list(self):
        """
        Returns the list of this job's tasks
        :return: the list of tasks of this job
        """
        return self._task_list

