from __future__ import annotations
from typing import List


class Task:
    def __init__(self, title: str) -> None:
        self.title = title
        self.sub_tasks: List[Task] = []

    def add_sub_task(self, task: Task):
        self.sub_tasks.append(task)
