
from ..model.task import Task


def rft(origin_task: Task, operator, refinement_tasks):
    op = operator()
    for t in refinement_tasks:
        op.addEdge(t)
    
    origin_task.addEdge(op)
