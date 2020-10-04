from gmrs.graph.node import Node


class Task(Node):
    def __init__(self, id, fnc=lambda: []):
        super().__init__(self)
        self.id = id
        self.fnc = fnc


class LeafTask(Task):
    def __init__(self, label):
        self.skill = label
        pass


def extract_vars(label):
    m = re.search(r'\[(.*?)\]', label)
    return m.group(0)


def refinement():
    pass
