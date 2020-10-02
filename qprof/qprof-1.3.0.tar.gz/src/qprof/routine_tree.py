# ======================================================================
# Copyright CERFACS (July 2019)
# Contributor: Adrien Suau (adrien.suau@cerfacs.fr)
#
# This software is governed by the CeCILL-B license under French law and
# abiding  by the  rules of  distribution of free software. You can use,
# modify  and/or  redistribute  the  software  under  the  terms  of the
# CeCILL-B license as circulated by CEA, CNRS and INRIA at the following
# URL "http://www.cecill.info".
#
# As a counterpart to the access to  the source code and rights to copy,
# modify and  redistribute granted  by the  license, users  are provided
# only with a limited warranty and  the software's author, the holder of
# the economic rights,  and the  successive licensors  have only limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using, modifying and/or  developing or reproducing  the
# software by the user in light of its specific status of free software,
# that  may mean  that it  is complicated  to manipulate,  and that also
# therefore  means that  it is reserved for  developers and  experienced
# professionals having in-depth  computer knowledge. Users are therefore
# encouraged  to load and  test  the software's  suitability as  regards
# their  requirements  in  conditions  enabling  the  security  of their
# systems  and/or  data to be  ensured and,  more generally,  to use and
# operate it in the same conditions as regards security.
#
# The fact that you  are presently reading this  means that you have had
# knowledge of the CeCILL-B license and that you accept its terms.
# ======================================================================

from collections import Counter
import typing as ty

from qprof.routine import Routine, BaseRoutineWrapper
from qprof.exporters import BaseExporter, default_exporters
from qprof.data import ProgramData


class RoutineTree:
    def __init__(self, main_routine, gate_times: dict, **framework_kwargs):
        self._factory = RoutineNodeFactory()
        self._root = self._factory.get(
            Routine(main_routine, **framework_kwargs), gate_times
        )
        # Create the data structure that will store the call data.
        self._program_data: ProgramData = ProgramData(
            self._root.self_time + self._root.subroutines_times
        )
        # Enter the recursive exploration.
        self._root.first_pass_routines_data(self._program_data)

    def export(self, exporter: BaseExporter) -> ty.Union[str, bytes]:
        return exporter.export(self._program_data)


class RoutineNode:
    def __init__(
        self,
        routine: BaseRoutineWrapper,
        factory: "RoutineNodeFactory",
        gate_times: dict,
    ):
        self._routine = routine
        self._subroutines: ty.Dict["RoutineNode", int] = Counter(
            []
            if routine.is_base
            else [factory.get(rout, gate_times) for rout in routine]
        )
        self._calls = dict()
        for item, count in self._subroutines.items():
            self._calls[item] = self._calls.get(item, 0) + count
        self._calls = Counter(self._calls)
        # Computing routine timings
        self.self_time = (
            sum(
                gate_times[r.name.upper()] * count if r.is_base else 0
                for r, count in self._subroutines.items()
            )
            if not self.is_base
            else self._get_gate_time(gate_times, self.name)
        )
        self.subroutines_times = sum(
            count * (subrout.self_time + subrout.subroutines_times)
            for subrout, count in self._subroutines.items()
            if not subrout.is_base
        )

    @staticmethod
    def _get_gate_time(gate_times: ty.Dict[str, int], gate_name: str) -> int:
        upper_gate_name: str = gate_name.upper()
        if upper_gate_name not in gate_times:
            raise RuntimeError(
                f"The gate '{gate_name}' is considered as a base gate but is not "
                f"present in the provided gate times. Provided gate times are: "
                f"{gate_times}. Please add the gate '{gate_name}' in the provided "
                f"gate execution times."
            )
        return gate_times[upper_gate_name]

    @property
    def name(self):
        return "Unknown" if not self._routine.name else self._routine.name

    @property
    def is_base(self):
        return self._routine.is_base

    def first_pass_routines_data(self, data: ProgramData):
        data.add_subroutine(self.name)
        data.add_entry_point_call(self.name, 1, self.self_time, self.subroutines_times)
        self._first_pass_routines_data_impl(data)

    def _first_pass_routines_data_impl(
        self, data: ProgramData, number_of_calls: int = 1
    ):
        # Subroutines index
        indices_global_data = data.indices
        if self.name not in indices_global_data:
            data.add_subroutine(self.name)

        # Explore subroutines
        for rout, count in self._subroutines.items():
            number_of_subroutine_calls: int = count * number_of_calls
            rout._first_pass_routines_data_impl(data, number_of_subroutine_calls)
            data.add_subroutine_call(
                self.name,
                rout.name,
                number_of_subroutine_calls,
                number_of_subroutine_calls * rout.self_time,
                number_of_subroutine_calls * rout.subroutines_times,
            )


class RoutineNodeFactory:
    def __init__(self):
        self._cache: ty.Dict[BaseRoutineWrapper, "RoutineNode"] = dict()

    def get(
        self, routine_wrapper: BaseRoutineWrapper, gate_times: dict,
    ) -> "RoutineNode":
        if routine_wrapper not in self._cache:
            self._cache[routine_wrapper] = RoutineNode(
                routine_wrapper, self, gate_times
            )
        return self._cache[routine_wrapper]


def profile(
    routine, gate_times: dict, exporter: ty.Union[str, BaseExporter], **framework_kwargs
) -> ty.Union[str, bytes]:
    """Profile the given routine.

    :param routine: The routine to profile.
    :param gate_times: A dictionary whose keys are routine names and values are
        the execution time of the associated routine name.
    :param exporter: The output format to use. Can be either an instance of a
        subclass of BaseExporter or a string. Possible string values can be found in
        the keys of qprof.exporters.default_exporters.
    :return: a string that is formatted like gprof's output.
    """
    tree = RoutineTree(routine, gate_times, **framework_kwargs)
    if type(exporter) is str:
        exporter: BaseExporter = default_exporters[exporter]()
    return tree.export(exporter)
