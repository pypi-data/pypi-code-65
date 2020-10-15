from typing import List, Optional, Dict, Iterable

from expnote.component import ExpNoteComponentGroup
from expnote.config import default_stages


class ExpNoteProject:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.component_groups: Dict[str, ExpNoteComponentGroup] = {}

    def list_groups(self) -> List[ExpNoteComponentGroup]:
        return list(self.component_groups.values())

    def find_group(self, name) -> Optional[ExpNoteComponentGroup]:
        return self.component_groups.get(name, None)

    def add_group(self, name: str, description: str = ""):
        assert self.find_group(name) is None, f"group {name} already exists."
        self.component_groups[name] = ExpNoteComponentGroup(name, description)

    def add_component(self, group: str, name: str, description: str = "",
                      stages: Iterable[str] = ("train", "test", "val")):
        if self.find_group(group) is None:
            self.add_group(group)
        self.component_groups[name].add_component(name, description, stages)

    def set_component_object(self, group: str, component: str, stage: str,
                             stages: Iterable[str] = default_stages,
                             **kwargs):
        if self.find_group(group) is None:
            self.add_group(group)
        g = self.find_group(group)
        if g.find_component(component) is None:
            g.add_component(component, stages=stages)
        c = g.find_component(component)
        c.set(stage, **kwargs)

    def __getitem__(self, key):
        g = self.find_group(key)
        if g is not None:
            return g

        self.add_group(key)
        return self.find_group(key)

    def exp(self, name: Optional[str] = None) -> 'ExpNoteExperiment':
        from expnote.experiment import ExpNoteExperiment
        exp = ExpNoteExperiment(self, name)
        return exp
