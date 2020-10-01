import os
import signal
import time
from threading import Thread

import pytest

from dagster import (
    DagsterEventType,
    DagsterSubprocessError,
    Field,
    ModeDefinition,
    String,
    execute_pipeline_iterator,
    pipeline,
    reconstructable,
    resource,
    seven,
    solid,
)
from dagster.core.instance import DagsterInstance
from dagster.utils import delay_interrupts, safe_tempfile_path


def _send_kbd_int(temp_files):
    while not all([os.path.exists(temp_file) for temp_file in temp_files]):
        time.sleep(0.1)
    seven.thread.interrupt_main()


@solid(config_schema={"tempfile": Field(String)})
def write_a_file(context):
    with open(context.solid_config["tempfile"], "w") as ff:
        ff.write("yup")

    while True:
        time.sleep(0.1)


@solid
def should_not_start(_context):
    assert False


@pipeline
def write_files_pipeline():
    write_a_file.alias("write_1")()
    write_a_file.alias("write_2")()
    write_a_file.alias("write_3")()
    write_a_file.alias("write_4")()
    should_not_start.alias("x_should_not_start")()
    should_not_start.alias("y_should_not_start")()
    should_not_start.alias("z_should_not_start")()


def test_interrupt():
    @pipeline
    def write_a_file_pipeline():
        write_a_file()

    with safe_tempfile_path() as success_tempfile:

        # launch a thread the waits until the file is written to launch an interrupt
        Thread(target=_send_kbd_int, args=([success_tempfile],)).start()

        results = []
        try:
            # launch a pipeline that writes a file and loops infinitely
            # next time the launched thread wakes up it will send a keyboard
            # interrupt
            for result in execute_pipeline_iterator(
                write_a_file_pipeline,
                run_config={"solids": {"write_a_file": {"config": {"tempfile": success_tempfile}}}},
            ):
                results.append(result.event_type)
            assert False  # should never reach
        except KeyboardInterrupt:
            pass

        assert DagsterEventType.STEP_FAILURE in results
        assert DagsterEventType.PIPELINE_FAILURE in results


# https://github.com/dagster-io/dagster/issues/1970
@pytest.mark.skip
def test_interrupt_multiproc():
    with seven.TemporaryDirectory() as tempdir:
        file_1 = os.path.join(tempdir, "file_1")
        file_2 = os.path.join(tempdir, "file_2")
        file_3 = os.path.join(tempdir, "file_3")
        file_4 = os.path.join(tempdir, "file_4")

        # launch a thread the waits until the file is written to launch an interrupt
        Thread(target=_send_kbd_int, args=([file_1, file_2, file_3, file_4],)).start()

        results = []
        try:
            # launch a pipeline that writes a file and loops infinitely
            # next time the launched thread wakes up it will send a keyboard
            # interrupt
            for result in execute_pipeline_iterator(
                reconstructable(write_files_pipeline),
                run_config={
                    "solids": {
                        "write_1": {"config": {"tempfile": file_1}},
                        "write_2": {"config": {"tempfile": file_2}},
                        "write_3": {"config": {"tempfile": file_3}},
                        "write_4": {"config": {"tempfile": file_4}},
                    },
                    "execution": {"multiprocess": {"config": {"max_concurrent": 4}}},
                    "storage": {"filesystem": {}},
                },
                instance=DagsterInstance.local_temp(tempdir=tempdir),
            ):
                results.append(result)
            assert False  # should never reach
        except (DagsterSubprocessError, KeyboardInterrupt):
            pass

        assert [result.event_type for result in results].count(DagsterEventType.STEP_FAILURE) == 4
        assert DagsterEventType.PIPELINE_FAILURE in [result.event_type for result in results]


def test_interrupt_resource_teardown():
    called = []
    cleaned = []

    @resource
    def resource_a(_):
        try:
            called.append("A")
            yield "A"
        finally:
            cleaned.append("A")

    @solid(config_schema={"tempfile": Field(String)}, required_resource_keys={"a"})
    def write_a_file_resource_solid(context):
        with open(context.solid_config["tempfile"], "w") as ff:
            ff.write("yup")

        while True:
            time.sleep(0.1)

    @pipeline(mode_defs=[ModeDefinition(resource_defs={"a": resource_a})])
    def write_a_file_pipeline():
        write_a_file_resource_solid()

    with safe_tempfile_path() as success_tempfile:

        # launch a thread the waits until the file is written to launch an interrupt
        Thread(target=_send_kbd_int, args=([success_tempfile],)).start()

        results = []
        try:
            # launch a pipeline that writes a file and loops infinitely
            # next time the launched thread wakes up it will send a keyboard
            # interrupt
            for result in execute_pipeline_iterator(
                write_a_file_pipeline,
                run_config={
                    "solids": {
                        "write_a_file_resource_solid": {"config": {"tempfile": success_tempfile}}
                    }
                },
            ):
                results.append(result.event_type)
            assert False  # should never reach
        except KeyboardInterrupt:
            pass

        assert DagsterEventType.STEP_FAILURE in results
        assert DagsterEventType.PIPELINE_FAILURE in results
        assert "A" in cleaned


@pytest.mark.skipif(seven.IS_WINDOWS, reason="Interrupts handled differently on windows")
def test_delay_interrupt():
    outer_interrupt = False
    inner_interrupt = False

    try:
        with delay_interrupts():
            try:
                os.kill(os.getpid(), signal.SIGINT)
                time.sleep(1)
            except KeyboardInterrupt:
                inner_interrupt = True
    except KeyboardInterrupt:
        outer_interrupt = True

    assert outer_interrupt
    assert not inner_interrupt

    # Verify standard interrupt handler is restored
    standard_interrupt = False

    try:
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(1)
    except KeyboardInterrupt:
        standard_interrupt = True

    assert standard_interrupt

    outer_interrupt = False
    inner_interrupt = False
    # No exception if no signal thrown
    try:
        with delay_interrupts():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                inner_interrupt = True
    except KeyboardInterrupt:
        outer_interrupt = True

    assert not outer_interrupt
    assert not inner_interrupt
