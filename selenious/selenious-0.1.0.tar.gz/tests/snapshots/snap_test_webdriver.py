# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
# flake8: noqa
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots["test_all_find_el_are_wrapped 1"] = [
    True,
    [True],
    True,
    [True],
    True,
    [True],
    True,
    [True],
    True,
    [True],
    True,
    [True],
    True,
    [True],
    True,
    [True],
    True,
    [True],
]

snapshots["test_all_find_el_are_wrapped 2"] = [
    {"args": (), "kwargs": {}, "name": "__init__", "retval": "self"},
    {"args": ("ignored",), "kwargs": {}, "name": "find_element_by_id", "retval": True},
    {
        "args": ("ignored",),
        "kwargs": {},
        "name": "find_elements_by_id",
        "retval": [True],
    },
    {
        "args": ("ignored",),
        "kwargs": {},
        "name": "find_element_by_xpath",
        "retval": True,
    },
    {
        "args": ("ignored",),
        "kwargs": {},
        "name": "find_elements_by_xpath",
        "retval": [True],
    },
    {
        "args": ("ignored",),
        "kwargs": {},
        "name": "find_element_by_link_text",
        "retval": True,
    },
    {
        "args": ("ignored",),
        "kwargs": {},
        "name": "find_elements_by_link_text",
        "retval": [True],
    },
    {
        "args": ("ignored",),
        "kwargs": {},
        "name": "find_element_by_partial_link_text",
        "retval": True,
    },
    {
        "args": ("ignored",),
        "kwargs": {},
        "name": "find_elements_by_partial_link_text",
        "retval": [True],
    },
    {
        "args": ("ignored",),
        "kwargs": {},
        "name": "find_element_by_name",
        "retval": True,
    },
    {
        "args": ("ignored",),
        "kwargs": {},
        "name": "find_elements_by_name",
        "retval": [True],
    },
    {
        "args": ("ignored",),
        "kwargs": {},
        "name": "find_element_by_tag_name",
        "retval": True,
    },
    {
        "args": ("ignored",),
        "kwargs": {},
        "name": "find_elements_by_tag_name",
        "retval": [True],
    },
    {
        "args": ("ignored",),
        "kwargs": {},
        "name": "find_element_by_class_name",
        "retval": True,
    },
    {
        "args": ("ignored",),
        "kwargs": {},
        "name": "find_elements_by_class_name",
        "retval": [True],
    },
    {
        "args": ("ignored",),
        "kwargs": {},
        "name": "find_element_by_css_selector",
        "retval": True,
    },
    {
        "args": ("ignored",),
        "kwargs": {},
        "name": "find_elements_by_css_selector",
        "retval": [True],
    },
    {
        "args": ("ignored", "twice"),
        "kwargs": {},
        "name": "find_element",
        "retval": True,
    },
    {
        "args": ("ignored", "twice"),
        "kwargs": {},
        "name": "find_elements",
        "retval": [True],
    },
]

snapshots["test_stripped_selenious_args 1"] = [
    {
        "args": (),
        "kwargs": {"implicitly_wait": 0.1},
        "name": "__init__",
        "retval": "self",
    }
]

snapshots["test_find_element_decorator_raise 1"] = [
    {
        "args": (
            GenericRepr("<pytest_mock.plugin.MockerFixture object at 0x100000000>"),
        ),
        "kwargs": {},
        "name": "__init__",
        "retval": "self",
    },
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 0},
    {
        "args": ("_",),
        "kwargs": {},
        "name": "find_element_by_id",
        "retval": GenericRepr(
            "<class 'selenium.common.exceptions.NoSuchElementException'>"
        ),
    },
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 99},
    {
        "args": (),
        "kwargs": {"poll_frequency": 0.5, "prev_state": None, "time_left": -99},
        "name": "mock_next_state",
        "retval": ("raise", 0),
    },
]

snapshots["test_find_element_decorator_recover_or_raise_null 1"] = [
    {
        "args": (
            GenericRepr("<pytest_mock.plugin.MockerFixture object at 0x100000000>"),
        ),
        "kwargs": {},
        "name": "__init__",
        "retval": "self",
    },
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 0},
    {
        "args": ("_",),
        "kwargs": {},
        "name": "find_element_by_id",
        "retval": GenericRepr(
            "<class 'selenium.common.exceptions.NoSuchElementException'>"
        ),
    },
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 99},
    {
        "args": (),
        "kwargs": {"poll_frequency": 0.5, "prev_state": None, "time_left": 101},
        "name": "mock_next_state",
        "retval": ("recover_or_raise", 0),
    },
]

snapshots["test_find_element_decorator_recover_or_raise_nonnull 1"] = [
    {
        "args": (
            GenericRepr("<pytest_mock.plugin.MockerFixture object at 0x100000000>"),
        ),
        "kwargs": {},
        "name": "__init__",
        "retval": "self",
    },
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 0},
    {
        "args": ("_",),
        "kwargs": {},
        "name": "find_element_by_id",
        "retval": GenericRepr(
            "<class 'selenium.common.exceptions.NoSuchElementException'>"
        ),
    },
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 99},
    {
        "args": (),
        "kwargs": {"poll_frequency": 0.5, "prev_state": None, "time_left": 101},
        "name": "mock_next_state",
        "retval": ("recover_or_raise", 0),
    },
    {"args": (0,), "kwargs": {}, "name": "mock_sleep", "retval": None},
    {"args": ("_",), "kwargs": {}, "name": "find_element_by_id", "retval": True},
]

snapshots["test_find_elements_decorator_debounce 1"] = [
    {
        "args": (
            GenericRepr("<pytest_mock.plugin.MockerFixture object at 0x100000000>"),
        ),
        "kwargs": {},
        "name": "__init__",
        "retval": "self",
    },
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 0},
    {"args": ("_",), "kwargs": {}, "name": "find_elements_by_id", "retval": []},
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 1},
    {
        "args": (),
        "kwargs": {
            "debounce": 0.1,
            "ismin": False,
            "poll_frequency": 0.5,
            "prev_state": None,
            "stable_time": 1,
            "time_left": 199,
        },
        "name": "mock_next_state",
        "retval": ("debounce", 1),
    },
    {"args": (1,), "kwargs": {}, "name": "mock_sleep", "retval": None},
    {"args": ("_",), "kwargs": {}, "name": "find_elements_by_id", "retval": [1, 2, 3]},
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 99},
    {
        "args": (),
        "kwargs": {
            "debounce": 0.1,
            "ismin": True,
            "poll_frequency": 0.5,
            "prev_state": "debounce",
            "stable_time": 0,
            "time_left": 101,
        },
        "name": "mock_next_state",
        "retval": ("success", 0),
    },
]

snapshots["test_find_elements_decorator_recover_or_raise_recover 1"] = [
    {
        "args": (
            GenericRepr("<pytest_mock.plugin.MockerFixture object at 0x100000000>"),
        ),
        "kwargs": {},
        "name": "__init__",
        "retval": "self",
    },
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 0},
    {"args": ("_",), "kwargs": {}, "name": "find_elements_by_id", "retval": []},
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 1},
    {
        "args": (),
        "kwargs": {
            "debounce": 0.1,
            "ismin": False,
            "poll_frequency": 0.5,
            "prev_state": None,
            "stable_time": 1,
            "time_left": 199,
        },
        "name": "mock_next_state",
        "retval": ("recover_or_raise", 1),
    },
    {"args": (1,), "kwargs": {}, "name": "mock_sleep", "retval": None},
    {"args": ("_",), "kwargs": {}, "name": "find_elements_by_id", "retval": [1, 2, 3]},
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 99},
    {
        "args": (),
        "kwargs": {
            "debounce": 0.1,
            "ismin": True,
            "poll_frequency": 0.5,
            "prev_state": "recover_or_raise",
            "stable_time": 0,
            "time_left": 101,
        },
        "name": "mock_next_state",
        "retval": ("success", 0),
    },
]

snapshots["test_find_elements_decorator_recover_or_raise_no_recover 1"] = [
    {
        "args": (
            GenericRepr("<pytest_mock.plugin.MockerFixture object at 0x100000000>"),
        ),
        "kwargs": {},
        "name": "__init__",
        "retval": "self",
    },
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 0},
    {"args": ("_",), "kwargs": {}, "name": "find_elements_by_id", "retval": []},
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 1},
    {
        "args": (),
        "kwargs": {
            "debounce": 0.1,
            "ismin": False,
            "poll_frequency": 0.5,
            "prev_state": None,
            "stable_time": 1,
            "time_left": 199,
        },
        "name": "mock_next_state",
        "retval": ("recover_or_raise", 1),
    },
]

snapshots["test_find_elements_decorator_raise 1"] = [
    {
        "args": (
            GenericRepr("<pytest_mock.plugin.MockerFixture object at 0x100000000>"),
        ),
        "kwargs": {},
        "name": "__init__",
        "retval": "self",
    },
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 0},
    {"args": ("_",), "kwargs": {}, "name": "find_elements_by_id", "retval": []},
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 1},
    {
        "args": (),
        "kwargs": {
            "debounce": 0.1,
            "ismin": False,
            "poll_frequency": 0.5,
            "prev_state": None,
            "stable_time": 1,
            "time_left": 199,
        },
        "name": "mock_next_state",
        "retval": ("raise", 1),
    },
]

snapshots["test_find_elements_decorator_recover_and_retry_recover 1"] = [
    {
        "args": (
            GenericRepr("<pytest_mock.plugin.MockerFixture object at 0x100000000>"),
        ),
        "kwargs": {},
        "name": "__init__",
        "retval": "self",
    },
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 0},
    {"args": ("_",), "kwargs": {}, "name": "find_elements_by_id", "retval": []},
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 1},
    {
        "args": (),
        "kwargs": {
            "debounce": 0.1,
            "ismin": False,
            "poll_frequency": 0.5,
            "prev_state": None,
            "stable_time": 1,
            "time_left": 199,
        },
        "name": "mock_next_state",
        "retval": ("recover_and_retry", 1),
    },
    {"args": (1,), "kwargs": {}, "name": "mock_sleep", "retval": None},
    {"args": ("_",), "kwargs": {}, "name": "find_elements_by_id", "retval": [1, 2, 3]},
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 99},
    {
        "args": (),
        "kwargs": {
            "debounce": 0.1,
            "ismin": True,
            "poll_frequency": 0.5,
            "prev_state": "recover_and_retry",
            "stable_time": 0,
            "time_left": 101,
        },
        "name": "mock_next_state",
        "retval": ("success", 0),
    },
]

snapshots["test_find_elements_decorator_recover_and_retry_no_recover 1"] = [
    {
        "args": (
            GenericRepr("<pytest_mock.plugin.MockerFixture object at 0x100000000>"),
        ),
        "kwargs": {},
        "name": "__init__",
        "retval": "self",
    },
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 0},
    {"args": ("_",), "kwargs": {}, "name": "find_elements_by_id", "retval": []},
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 1},
    {
        "args": (),
        "kwargs": {
            "debounce": 0.1,
            "ismin": False,
            "poll_frequency": 0.5,
            "prev_state": None,
            "stable_time": 1,
            "time_left": 199,
        },
        "name": "mock_next_state",
        "retval": ("recover_and_retry", 1),
    },
    {"args": (1,), "kwargs": {}, "name": "mock_sleep", "retval": None},
    {"args": ("_",), "kwargs": {}, "name": "find_elements_by_id", "retval": [1, 2, 3]},
    {"args": (), "kwargs": {}, "name": "monotonic", "retval": 99},
    {
        "args": (),
        "kwargs": {
            "debounce": 0.1,
            "ismin": True,
            "poll_frequency": 0.5,
            "prev_state": "recover_and_retry",
            "stable_time": 0,
            "time_left": 101,
        },
        "name": "mock_next_state",
        "retval": ("success", 0),
    },
]
