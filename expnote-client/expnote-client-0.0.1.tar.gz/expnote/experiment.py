import pickle
from encodings.base64_codec import base64_encode
from io import StringIO, BytesIO
from pathlib import Path
from typing import Optional, Dict, Union

import yaml

from expnote.component import ExpNoteComponent, ExpNoteStageComponent
from expnote.config import default_stages
from expnote.project import ExpNoteProject


class ExpNoteExperiment:
    def __init__(self, project: ExpNoteProject, name: Optional[str] = None):
        self._name = name
        self.project = project
        self.components: Dict[str, ExpNoteComponent] = {}
        self._component_order: Dict[str, int] = {}
        self._assign_i = 0
        self.metrics = {}

    def assign(self, group: str, component: str):
        g = self.project.find_group(group)
        assert g is not None, f"group {group} does not exist"
        c = g.find_component(component)
        assert c is not None, f"component {component} does not exist in {group}"
        self.components[group] = c
        self._component_order[group] = self._assign_i
        self._assign_i += 1

    def autogen_name(self) -> str:
        group_order = list(sorted(self._component_order.keys(), key=lambda v: self._component_order[v]))
        group_component_names = [self.components[g].name for g in group_order]
        return "-".join(group_component_names)

    @property
    def name(self) -> str:
        if self._name is None:
            return self.autogen_name()
        return self._name

    def find_component(self, group: str):
        assert group in self.components.keys()
        return self.components[group]

    def __getitem__(self, key) -> ExpNoteComponent:
        return self.find_component(key)

    def __setitem__(self, key: str, value: str):
        self.assign(key, value)

    def stage(self, stage: str) -> 'ExpNoteExperimentStage':
        assert stage in default_stages
        return ExpNoteExperimentStage(self, stage)

    def result(self, **kwargs):
        self.metrics.update(kwargs)

    def _exp_dict(self):

        metric_values = {}
        for key, metric in self.metrics.items():
            try:
                yaml.dump(metric, StringIO())
                metric_values[key] = metric
            except:
                b = pickle.dumps(metric)
                metric_values[key] = base64_encode(b)

        d = {
            'name': self.name,
            'components': {k: v.name for k, v in self.components.items()},
            'metrics': metric_values
        }
        return d

    def dump(self, file: Union[str, Path]):
        file = Path(file)
        try:
            exp_result = yaml.load(file.open('r'))
            if 'exp' not in exp_result.keys():
                exp_result['exp'] = []
        except:
            exp_result = {'exp': []}
        exp_result['exp'].append(self._exp_dict())
        yaml.dump(exp_result, file.open('w'))


class ExpNoteExperimentStage:
    def __init__(self, experiment: ExpNoteExperiment, stage: str):
        self.experiment = experiment
        self.stage = stage
        self._accessed = []

    def get(self, group) -> ExpNoteStageComponent:
        self._accessed.append(group)
        return self.experiment.find_component(group).get(self.stage)

    def __getitem__(self, key) -> ExpNoteStageComponent:
        return self.get(key)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        all_items = set(self.experiment.components.keys())
        used_items = set(self._accessed)
        unused = all_items - used_items
        assert len(unused) == 0, f"component groups {unused} are unused while stage."
