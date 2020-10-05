from time import sleep, time
from math import ceil

from psutil import Process, cpu_count, cpu_times

# How often to poll the CPU, compared to the moving-average of the job-start-interval
CPU_IDLE_POLL_DIVISOR = 20

# Polling the cpu-idle more often than this is bound to give noisy results
# If your application consumes jobs more often than this, pothead probably is not for you
CPU_IDLE_POLL_MIN_INTERVAL = 0.050
CPU_IDLE_POLL_MAX_INTERVAL = 2

# Jobs will still be clamped to idle CPU, but we want SOME kind of upper bound on concurrency, to avoid I/O
# blockage causing ridiculous amounts of work
DEFAULT_MAX_CONCURRENT_MULTIPLIER = 2

__all__ = ["wait_for_idle_cpus"]


class MovingAverage:
    def __init__(self, init=0, inertia=0.6):
        self.value = init
        self.speed = 1 - inertia
        self.inertia = inertia

    def update(self, value):
        self.value = (self.value * self.inertia) + (value * self.speed)
        return self.value


class WorkersRunning:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1
        return self

    def done(self):
        self.count -= 1


"""Timed measurement on an incrementing counter

Reads the counter, divides with time passed since last reading, and smooths the value using a moving average
"""


class InertialTimeDerivate:
    def __init__(self, func, initial, inertia):
        self.func = func
        self.last_value = self.func()
        self.last_check = time()
        self.inertial_value = MovingAverage(initial, inertia)

    def update(self):
        new_value = self.func()
        this_check = time()
        elapsed = this_check - self.last_check
        delta = new_value - self.last_value
        self.last_check = this_check
        self.last_value = new_value
        return self.inertial_value.update(delta / elapsed)


"""CPU-gated wait_for_slot implementation

Creates a wait_for_slot-callable that will let through at least one concurrent job, and additional jobs as
long as `count` cpu:s are idle. It is cgroup-aware, and will not allow current process and subprocesses to
consume more CPU than configured cgroup-limit.
"""


def wait_for_idle_cpus(required, *, max_concurrent=None, fixed_delay=0.2, inertia=0.7):
    workers = WorkersRunning()
    cpu_wait_time = MovingAverage(1, 0.7)

    process = Process()

    def cpu_used_in_process():
        times = process.cpu_times()
        return times.user + times.system + times.children_user + times.children_system

    # CPU.limits enforced by cgroup, configured by I.E. K8S
    # Authorative docs at https://www.kernel.org/doc/Documentation/scheduler/sched-bwc.txt
    with open("/sys/fs/cgroup/cpu/cpu.cfs_quota_us", "rt") as quota, open(
        "/sys/fs/cgroup/cpu/cpu.cfs_period_us", "rt"
    ) as period:
        quota = int(quota.read())
        if quota > 0:
            cpu_quota = quota / int(period.read())
            if not max_concurrent:
                max_concurrent = ceil(cpu_quota * DEFAULT_MAX_CONCURRENT_MULTIPLIER / required)

            # Precalculate the quota with headroom for a new job
            cpu_quota -= required
        else:
            cpu_quota = None
            if not max_concurrent:
                max_concurrent = ceil(cpu_count() * DEFAULT_MAX_CONCURRENT_MULTIPLIER / required)

    def wait_for_slot(halt):
        if workers.count == 0:
            workers.increment()

        sleep(fixed_delay)

        start_time = time()

        idle = InertialTimeDerivate(lambda: cpu_times().idle, 0, inertia)
        if cpu_quota:
            cpu_used = InertialTimeDerivate(cpu_used_in_process, cpu_count(), inertia)

        cpu_poll_interval = max(CPU_IDLE_POLL_MIN_INTERVAL, min(cpu_wait_time.value / CPU_IDLE_POLL_DIVISOR, CPU_IDLE_POLL_MAX_INTERVAL))
        while workers.count > 0 and not halt():
            if (
                workers.count < max_concurrent
                and idle.update() >= required
                and (cpu_quota is None or cpu_used.update() <= cpu_quota)
            ):
                cpu_wait_time.update(time() - start_time)
                break

            sleep(cpu_poll_interval)

        return workers.increment()

    return wait_for_slot
