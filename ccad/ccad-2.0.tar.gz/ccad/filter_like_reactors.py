#!/usr/bin/python
# coding: utf-8

from .reactor import ReactorCAD


class FilterLikeReactor(ReactorCAD):

    _h_filter: float
    _d_filter: float

    def alignFilterToHeight(self, target_height: float) -> None:

        """
        Align the filter to 'target_height', depending on strategy. Keep
        top aligned if needed.
        To be sublassed.

        Args:
            target_height;float:

        Returns:
            None

        Raises:
            NotImplementedError: when accessed through this class and not subclass
        """

        raise NotImplementedError

    @property
    def z_bottom_filter(self) -> float:

        """
        Return absolute z for bottom of the filter.
        No setter for this property

        Returns:
            float: height for filter's bottom
        """

        return self._findZFilter()

    @property
    def z_top_filter(self) -> float:

        """
        Return absolute z for top of the filter.
        No setter for this property

        Returns:
            float: height for filter's bottom
        """

        return self._findZFilter() + self._h_filter

    def _findZFilter(self) -> float:

        """
        To be subclassed
        Find the absolute height (z) of the bottom of the filter

        Args:

        Returns:
            float

        Raises:
            NotImplementedError: when accessed through this class and not subclass
        """

        raise NotImplementedError


if __name__ == "__main__":
    pass
