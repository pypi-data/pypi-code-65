from xerparser.model.classes.rsrc import Resource

class Resources:

    _rsrcs = []

    def __init__(self):
        self.index = 0

    def add_resource(self, params):
        rsrc = Resource(params)
        self._rsrcs.append(rsrc)

    @staticmethod
    def get_resource_by_id(id):
        rsrc = list(filter(lambda x: x.rsrc_id == id, Resources._rsrcs))
        if len(rsrc) > 0:
            rsrc = rsrc[0]
        else:
            rsrc = None
        return rsrc

    @staticmethod
    def get_parent(id):
        rsrc = list(filter(lambda x: x.rsrc_id == id, Resources._rsrcs))
        if len(rsrc) > 0:
            rsrc = rsrc[0]
            parent = Resources.get_resource_by_id(rsrc.parent_rsrc_id)
        else:
            rsrc = None
        return rsrc


    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self._rsrcs):
            raise StopIteration
        idx = self.index
        self.index +=1
        return self._rsrcs[idx]