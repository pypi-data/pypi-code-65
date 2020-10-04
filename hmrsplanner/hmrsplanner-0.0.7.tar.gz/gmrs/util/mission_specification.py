#!/usr/bin/python
from gmrs.model.mission.operator import Operator


def composit_task(ref_type, *tasks):
    op = Operator(ref_type)
    for t in tasks:
        op.addEdge(t)


def add_refinement(origin, refinement):
    op = Operator(refinement[0])
    op.addEdges(refinement[1:])


def set_location(node, location):
    pass
