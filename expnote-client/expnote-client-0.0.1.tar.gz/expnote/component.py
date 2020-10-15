from typing import Iterable, Optional, List, Dict

from expnote.config import default_stages


class ExpNoteStageComponent:

    def __init__(self, **kwargs):
        self.objs = kwargs

    def get(self, name: str):
        return self.objs[name]

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.objs[key] = value


class ExpNoteComponent:

    def __init__(self, name: str, description: str = "", stages: Iterable[str] = default_stages):
        self.name = name
        self.description = description
        self.stages = {k: None for k in stages}

    def check(self):
        return sum([1 if v is not None else 0 for v in self.stages.values()]) == len(self.stages)

    def get(self, stage) -> ExpNoteStageComponent:
        assert stage in self.stages.keys()
        return self.stages[stage]

    def set(self, stage, **kwargs):
        assert stage in self.stages.keys(), \
            f"{stage} is unrecognizable stage. should be one of {','.join(self.stages.keys())}"
        assert self.get(stage) is None, f"stage {stage} is already set"

        self.stages[stage] = ExpNoteStageComponent(**kwargs)

    def __getitem__(self, key):
        assert key in self.stages.keys()

        s = self.get(key)
        if s is not None:
            return s

        self.set(key)
        return self.get(key)

    def copy_stage(self, copy_from: str, copy_to: str):
        assert copy_from in default_stages
        assert copy_to in default_stages

        self.stages[copy_to] = self.stages[copy_from]


class ExpNoteComponentGroup:

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.components: Dict[str, ExpNoteComponent] = {}

    def list_components(self) -> List[ExpNoteComponent]:
        return list(self.components.values())

    def find_component(self, name: str) -> Optional[ExpNoteComponent]:
        return self.components.get(name, None)

    def add_component(self, name: str, description: str = "", stages: Iterable[str] = default_stages):
        assert name not in self.components.keys(), f"component {name} already exists."
        self.components[name] = ExpNoteComponent(name, description, stages)

    def __getitem__(self, key):
        c = self.find_component(key)
        if c is not None:
            return c

        self.add_component(key)
        return self.find_component(key)
