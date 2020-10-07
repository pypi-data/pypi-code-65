from dataclasses import dataclass
from typing import Dict


@dataclass
class SprintStoryPoints:
    """
    A sprint story points representation class.
    """
    completed: int = 0
    not_completed: int = 0

    @property
    def total(self) -> int:
        """
        Total story points assigned.

        :return: Total story points.
        """
        return self.completed + self.not_completed

    @property
    def completed_perc(self) -> float:
        try:
            return (self.completed / self.total) * 100
        except ZeroDivisionError:
            return 0.0

    @property
    def not_completed_perc(self) -> float:
        try:
            return (self.not_completed / self.total) * 100
        except ZeroDivisionError:
            return 0.0

    def add_completed(self, points: int) -> None:
        """
        Adds completed story points.

        :param points: Completed story points.

        :return: No return.
        """
        self.completed += points

    def add_not_completed(self, points: int) -> None:
        """
        Adds not completed story points.

        :param points: Not completed story points.

        :return: No return.
        """
        self.not_completed += points

    def to_dict(self) -> Dict[str, int]:
        """
        Serializes the class.

        :return: Dictionary class representation.
        """
        return {
            'completed': self.completed,
            'not_completed': self.not_completed,
            'total': self.total
        }

    def __str__(self) -> str:
        """
        String representation.

        :return: String representation.
        """
        return (
            f'Total: {self.total:3d} | '
            f'Completed: {self.completed:3d}({self.completed_perc:5.1f}%) | '
            f'Not completed: {self.not_completed:3d}({self.not_completed_perc:5.1f}%).'
        )
