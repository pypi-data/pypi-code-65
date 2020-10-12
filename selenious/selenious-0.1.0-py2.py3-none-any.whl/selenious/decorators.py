from selenium.common.exceptions import NoSuchElementException
import functools
from time import sleep, monotonic
from .helpers import validate_time_settings


def _find_element_next_state(prev_state, time_left, poll_frequency):
    if time_left <= 0:
        if prev_state is None:
            return ("recover_or_raise", 0)
        else:
            return ("raise", None)

    return ("recover_and_retry", min(time_left, poll_frequency))


def find_element(func):
    special_args = ("timeout", "poll_frequency", "recover")

    @functools.wraps(func)
    def find_element_decorator(self, *args, **kwargs):
        func_kwargs = {k: v for (k, v) in kwargs.items() if k not in special_args}
        timeout = kwargs.get("timeout", self.timeout)
        poll_frequency = kwargs.get("poll_frequency", self.poll_frequency)
        recover = kwargs.get("recover", self.recover)
        start_time = monotonic()
        state = None
        attempts = 0

        validate_time_settings(self._implicitly_wait, timeout, poll_frequency)

        while True:
            try:
                return func(self, *args, **func_kwargs)
            except NoSuchElementException:
                timestamp = monotonic()
                time_left = timeout + start_time - timestamp
                state, sleep_time = _find_element_next_state(
                    prev_state=state, time_left=time_left, poll_frequency=poll_frequency
                )
                if state == "raise" or (state == "recover_or_raise" and not recover):
                    raise

            attempts += 1
            if recover:
                recover(
                    webdriver=self,
                    function=func.__name__,
                    args=args,
                    kwargs=kwargs,
                    elapased=timestamp - start_time,
                    attempts=attempts,
                )
            sleep(sleep_time)

    return find_element_decorator


def _find_elements_next_state(
    prev_state,
    time_left,
    poll_frequency,
    debounce,
    stable_time,
    ismin,
):
    if ismin:
        settle_time_remaining = debounce - stable_time
        if settle_time_remaining > 0:
            return ("debounce", settle_time_remaining)
        else:
            return ("success", None)

    if time_left <= 0:
        if prev_state is None:
            return ("recover_or_raise", 0)
        else:
            return ("raise", None)

    return ("recover_and_retry", min(time_left, poll_frequency))


def find_elements(func):

    special_args = ("timeout", "poll_frequency", "recover", "min", "debounce")

    @functools.wraps(func)
    def find_elements_decorator(self, *args, **kwargs):
        func_kwargs = {k: v for (k, v) in kwargs.items() if k not in special_args}
        timeout = kwargs.get("timeout", self.timeout)
        poll_frequency = kwargs.get("poll_frequency", self.poll_frequency)
        recover = kwargs.get("recover", self.recover)
        min = kwargs.get("min", 0)
        debounce = kwargs.get("debounce", self.debounce)
        debounce = poll_frequency if debounce is True else debounce
        start_time = monotonic()
        attempts = 0
        prev_len = 0
        prev_time = start_time
        state = None

        validate_time_settings(self._implicitly_wait, timeout, poll_frequency)

        while True:
            retval = func(self, *args, **func_kwargs)
            timestamp = monotonic()
            attempts += 1
            length = len(retval)
            if length != prev_len:
                prev_time = timestamp
                prev_len = length
                stable_time = 0
            else:
                stable_time = timestamp - prev_time
            time_left = timeout + start_time - timestamp
            ismin = prev_len >= min

            state, sleep_time = _find_elements_next_state(
                prev_state=state,
                time_left=time_left,
                poll_frequency=poll_frequency,
                debounce=debounce,
                stable_time=stable_time,
                ismin=ismin,
            )

            if state == "success":
                return retval

            if state == "raise" or (state == "recover_or_raise" and not recover):
                raise NoSuchElementException(
                    "{} elements is less than min of {}".format(length, min)
                )

            if state in ("recover_or_raise", "recover_and_retry") and recover:
                recover(
                    webdriver=self,
                    function=func,
                    args=args,
                    kwargs=kwargs,
                    elapased=timestamp - start_time,
                    attempts=attempts,
                    elements=retval,
                )
            sleep(sleep_time)

    return find_elements_decorator
