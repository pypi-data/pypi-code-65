from typing import List, Optional
from pint import UnitRegistry, UndefinedUnitError

from shyft.dashboard.time_series.sources.source import DataSource
from shyft.dashboard.time_series.view import BaseView
from shyft.dashboard.base.hashable import Hashable


class DsViewHandleError(RuntimeError):
    pass


class DsViewHandle(Hashable):
    """
    This Object combines the data_source with views. It is used to show data in ts_viewer
    """
    def __init__(self, *,
                 data_source: DataSource,
                 views: List[BaseView],
                 tag: Optional[str]=None,
                 unit_registry: Optional[UnitRegistry]=None):
        """
        Initializes an immutable, hashable ds_view_handle.

        Parameters
        ----------
        data_source: unbound data source to combine with views
        views: list of unbound views to view the data
        tag: optional uid to identify the ds view handle later
        unit_registry: optional unit_registry, is used to verify if units in data_source and views are compatible,
                       should be used provided if custom defined units are used
        """
        super().__init__()
        # check data_source is unbound
        if data_source.bound:
            raise DsViewHandleError(f'{tag}: data_source {data_source.tag} already bound!')
        data_source.bind(parent=self)

        # check views
        for view in views:
            if view.bound:
                raise DsViewHandleError(f'{tag}: data_source {view.label} already bound!')
            view.bind(parent=self)

        # check units
        try:
            temp_ureg = unit_registry or UnitRegistry()
            ds_unit_dimensionality = temp_ureg.Unit(data_source.unit).dimensionality
            for v in views:
                if not hasattr(v, 'unit'):
                    continue
                v_unit_dimensionality = temp_ureg.Unit(v.unit).dimensionality
                if not ds_unit_dimensionality == v_unit_dimensionality:
                    raise DsViewHandleError(f"{tag}: Incompatible units {data_source.unit}!!{v.unit} of {data_source} and {v}!")
        except UndefinedUnitError as u:
            raise DsViewHandleError(f"{tag}: Incompatible unit registry! Please provide one!: {u}")

        self.__data_source = data_source
        self.__views = views
        self.tag = tag or str(self.uid)

    @property
    def data_source(self):
        """
        This property returns the data source
        """
        return self.__data_source

    @property
    def views(self):
        """
        This property returns the list with all defiend views
        """
        return self.__views
