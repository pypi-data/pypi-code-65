"""logging psutil utilities."""
import logging

from psutil import cpu_percent, virtual_memory

# Reference for using a logging filter: https://stackoverflow.com/a/61830838/


class PsutilFilter(logging.Filter):
    """psutil logging filter."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add contextual information about the currently used CPU and virtual memory percentages into the `psutil` attribute of the given log record.

        An example of the set value is "c18m68", which means that 18% of the system-wide CPU and 68% of the physical memory are in use.
        """
        record.psutil = f"c{cpu_percent():02.0f}m{virtual_memory().percent:02.0f}"  # type: ignore
        return True  # True means don't discard the record.
