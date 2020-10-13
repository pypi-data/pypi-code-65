import json
from os import path
import torch as th
import scipy.sparse
from typing import (
    Literal,
    Optional,
    Tuple,
    Union, Set
)
import random
from collections import defaultdict

"""
self.ent2id = {ent: idx for idx, ent in enumerate(ent_set)}
self.rel2id = {rel: idx for idx, rel in enumerate(rel_set)}
self.rel2id.update(
        {rel + '_reverse': idx + len(self.rel2id) for idx, rel in enumerate(rel_set)})

self.id2ent = {idx: ent for ent, idx in self.ent2id.items()}
self.id2rel = {idx: rel for rel, idx in self.rel2id.items()}

"""

PATTERNS = Literal['hrt', 'rht', 'htr']


class KnowledgeKit:
    """Provide only necessary methods"""

    def __init__(self,
                 kg_file: str,
                 indexed: bool = False,
                 pattern: PATTERNS = 'hrt',
                 sep: str = ',',
                 ent2id_file: str = None,
                 rel2id_file: str = None
                 ):
        assert path.isfile(kg_file), f"{kg_file} is not exists!"
        self.ent2idx = dict()
        self.entities = set()
        self.ent_idx = set()
        self.relations = set()
        self.rel_idx = set()
        self.rel2idx = dict()
        self.head_tp = defaultdict(list)  # {head => [(r, t)]}
        self.rel_tp = defaultdict(list)  # {rel => [(h, t)]}
        self.tail_tp = defaultdict(list)  # {tail => [(h, r)]}
        self.pattern = pattern
        self.indexed = indexed
        # deal with type and entities information
        self.ent2type = dict()
        self.type2entities = defaultdict(list)
        self.tp_count = 0
        if indexed:
            # providing file is indexing [int sep int sep int] mode
            assert ent2id_file is not None and rel2id_file is not None
            self._load_ent_idx(ent2id_file, sep=sep)
            self._load_rel_idx(rel2id_file, sep=sep)
            self._build_indexed(kg_file, sep=sep)
        else:
            self._indexing_(kg_file=kg_file, sep=sep)
            self.indexed = True
            self._build_(kg_file=kg_file, sep=sep)

    def _indexing_(self, kg_file: str, sep: str):
        with open(kg_file) as fp:
            for line in fp:
                line = line.strip()
                if sep in line:
                    if self.pattern == 'hrt':
                        head, rel, tail = line.split(sep)
                    elif self.pattern == 'htr':
                        head, rel, tail = line.split(sep)
                    else:
                        rel, head, tail = line.split(sep)
                    self.entities.add(head)
                    self.entities.add(tail)
                    self.relations.add(rel)
                else:
                    print(f"{line=}")
                self.tp_count += 1
        self.ent2idx = {ent: idx for idx, ent in enumerate(self.entities)}
        self.rel2idx = {rel: idx for idx, rel in enumerate(self.relations)}
        self.idx2ent = {idx: ent for ent, idx in self.ent2idx.items()}
        self.idx2rel = {idx: rel for rel, idx in self.rel2idx.items()}
        self.ent_idx = set(list(self.idx2ent.keys()))
        self.rel_idx = set(list(self.idx2rel.keys()))

    def _load_ent_idx(self, ent2idx_file: str, sep: str):
        with open(ent2idx_file) as fp:
            for line in fp:
                if sep in line:
                    line = line.strip()
                    ent, idx = line.split(sep=sep)
                    self.entities.add(ent)
                    self.ent2idx[ent] = int(idx)
                else:
                    print(f"{line=}")
        self.idx2ent = {idx: ent for ent, idx in self.ent2idx.items()}
        self.ent_idx = list(self.idx2ent.keys())

    def _load_rel_idx(self, rel2idx_file: str, sep: str):
        with open(rel2idx_file) as fp:
            for line in fp:
                if sep in line:
                    line = line.strip()
                    rel, idx = line.split(sep=sep)
                    self.relations.add(rel)
                    self.rel2idx[rel] = int(idx)
                else:
                    print(f"{line=}")
        self.idx2rel = {idx: rel for rel, idx in self.rel2idx.items()}
        self.rel_idx = set(self.idx2rel.keys())

    def _build_(self, kg_file: str, sep: str):
        assert self.indexed
        with open(kg_file) as fp:
            for line in fp:
                line = line.strip()
                if self.pattern == 'hrt':
                    head, rel, tail = line.split(sep)
                elif self.pattern == 'htr':
                    head, tail, rel = line.split(sep)
                else:
                    rel, head, tail = line.split(sep)
                head_idx = self.ent2idx[head]
                rel_idx = self.rel2idx[rel]
                tail_idx = self.ent2idx[tail]
                self.head_tp[head_idx].append((rel_idx, tail_idx))
                self.rel_tp[rel_idx].append((head_idx, tail_idx))
                self.tail_tp[tail_idx].append((head_idx, rel_idx))

    def _build_indexed(self, kg_file, sep: str):
        """Build from given indexing kg file"""
        with open(kg_file) as fp:
            for line in fp:
                line = line.strip()
                if sep in line:
                    if self.pattern == 'hrt':
                        head, rel, tail = map(int, line.split(sep))
                    elif self.pattern == 'htr':
                        head, tail, rel = map(int, line.split(sep))
                    else:
                        rel, head, tail = map(int, line.split(sep))
                    # self.entities.update((head, tail))
                    # self.relations.add(rel)
                    self.head_tp[head].append((rel, tail))
                    self.rel_tp[rel].append((head, tail))
                    self.tail_tp[tail].append((head, rel))
                else:
                    print(f"{line=}")

    def reverse(self):
        """Add reverse edges."""
        pass

    def k_hop_metapath(self, start_ent: str, k: int = 3, limits: int = -1):
        """

        Args:
            start_ent: path start entity
            k: path length, num of rel count in a path
            limits: search limits for decrease search time, -1 for no limits

        Returns:
            List of Path, List of Pos
        """
        assert start_ent in self.entities, f"{start_ent} not in entities"
        result = list()  # finish path
        path_length = k + 2  # num_rel + head and tail
        # [paths], paths is head-r-t mode
        # in search, pop a path, replace last item with rel and append in the stack
        search_path_stack = list()
        # build init path set
        for item in self.head_tp[start_ent]:
            rel, tail = item
            search_path_stack.append([start_ent, rel, tail])
        while len(search_path_stack) != 0:
            last_item = search_path_stack.pop()
            if len(last_item) == path_length:
                result.append(last_item)
                continue
            else:
                tail = last_item.pop()
                if limits == -1:
                    for item in self.head_tp[tail]:  # [(r, t)]
                        new_path = last_item.copy().extend(item)
                        search_path_stack.append(new_path)
                else:
                    for item in random.choices(self.head_tp[tail], k=limits):
                        new_path = last_item.copy().extend(item)
                        search_path_stack.append(new_path)
        from functools import reduce

        def lengthable(im: list) -> bool:
            return len(im) == path_length

        def get_pos(ent_path):
            assert len(ent_path) == path_length
            return [i for i, _ in enumerate(ent_path)]

        assert reduce(lambda f, second: f and lengthable(second), result, True), \
            "[ERR] Meta path error"
        pos_path_l = [get_pos(i) for i in result]
        return result, pos_path_l

    def k_hop_subgraph(self, center_ent: int, max_hops: int):
        # todo
        # or just give to geo to do it
        src_l = list()
        dest_l = list()
        edges = list()
        todo_node = [center_ent]
        hops = max_hops
        assert len(src_l) == len(dest_l)
        while hops > 0:
            while len(todo_node) != 0:
                deal = todo_node.pop()
                for item in self.head_tp[deal]:
                    rel, tail = item
                    src_l.append(deal)
                    dest_l.append(tail)
                    edges.append(rel)
                    todo_node.append(tail)
                for item in self.tail_tp[deal]:
                    head, rel = item
                    src_l.append(head)
                    dest_l.append(deal)
                    edges.append(rel)
                    todo_node.append(head)
            hops = hops - 1
        return src_l, dest_l, edges

    @property
    def whole_edge_index(self):
        src_l = list()
        dest_l = list()
        edge_types = list()
        for h, rts in self.head_tp.items():
            h = int(h)
            for item in rts:
                rel, tail = item
                rel = int(rel)
                tail = int(tail)
                src_l.append(h)
                dest_l.append(tail)
                edge_types.append(rel)
        assert len(src_l) == len(dest_l) == len(edge_types)
        return [src_l, dest_l, edge_types]

    def save_coo(self, name):
        coo_tensor = th.tensor(self.whole_edge_index, dtype=th.long)
        th.save(coo_tensor, f"{name}-sde.pt")

    def k_hop_neighbors(self, center: int, hops: int = 1, max_neighbors = -1):
        """
        Return khop neighbor set of given center node
        Args:
            center: entity
            hops: >=1, default is 1

        Returns:
            entity set
        """
        result = set()
        result.add(center)
        current_search_stack = {center}
        next_round = set()
        hop_tmp = hops
        assert center in self.ent_idx, f"Wrong Entity"
        x_hop_neighbors = set()
        while hop_tmp > 0:
            while current_search_stack:
                e = current_search_stack.pop()
                for item in self.head_tp[e]:
                    _, tail = item
                    next_round.add(tail)
                    # result.add(tail)
                    x_hop_neighbors.add(tail)
                for item in self.tail_tp[e]:
                    h, _ = item  # h, r
                    next_round.add(h)
                    # result.add(e)
                    x_hop_neighbors.add(h)
                result.update(set(x_hop_neighbors))
                if max_neighbors < 0:
                    continue
                if len(x_hop_neighbors) >= max_neighbors:
                    x_hop_neighbors.clear()
                    break
            hop_tmp = hop_tmp - 1
            current_search_stack.update(next_round)
            next_round.clear()  # keep next_round clear
        return result

    def k_hop_neighbors_from_set(self, nodes: Set[int], hops: int = 1, max_neighbors=-1) -> set:
        neighbors = set()
        for n in nodes:
            neighbors.update(self.k_hop_neighbors(center=n, hops=hops, max_neighbors=max_neighbors))
        return neighbors


def levi(src: dict) -> Tuple[dict, dict, list, list]:
    """
    Make levi graph.

    Args:
        src: key is head, tail is list of (rel, tail)
    Returns:
        index_map_vertex, vertex_map, start, end
    """
    _INDEX_KEY = 'index'
    _TYPE_KEY = 'type'
    heads = list(src.keys())
    start = list()
    end = list()
    index = len(heads)
    vertex_map = dict()
    index_map_vertex = dict()
    for i, head in enumerate(heads):
        vertex_map[head] = dict()
        vertex_map[head][_INDEX_KEY] = i
        vertex_map[head][_TYPE_KEY] = 'e'
        index_map_vertex[i] = head
    for head, val_list in src:
        for tup in val_list:
            rel, tail = tup
            if rel not in vertex_map.keys():
                vertex_map[rel] = dict()
                vertex_map[rel][_INDEX_KEY] = index
                vertex_map[rel][_TYPE_KEY] = 'r'
                index_map_vertex[index] = rel
                index += 1
            start.append(head)
            end.append(rel)
            if tail not in vertex_map.keys():
                vertex_map[tail] = dict()
                vertex_map[tail][_INDEX_KEY] = index
                vertex_map[tail][_TYPE_KEY] = 't'
                index_map_vertex[index] = tail
                index += 1
            start.append(rel)
            end.append(tail)
    assert len(start) == len(end), "len(start) != len(end)"
    return index_map_vertex, vertex_map, start, end


class Relation:
    def __init__(self, rel: Union[str, int]):
        self.relation = rel
        self.instances = list()
        self.entities = set()

    def add_instance(self, i: tuple):
        self.instances.append(i)

    def add_entity(self, e: Union[int, str]):
        self.entities.add(e)

    def add_entities(self, *es):
        self.entities.update(set(es))


if __name__ == '__main__':
    kg = KnowledgeKit(kg_file="/Users/yat/code/testdata/nell/train2id-regulation.txt",
                      indexed=True, ent2id_file="/Users/yat/code/testdata/nell/entity2id.txt",
                      rel2id_file="/Users/yat/code/testdata/nell/relation2id.txt", sep='\t',
                      pattern='htr')
    print(f"{kg.k_hop_neighbors_from_set({100, 10, 20}, hops=1)=}")
    print(f"{kg.k_hop_neighbors(center=100, hops=1)=}")
    print(f"{kg.k_hop_neighbors(center=20, hops=1, max_neighbors=30)=}")
    print(f"{kg.k_hop_neighbors(center=10, hops=1, max_neighbors=30)=}")

