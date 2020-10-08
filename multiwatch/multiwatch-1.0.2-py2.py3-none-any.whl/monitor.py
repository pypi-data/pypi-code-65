import datetime
import logging
import multiprocessing
import multiwatch
import os
import psutil
import time


class Stats:
    def __init__(self, sequence):
        self.minimum = min(sequence)
        self.maximum = max(sequence)
        self.average = sum(sequence) / len(sequence)

    def __str__(self):
        return "{:.2f}..{:.2f}, x̄ {:.2f}".format(
            self.minimum, self.maximum, self.average)


class ProcessSnapshot:
    def __init__(self, process):
        self.name = process.name
        self.is_alive = process.is_alive()

    def __str__(self):
        state = "alive" if self.is_alive else "idle"
        return "{}: {}".format(self.name, state)


class QueueSnapshot:
    def __init__(self, name, queue):
        self.name = name
        self.size = queue.qsize()
        self.capacity = queue._maxsize

    def __str__(self):
        return "{}: {} of {}".format(self.name, self.size, self.capacity)


class Report:
    def __init__(self, cpu, memory, processes, queues):
        self.cpu = cpu
        self.memory = memory
        self.processes = processes
        self.queues = queues

    def to_text(self):
        return "\n".join(self._to_lines())

    def _to_lines(self):
        yield "CPU: {}".format(self.cpu)
        yield "Memory: {}".format(self.memory)

        for p in self.processes:
            yield "Process {}".format(p)

        for q in self.queues:
            yield "Queue {}".format(q)


def monitor(processes, queues, exit_event, sleep, report_interval, output):
    if (
            not isinstance(output, multiprocessing.queues.Queue) and
            not isinstance(output, str)
    ):
        raise TypeError("The output should be a queue or a string.")

    logger = logging.getLogger("multiwatch.monitor")

    pid = os.getpid()
    current_psutil_process = psutil.Process(pid)

    last_snapshot = datetime.datetime.now()

    logger.info("Started the loop.")

    cpu_all = []
    memory_all = []

    while not exit_event.is_set():
        time.sleep(sleep)
        cpu_all.append(current_psutil_process.cpu_percent())
        memory_all.append(current_psutil_process.memory_percent())

        now = datetime.datetime.now()
        if (now - last_snapshot).total_seconds() > report_interval:
            last_snapshot = now

            report = Report(
                Stats(cpu_all),
                Stats(memory_all),
                [ProcessSnapshot(p) for p in processes],
                [QueueSnapshot(name, q) for name, q in queues]
            )

            cpu_all.clear()
            memory_all.clear()

            if isinstance(output, multiprocessing.queues.Queue):
                output.put(report)
            else:
                with open(output, "w") as f:
                    print(report.to_text(), file=f)

    logger.info("Finished the loop.")

    for p in processes:
        multiwatch.terminate_process(p)

    logger.info("Exiting the application.")

    for child in multiprocessing.active_children():
        logger.error(
            "Process {} prevents the program from terminating.".format(
                child.name))
