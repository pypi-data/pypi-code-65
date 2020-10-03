#!/usr/bin/env python3

"""Tests for `podcust` package."""

import pytest
import mock

from podcust.platform import podman_exists
from subprocess import CompletedProcess


class TestPodman:
    @mock.patch("podcust.platform.subprocess.run")
    def test_podman_exists1(self, mocked_run):
        mocked_run.return_value = CompletedProcess(
            args=["podman", "--version"],
            returncode=0,
            stdout="podman version 2.0.6\n",
            stderr="",
        )
        podman_exists()

    @mock.patch("podcust.platform.subprocess.run")
    def test_podman_exists2(self, mocked_run):
        mocked_run.return_value = CompletedProcess(
            args=["podman", "--version"],
            returncode=127,
            stdout="",
            stderr="--version: podman: command not found\n",
        )
        with pytest.raises(OSError, match="podman package is not available!"):
            podman_exists()
