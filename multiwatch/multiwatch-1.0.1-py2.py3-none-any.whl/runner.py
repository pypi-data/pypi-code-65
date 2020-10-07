import logging
import multiprocessing
import multiwatch
import os
import time


def init_log():
    formatter = logging.Formatter(
        "%(processName)s "
        "%(levelname)s "
        "%(name)s: "
        "%(message)s"
    )
    app_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    fh = logging.FileHandler(os.path.join(app_path, "tests.log"))
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger = logging.getLogger("multiwatch.runner")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    return logger


class RunnerProcess:
    def __init__(
            self, name, target,
            args=(), kwargs={}, cannot_fail_for=5, max_failures=3):
        self.name = name
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.cannot_fail_for = cannot_fail_for
        self.max_failures = max_failures

    def on_resume(self, exit_event):
        def underlying(*args, **kwargs):
            logger = logging.getLogger("multiwatch.runner")
            logger.info("Starting the runner.")
            start_time = time.time()
            count_failures = 0
            while True:
                try:
                    self.target(*args, **kwargs)
                    exit_event.set()
                    return
                except Exception as ex:
                    count_failures += 1
                    now = time.time()
                    logger.error("Failure {} on {}. Exception {}".format(
                        count_failures, self.max_failures, ex))

                    time_ellapsed = now - start_time
                    if time_ellapsed < self.cannot_fail_for:
                        logger.info(
                            "Stopping, because the failure happened {:.2f} s. "
                            "after start, which is below the threshold of "
                            "{:.2f} s.".format(
                                time_ellapsed, self.cannot_fail_for))
                        exit_event.set()
                        return

                    if count_failures >= self.max_failures:
                        logger.info(
                            "Stopping, because the maximum number of failures "
                            "({}) is reached.".format(self.max_failures))
                        exit_event.set()
                        return

        return underlying


def run(processes, queues, exit_event, sleep, report_interval, output):
    logger = init_log()
    logger.info("Running processes.")
    derived_processes = [
        multiprocessing.Process(
            name=p.name,
            target=p.on_resume(exit_event),
            args=p.args,
            kwargs=p.kwargs
        )
        for p
        in processes
    ]

    for p in derived_processes:
        logger.info("Starting process {}.".format(p.name))
        p.start()

    logger.info("Starting the monitor.")

    multiwatch.monitor(
        derived_processes, queues, exit_event, sleep, report_interval, output)
