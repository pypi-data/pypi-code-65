import logging
import signal


logger = logging.getLogger("multiwatch.termination")


def setup_sigterm(*exit_events):
    # exit_event can be either a single multiprocessing.Event() or a list.
    def terminate(signum, frame):
        for e in exit_events:
            e.set()

    signal.signal(signal.SIGINT, terminate)
    signal.signal(signal.SIGTERM, terminate)


def terminate_process(process, timeout=2):
    process.join(timeout)
    if process.is_alive():
        process.terminate()

    if process.exitcode:
        logger.info("Process {} exited with code {}.".format(
            process.name, process.exitcode))
    else:
        logger.info(
            "Process {} exited with no exit code.".format(process.name))
