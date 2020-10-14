import sys
from . import scheduling_problem
from .SchedulingModels.Machine import Machine
from .SchedulingModels.Job import Job
from parallelsdk.proto import optimizer_model_pb2
from parallelsdk.proto.scheduling_model_pb2 import SearchStrategy
from parallelsdk.proto.optimizer_defs_pb2 import *


class JobShopProblem(scheduling_problem.SchedulingProblem):
    """
    Class encapsulating a Job-Shop problem.
    Job shop scheduling or the job-shop problem (JSP) is an optimization problem
    in which jobs are assigned to resources at particular times.
    The most basic version is as follows:
    We are given n jobs J1, J2, ..., Jn of varying processing times,
    which need to be scheduled on m machines with varying processing power,
    while trying to minimize the makespan.
    The makespan is the total length of the schedule (that is,
    when all the jobs have finished processing).
    """

    def __init__(self, name=""):
        """
        Generates a new Job-Shop scheduling model instance.
        A Job-Shop problem is generally described with the following components:
        - A set of jobs: J1, J2, ...
        - A set of tasks: T_1_1, T_1_2, T_2_1, ...
        - A set of machines: M_1, M_2, ...
        Each job can contain one or more tasks.
        Each tasks within a job must be started only after the previous one has completed.
        Each task is executed on a specified machine.
        Each machine can execute at most one task at a time.
        Each machine can have maintenance times in which the machine cannot be used.
        """
        super().__init__(name, scheduling_problem.SchedulingModelType.JOB_SHOP)

        # Flag indicating whether this is a satisfaction problem or not
        self._is_satisfaction = False

        # Cost per time unit
        self._makespan_cost_per_time_unit = 1

        # Internal mapping for machines
        self._machines_map = {}

        # Internal mapping for jobs
        self._job_map = {}

        # Makespan value
        self._make_span = sys.maxsize

        # Internal mapping of machines to protobuf objects
        self._machine_protobuf_mapping = {}
        self._machine_protobuf_mapping_reverse = {}

        # Internal mapping for jobs to protobuf objects
        self._job_protobuf_mapping = {}
        self._job_protobuf_mapping_reverse = {}
        self._task_protobuf_mapping_reverse = {}

        # Search heuristics
        self._variable_selection_strategy = SearchStrategy.CHOOSE_LOWEST_MIN
        self._value_selection_strategy = SearchStrategy.SELECT_MIN_VALUE

        # Search options
        self._search_timeout_sec = -1.0
        self._num_parallel_cores = 1

    def _set_task_start_time(self, task_idx, start_time):
        task = self._task_protobuf_mapping_reverse[task_idx]
        task._start_time = start_time

        # Set this task on the machine running it
        machine = self._machines_map[task.get_required_machine()]
        machine._machine_schedule.append([task.get_id(),
                                          task.get_start_time(),
                                          task.get_start_time() + task.get_duration()])

    def set_num_parallel_cores(self, num_cores):
        """
        Sets the number of parallel cores.
        :param num_cores: number of parallel cores
        :return: None
        """
        if not isinstance(num_cores, int):
            raise Exception("Number of cores should be an integer value")
        self._num_parallel_cores = max(1, num_cores)

    def get_num_parallel_cores(self):
        """
        Returns the number of parallel cores to be used during search.
        :return: the number of parallel cores to be used during search
        """
        return self._num_parallel_cores

    def set_search_timeout(self, timeout_sec):
        """
        Sets the search timeout in seconds
        :param timeout_sec: timeout in seconds
        :return: None
        """
        if not isinstance(timeout_sec, float):
            raise Exception("Timeout should be a float value")
        self._search_timeout_sec = timeout_sec

    def get_search_timeout(self):
        """
        Returns the search timeout in seconds
        :return: search timeout in seconds
        """
        return self._search_timeout_sec

    def set_variable_selection_strategy(self, var_strategy):
        if var_strategy == 'lowest_min':
            self._variable_selection_strategy = SearchStrategy.CHOOSE_LOWEST_MIN
        elif var_strategy == 'highest_max':
            self._variable_selection_strategy = SearchStrategy.CHOOSE_HIGHEST_MAX
        elif var_strategy == 'min_domain_size':
            self._variable_selection_strategy = SearchStrategy.CHOOSE_MIN_DOMAIN_SIZE
        elif var_strategy == 'max_domain_size':
            self._variable_selection_strategy = SearchStrategy.CHOOSE_MAX_DOMAIN_SIZE

    def set_value_selection_strategy(self, val_strategy):
        if val_strategy == 'min_value':
            self._value_selection_strategy = SearchStrategy.SELECT_MIN_VALUE
        elif val_strategy == 'max_value':
            self._value_selection_strategy = SearchStrategy.SELECT_MAX_VALUE
        elif val_strategy == 'lower_half':
            self._value_selection_strategy = SearchStrategy.SELECT_LOWER_HALF
        elif val_strategy == 'upper_half':
            self._value_selection_strategy = SearchStrategy.SELECT_UPPER_HALF
        elif val_strategy == 'median_value':
            self._value_selection_strategy = SearchStrategy.SELECT_MEDIAN_VALUE

    def set_consistency_search(self, set_satisfaction=True):
        self._is_satisfaction = set_satisfaction

    def is_consistency_search_enabled(self):
        return self._is_satisfaction

    def set_makespan_cost_per_time_unit(self, cost):
        if cost < 0:
            raise Exception("Invalid cost: negative cost")
        self._makespan_cost_per_time_unit = cost

    def get_makespan_cost_per_time_unit(self):
        return self._makespan_cost_per_time_unit

    def print_solution(self):
        sol_str = self.name() + " - Solution:\n"
        for machine in self._machines_map.values():
            sol_str += "Machine " + str(machine.get_id())
            if machine.get_name():
                sol_str += " - " + machine.get_name()
            sol_str += ":\n"
            sol_str += "\t" + str(machine.get_schedule()) + "\n"
        print(sol_str)

    def add_machine(self, id_machine, name=''):
        """
        Builds and adds a new machine/resource to the Job-Shop problem.
        :param id_machine: unique identifier for this machine
        :param name: optional name of this machine
        :return: the machine object
        """
        if id_machine in self._machines_map:
            raise Exception("A machine with the same identifier is already present")
        self._machines_map[id_machine] = Machine(id_machine, name)
        return self._machines_map[id_machine]

    def get_machine(self, machine_lookup_value):
        if isinstance(machine_lookup_value, int):
            if machine_lookup_value in self._machines_map:
                return self._machines_map[machine_lookup_value]
            return None
        elif isinstance(machine_lookup_value, str):
            for m in self._machines_map.values():
                if m.get_name() == machine_lookup_value:
                    return m
            return None
        else:
            raise Exception("Invalid machine identifier")

    def get_all_machines(self):
        return self._machines_map.values()

    def remove_machine(self, id_machine):
        if id_machine in self._machines_map:
            del self._machines_map[id_machine]

    def add_job(self, id_job, name=''):
        """
        Builds and adds a new job to the Job-Shop problem.
        :param id_job: unique identifier for this job
        :param name: optional name of this job
        :return: the job object
        """
        if id_job in self._job_map:
            raise Exception("A job with the same identifier is already present")
        self._job_map[id_job] = Job(id_job, name)
        return self._job_map[id_job]

    def get_job(self, job_lookup_value):
        if isinstance(job_lookup_value, int):
            if job_lookup_value in self._job_map:
                return self._job_map[job_lookup_value]
            return None
        elif isinstance(job_lookup_value, str):
            for j in self._job_map.values():
                if j.get_name() == job_lookup_value:
                    return j
            return None
        else:
            raise Exception("Invalid job identifier")

    def get_all_jobs(self):
        """
        Returns all jobs.
        :return: returns all jobs
        """
        return self._job_map.values()

    def remove_job(self, id_job):
        if id_job in self._job_map:
            del self._job_map[id_job]

    def get_make_span(self):
        """
        Returns the makespan value
        :return: makespan value
        """
        return self._make_span

    def upload_problem_proto_solution(self, job_shop_solution_proto):
        """
        Uploads the solution returned from the back-end optimizer.
        """
        if not job_shop_solution_proto.HasField("job_shop_solution"):
            err_msg = "JobShopProblem - invalid solution type"
            raise Exception(err_msg)

        if job_shop_solution_proto.status == OptimizerSolutionStatusProto.OPT_SOLVER_FAIL:
            print("Solution not found")
            return
        elif job_shop_solution_proto.status == OptimizerSolutionStatusProto.OPT_SOLVER_MODEL_INVALID:
            print("Invalid model")
            return
        elif job_shop_solution_proto.status == OptimizerSolutionStatusProto.OPT_SOLVER_NOT_SOLVED:
            print("Model not solved")
            return

        js_schedule = job_shop_solution_proto.job_shop_solution.job_shop_schedule
        if not self._is_satisfaction:
            self._make_span = js_schedule.makespan_cost
        task_ctr = 0
        for job in js_schedule.jobs:
            for task in job.tasks:
                self._set_task_start_time(task_ctr, task.start_time)
                task_ctr += 1

    def to_protobuf(self):
        # Create a Job-Shop model
        self._machine_protobuf_mapping.clear()
        self._job_protobuf_mapping.clear()
        self._machine_protobuf_mapping_reverse.clear()
        self._job_protobuf_mapping_reverse.clear()
        self._task_protobuf_mapping_reverse.clear()

        optimizer_model = optimizer_model_pb2.OptimizerModel()
        optimizer_model.scheduling_model.model_id = self.model_name

        # Search strategy selection
        src_strat = optimizer_model.scheduling_model.job_shop_model.search_strategy
        src_strat.variable_selection_type = SearchStrategy.CHOOSE_LOWEST_MIN
        src_strat.value_selection_type = SearchStrategy.SELECT_MIN_VALUE

        # Search options
        optimizer_model.scheduling_model.job_shop_model.timeout_sec = self._search_timeout_sec
        optimizer_model.scheduling_model.job_shop_model.num_parallel_cores = self._num_parallel_cores

        # Job-Shop model declaration
        js_model = optimizer_model.scheduling_model.job_shop_model.job_shop_model
        js_model.is_optimization = not self._is_satisfaction
        js_model.makespan_cost_per_time_unit = self._makespan_cost_per_time_unit

        # Create all the resources/machines
        machine_ctr = 0
        for machine in self._machines_map.values():
            self._machine_protobuf_mapping[machine.get_id()] = machine_ctr
            self._machine_protobuf_mapping_reverse[machine_ctr] = machine.get_id()
            # Reset machine's schedule
            machine.reset_schedule()
            proto_machine = js_model.machines.add()
            proto_machine.name = machine.get_name()
            availability_list = machine.get_time_window_availabilities()
            for availability_window in availability_list:
                proto_machine.availability_matrix.availability_time.append(availability_window[0])
                proto_machine.availability_matrix.availability_time.append(availability_window[1])
            machine_ctr += 1

        job_ctr = 0
        task_ctr = 0
        for job in self._job_map.values():
            self._job_protobuf_mapping[job.get_id()] = job_ctr
            self._job_protobuf_mapping_reverse[job_ctr] = job.get_id()
            proto_job = js_model.jobs.add()

            # Set default values
            proto_job.earliest_start = 0
            proto_job.latest_end = sys.maxsize
            proto_job.name = job.get_name()
            for task in job.get_task_list():
                self._task_protobuf_mapping_reverse[task_ctr] = task
                proto_task = proto_job.tasks.add()
                # Set required machine
                required_machine = task.get_required_machine()
                if required_machine >= 0:
                    machine_id = self._machine_protobuf_mapping[task.get_required_machine()]
                    proto_task.machine.append(machine_id)
                    # Set duration only if there is a machine
                    proto_task.duration.append(task.get_duration())
                task_ctr += 1
            job_ctr += 1

        # Set dependency list
        for job in self._job_map.values():
            this_job_idx = self._job_protobuf_mapping[job.get_id()]
            dep_list = job.get_dependency_list()
            for dep in dep_list:
                if dep in self._job_protobuf_mapping:
                    prec_proto = js_model.precedences.add()
                    prec_proto.first_job_index = self._job_protobuf_mapping[dep]
                    prec_proto.second_job_index = this_job_idx

        # Return the protobuf object
        return optimizer_model
