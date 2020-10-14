from decorators import *
import time


@timer
def take_some_time():
    time.sleep(1)
    print("hello")


@debug
def debug_func(message):
    print(message)
    return True


@count_calls
def call_twice():
    print("Hi")


@deprecated
def deprecated_func():
    print("This is deprecated")


print()

take_some_time()

print()

debug_func("hello, world")

call_twice()
call_twice()

print()

warnings.simplefilter("always", DeprecationWarning)
deprecated_func()

print()