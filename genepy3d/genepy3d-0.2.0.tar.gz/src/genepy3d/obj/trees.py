import os
import re

from scipy import interpolate

import requests

import numpy as np
import pandas as pd
import anytree
from anytree import search, PreOrderIter
from anytree.walker import Walker

from genepy3d.util import plot as pl
from genepy3d.io.base import CatmaidApiTokenAuth


class Tree:
    """Tree in 3D.
    
    Attributes:
        id (int): tree ID.
        name (str): tree name.
        nodes (anytree): structure of tree nodes.    
    
    """
    
    def __init__(self,_nodes,_id=0,_name="GeNePy3D"):
        self.nodes = _nodes
        self.id = _id
        self.name = _name
    
    @staticmethod
    def build_treenodes(nodes_tbl, connectors_tbl):
        """Building tree object using anytree package.
        
        Args:
            nodes_tbl (pandas dataframe): tree nodes table.
            connectors_tbl (pandas dataframe): connectors table.
        
        """        
        
        nodes = {}
        
        # get connector nodes
        conlst = []
        if connectors_tbl is not None:
            conlst = connectors_tbl.index.values.astype('int') # it may happen similar (ske,treenode) for 2 different connector id 
        
        # build treenodes
        for i in range(len(nodes_tbl)):
            nodeid = int(nodes_tbl.index[i])
            _x, _y, _z, _r, _structure_id = tuple(nodes_tbl.iloc[i][["x","y","z","r","structure_id"]])
            nodes[nodeid] = anytree.Node(nodeid,x=_x,y=_y,z=_z,r=_r,structure_id=_structure_id)
        
        # assign others features
        for i in range(len(nodes_tbl)):
            nodeid = int(nodes_tbl.index[i])
            
            # assign their parents
            parentnodeid = int(nodes_tbl.iloc[i]['parent_treenode_id'])
            if parentnodeid != -1:
                nodes[nodeid].parent = nodes[parentnodeid]
                
            # assign connectors
            if nodeid in conlst:
                _connrel = connectors_tbl.loc[nodeid]['relation_id'] # could be "pre or post synaptic"
                _connid = connectors_tbl.loc[nodeid]['connector_id'] 
            else:
                _connrel = "None"
                _connid = -1
            nodes[nodeid].connector_relation = _connrel
            nodes[nodeid].connector_id = _connid
            
        return nodes
    
    @classmethod
    def from_table(cls,nodes_tbl,connectors_tbl=None,tree_id=0,tree_name='genepy3d'):
        """Build tree from dataframes.
        
        Args:
            nodes_tbl (pandas dataframe): tree nodes table.
            connectors_tbl (pandas dataframe): connector table.
            tree_id (int): tree ID.
            tree_name (str): tree name.
        
        """
        
        # check nodes_tbl
        if isinstance(nodes_tbl,pd.DataFrame):
            lbls = nodes_tbl.columns.values
            if all(lbl in lbls for lbl in ['treenode_id','structure_id','x','y','z','r','parent_treenode_id']):
                nodes_tbl_refined = nodes_tbl.dropna()
            else:
                raise Exception("can not find 'treenode_id','structure_id','x','y','z','r','parent_treenode_id' within the dataframe.")
        else: 
            raise Exception("nodes_tbl must be pandas dataframe.")
        
        # constraint some columns of nodes to int
        nodes_tbl_refined['structure_id'] = nodes_tbl_refined['structure_id'].astype('int')
        nodes_tbl_refined['treenode_id'] = nodes_tbl_refined['treenode_id'].astype('int')
        nodes_tbl_refined['parent_treenode_id'] = nodes_tbl_refined['parent_treenode_id'].astype('int')
        
        # reset index
        nodes_tbl_refined.drop_duplicates(subset=["treenode_id"],inplace=True) # make sure unique index
        nodes_tbl_refined.set_index('treenode_id',inplace=True) # reset dataframe index
        
        # check connectors_tbl
        connectors_tbl_refined = None
        if connectors_tbl is not None:
            # check dfcon columns
            if isinstance(connectors_tbl,pd.DataFrame): 
                lbls = connectors_tbl.columns.values
                if all(lbl in lbls for lbl in ['treenode_id','connector_id','relation_id']):
                    connectors_tbl_refined = connectors_tbl.dropna()
                else:
                    raise Exception("can not find 'treenode_id','connector_id','relation_id' within the dataframe.")
            else:
                raise Exception("connectors_tbl must be pandas dataframe.")
            
            # constraint columns to int
            connectors_tbl_refined['connector_id'] = connectors_tbl_refined['connector_id'].astype('int')
            connectors_tbl_refined['treenode_id'] = connectors_tbl_refined['treenode_id'].astype('int')
            
            # reset index
            connectors_tbl_refined.drop_duplicates(subset=["treenode_id"],inplace=True) # make sure unique index
            connectors_tbl_refined.set_index("treenode_id",inplace=True) # reset dataframe index
        
        # build tree node structure
        nodes = cls.build_treenodes(nodes_tbl_refined,connectors_tbl_refined)
        
        return cls(nodes,tree_id,tree_name)
                       
    @classmethod
    def from_swc(cls,filepath):
        """Build tree from SWC file.
        
        Args:
            filepath (str): path to swc file.
        
        """
        
        data = []
        
        # extract info from file
        f = open(filepath,'r')
        for line in f:
            if line[0]!='#':
                tmp = []
                
                elemens = re.split(r'\r|\n| |\s', line)
                for ile in elemens:
                    if ile!='':
                        tmp.append(float(ile))
                
                data.append(tmp)
                
        f.close()
    
        # build dataframe and cast columns types
        if len(data)!=0:
            
            tree_name = os.path.basename(filepath).split(".swc")[0]
            tree_id = 0
            
            dfneu = pd.DataFrame(data,columns=['treenode_id', 'structure_id', 'x', 'y', 'z', 'r', 'parent_treenode_id'])            
            
            dfneu.dropna(inplace=True)
            
            # cast type
            dfneu['treenode_id'] = dfneu['treenode_id'].astype('int')
            dfneu['structure_id'] = dfneu['structure_id'].astype('int')
            dfneu['parent_treenode_id'] = dfneu['parent_treenode_id'].astype('int')
            
            # reset index
            dfneu.drop_duplicates(subset=["treenode_id"],inplace=True) # make sure unique index
            dfneu.set_index('treenode_id',inplace=True) # reset dataframe index
            # build tree node structure
            nodes = cls.build_treenodes(dfneu,None)
            return cls(nodes,tree_id,tree_name)
        else:
            raise ValueError("Errors when reading file.")
    
    @classmethod
    def from_catmaid_server(cls,catmaid_host,token,project_id,neuron_id):
        """Build tree from CATMAID.
        
        Args:
            catmaid_host (str): address of CATMAID server
            token (str): authenticated string
            project_id (int): project ID
            neuron_id (int): neuron ID
        
        """
        
        subneu, subcon = [], []
        
        linkrequest = catmaid_host+'{}/skeleton/{}/json'.format(project_id,neuron_id)
        res = requests.get(linkrequest,auth=CatmaidApiTokenAuth(token))
        
        if res.status_code!=200:
            raise ValueError('something wrong: check again your host, token, project id or neuron id.')
        else:
            if isinstance(res.json(),dict):
                raise ValueError('something wrong: check again your project id or neuron id.')
            else: # should be a list
                res = np.array(res.json())
                
                # get neuron name
                try:
                    neuron_name = res[0]
                except:
                    neuron_name = 'genepy3d'
                
                # get neuron info
                try:
                    for iske in res[1]:
                        if iske[1] is not None:
                            iske_sub = [iske[0], 0, iske[3], iske[4], iske[5], iske[6], iske[1]]
                        else:
                            iske_sub = [iske[0], 0, iske[3], iske[4], iske[5], iske[6], -1]
                        subneu.append(iske_sub)
                except:
                    subneu = []
                
                # get connector info
                try:
                    for icon in res[3]:
                        relation_type = 'presynaptic_to'
                        if icon[2]==1:
                            relation_type = 'postsynaptic_to'
                        icon_sub = [icon[1], icon[0], relation_type]
                        subcon.append(icon_sub)
                except:
                    subcon = []
        
        # create dfneu dataframe
        if len(subneu)==0:
            raise ValueError('neuron is empty!')
        else:
            dfneu = pd.DataFrame(subneu,columns=['treenode_id','structure_id','x','y','z','r','parent_treenode_id'])
            # remove nan
            dfneu.dropna(inplace=True)
            # cast type
            dfneu['treenode_id'] = dfneu['treenode_id'].astype('int')
            dfneu['structure_id'] = dfneu['structure_id'].astype('int')
            dfneu['parent_treenode_id'] = dfneu['parent_treenode_id'].astype('int')
            # reset index
            dfneu.drop_duplicates(subset=["treenode_id"],inplace=True) # make sure unique index
            dfneu.set_index('treenode_id',inplace=True) # reset dataframe index
        
        # create dfcon dataframe
        if len(subcon)==0:
            dfcon = None
        else:
            dfcon = pd.DataFrame(subcon,columns=['connector_id','treenode_id','relation_id'])
            # remove nan
            dfcon.dropna(inplace=True)
            # constraint columns to int
            dfcon['connector_id'] = dfcon['connector_id'].astype('int')
            dfcon['treenode_id'] = dfcon['treenode_id'].astype('int')
            # reset index
            dfcon.drop_duplicates(subset=["treenode_id"],inplace=True) # make sure unique index
            dfcon.set_index("treenode_id",inplace=True) # reset dataframe index
            
        
        # build tree node structure
        nodes = cls.build_treenodes(dfneu,dfcon)
        return cls(nodes,neuron_id,neuron_name)
    
    def get_root(self):
        """Return root node ID.
        
        Returns:
            int.
        
        """
        
        # may contain many roots
        return list(filter(lambda nodeid: self.nodes[nodeid].parent is None, self.nodes.keys()))
    
    def get_parent(self,nodeid):
        """Return parent id of node id.
        """
        
        return self.nodes[nodeid].parent.name
    
    def get_children(self,nodeid):
        """Return children ids of nodeid.
        """
        
        return [node.name for node in self.nodes[nodeid].children]
    
    def get_preorder_nodes(self,rootid=None):
        """Return list of nodes in tree.
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        return [node.name for node in PreOrderIter(self.nodes[_rootid])]
        
    def get_nodes_number(self,rootid=None):
        """Return the number of nodes in tree.
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
            
        return len(self.get_preorder_nodes(_rootid))
    
    def get_leaves(self,rootid=None):
        """Return list of leaf node IDs.
        
        Returns:
            list of int.
        
        """
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        return [leaf.name for leaf in self.nodes[_rootid].leaves]
    
    def get_branchingnodes(self,rootid=None):
        """Return branching node IDs.
        
        Returns:
            list of int.
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        return [n.name for n in search.findall(self.nodes[_rootid],filter_=lambda node: len(node.children)>1)]
    
    def get_connectors(self,rootid=None):
        """Return list of connector node IDs.
        
        Returns:
            Pandas dataframe whose indices are node IDs and values are corresponding connector types, connector ids.
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        connector_nodes = np.array([[node.name,node.connector_relation,node.connector_id] for node in PreOrderIter(self.nodes[_rootid])])
        df = pd.DataFrame({"relation":connector_nodes[:,1],"id":connector_nodes[:,2].astype(np.integer)},
                           index=connector_nodes[:,0].astype(np.integer))
        subdf = df[(df['relation']!='None')&(df['id']!=-1)]
        
        return subdf
    
    def get_coordinates(self, nodeid=None, rootid=None):
        """Return coordinates of given nodes.
        
        Args:
            nodes (int | list of int): list of node IDs.
            
        Returns:
            Pandas dataframe whose indices are node IDs and values are corresponding coordinates.
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        if nodeid is None:
            nodelst = [node.name for node in PreOrderIter(self.nodes[_rootid])]
        elif nodeid is not None:
            if isinstance(nodeid,(int,np.integer)): # only one item.
                nodelst = [nodeid]
            elif isinstance(nodeid,(list,np.ndarray)):
                nodelst = nodeid
            else:
                raise Exception("node_id must be array-like.")
        
        coors = np.array([[self.nodes[i].x,self.nodes[i].y,self.nodes[i].z] for i in nodelst])
        df = pd.DataFrame({'nodeid':nodelst,'x':coors[:,0],'y':coors[:,1],'z':coors[:,2]})
        df.set_index('nodeid',inplace=True)
        return df    
    
    def compute_length(self,nodeid=None,rootid=None):
        """Return lengths for given nodes.
        """
        
        from genepy3d.obj.curves import Curve
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
            
        if nodeid is not None: # a list of nodes
            return Curve(self.get_coordinates(nodeid).values).compute_length()
        else:
            segments = self.decompose_segments(_rootid)
            total_length = 0
            for seg in segments.values():
                total_length += Curve(self.get_coordinates(seg).values).compute_length()
            return total_length
    
    def compute_spine(self,rootid=None):
        """Return spine node IDs (longest branch from root).
        
        Returns:
            list of int.
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
            
        segments = self.decompose_leaves(_rootid)
        segment_lengths = [self.compute_length(seg) for seg in segments.values()]
        return list(segments.values())[np.argmax(segment_lengths)]
    
    def compute_strahler_order(self, nodeid=None, rootid=None):
        """Return strahler order for given node IDs.
        
        Args:
            nodeid (int|list[int]): list of node IDs.
        
        Returns:
            Pandas serie whose indices are node IDs and values are corresponding strahler orders.
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        try:
            # check if strahler orders already computed
            _ = self.nodes[_rootid].strahler 
        except:
            preorder_lst = np.array([node.name for node in PreOrderIter(self.nodes[_rootid])])
            for i in preorder_lst[-1::-1]:
                n = self.nodes[i]
                if n.is_leaf:
                    n.strahler = 1
                else:
                    children_strahler = np.array([[k.name, k.strahler] for k in n.children])
                    if len(children_strahler)==1:
                        n.strahler = children_strahler[0,1]
                    else:
                        nbmax = len(np.argwhere(children_strahler[:,1]==np.max(children_strahler[:,1])).flatten())
                        if nbmax>=2:
                            n.strahler = np.max(children_strahler[:,1]) + 1
                        else:
                            n.strahler = np.max(children_strahler[:,1])

        if nodeid is None:
            nodelst = [node.name for node in PreOrderIter(self.nodes[_rootid])]
        elif nodeid is not None:
            if isinstance(nodeid,int): # only one item.
                nodelst = [nodeid]
            elif isinstance(nodeid,(list,np.ndarray)):
                nodelst = nodeid
            else:
                raise Exception("nodeid must be array-like.")
                
        strahler_orders = [self.nodes[i].strahler for i in nodelst]
        
        return pd.Series(strahler_orders,name='strahler_order',index=nodelst)
    
    # def compute_orientation(self,nodeid=None,nb_avg=1,rootid=None):
    #     """Compute orientation vectors at given nodes.
        
    #     The orientation vector depends on node type (e.g. root, branching node, leaf, normal node).
        
    #     Args:
    #         nodeid (int|array of int): list of node IDs.
    #         nb_avg (int): number of neighboring nodes used to average the orientation.     
    #     """
        
    #     # internal funcs
    #     def walk_to_parent(_nid,nb_steps,_rootid):
    #         target = _nid
    #         target_lst = []
    #         it = 0
    #         while(it < nb_steps):
    #             it = it + 1
    #             target = self.get_parent(target)
    #             if target is not None:
    #                 target_lst.append(target)
    #             else:
    #                 break
    #             if target in self.get_branchingnodes(_rootid):
    #                 break
    #         return target_lst
        
    #     def walk_to_children(_nid,nb_steps):
    #         target = [_nid]
    #         target_lst = []
    #         it = 0
    #         while(it < nb_steps):
    #             it = it + 1
    #             target = self.get_children(target[0])
    #             if len(target)==1:
    #                 target_lst.append(target[0])
    #             else:
    #                 break
    #         return target_lst
        
    #     if rootid is None:
    #         _rootid = self.get_root()[0]
    #     else:
    #         _rootid = rootid
        
    #     # get list of nodes
    #     if nodeid is None:
    #         nodeidlst = self.get_preorder_nodes(_rootid)
    #     elif isinstance(nodeid,(int,np.integer)):
    #         nodeidlst = [nodeid]
    #     else:
    #         nodeidlst = nodeid
            
    #     dic = {}
            
    #     for nid in nodeidlst:
    #         item = {}
    #         source_coors = self.get_coordinates(nid,_rootid).values.flatten()
            
    #         if nid==_rootid: # root
                
    #             # vectors toward children
    #             children = self.get_children(nid)
    #             for child in children:
    #                 target_lst = [child]
    #                 target_lst = target_lst + walk_to_children(child,nb_avg-1)
    #                 target_coors = self.get_coordinates(target_lst,_rootid).values
    #                 mean_target_coors = np.mean(target_coors,axis=0)
    #                 item[str(nid)+"-"+str(target_lst[0])] = geo.vector2points(source_coors,mean_target_coors)
            
    #         elif nid in self.get_branchingnodes(_rootid): # branchingnodes
                
    #             # vector toward parent
    #             target_lst = walk_to_parent(nid,nb_avg,_rootid)                
    #             target_coors = self.get_coordinates(target_lst,_rootid).values
    #             mean_target_coors = np.mean(target_coors,axis=0)
    #             item[str(nid)+"-"+str(target_lst[0])] = geo.vector2points(source_coors,mean_target_coors)
                
    #             # vectors toward children
    #             children = self.get_children(nid)
    #             for child in children:
    #                 target_lst = [child]
    #                 target_lst = target_lst + walk_to_children(child,nb_avg-1)
    #                 target_coors = self.get_coordinates(target_lst,_rootid).values
    #                 mean_target_coors = np.mean(target_coors,axis=0)
    #                 item[str(nid)+"-"+str(target_lst[0])] = geo.vector2points(source_coors,mean_target_coors)
            
    #         else: # leaf or normal node
                
    #             # vector toward parent
    #             target_lst = walk_to_parent(nid,nb_avg,_rootid)                
    #             target_coors = self.get_coordinates(target_lst,_rootid).values
    #             mean_target_coors = np.mean(target_coors,axis=0)
    #             item[str(nid)+"-"+str(target_lst[0])] = geo.vector2points(source_coors,mean_target_coors)

    #         dic[nid] = item
        
    #     return dic
    
    def path(self,target,source=None,rootid=None):
        """Find list of nodes going from source node to target node.
        
        Args:
            target (int): target node ID.
            source (int): source node ID.
            
        Returns:
            list of traveled node IDs included source and target node IDs.
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        if source==None:
            source = _rootid
            
        w = Walker()
        res = w.walk(self.nodes[source],self.nodes[target])
        return [n.name for n in res[0]] + [res[1].name] + [n.name for n in res[2]] 
    
    def extract_subtrees(self,nodeid,to_children=True,separate_children=False,rootid=None):
        """Extract a sub tree from the given node.
        
        Args:
            nodeid (int): node ID that becomes new root node in the sub tree.
            to_children (bool): if False, then extract upper subtree, else lower subtrees are extracted.
            separate_children (bool): if True, then different subtrees are extracted from children. Only available if ``to_children = True``.
            rootid (int): ID of root.
        
        Returns:
            list of Tree objects.
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        # list of nodes to be extracted by default
        nodelst = [nodeid] + [item.name for item in self.nodes[nodeid].descendants]
        
        if to_children == False: # then, getting nodes above the nodeid, i.e. subtree toward root node.
            fullnodelst = [_rootid] + [item.name for item in self.nodes[_rootid].descendants]
            nodelst = np.setdiff1d(fullnodelst,nodelst)
            subnodes = {}
            # first copy node properties
            for nid in nodelst:
                ref_node = self.nodes[nid]
                new_node = anytree.Node(nid, connector_id=ref_node.connector_id, 
                                        connector_relation=ref_node.connector_relation,
                                        r=ref_node.r, x=ref_node.x, y=ref_node.y, z=ref_node.z,
                                        structure_id=ref_node.structure_id)
                subnodes[nid] = new_node
            # second assign node relationship
            for nid in nodelst:
                try:
                    parent_id = self.nodes[nid].parent.name
                    subnodes[nid].parent = subnodes[parent_id]
                except:
                    subnodes[nid].parent = None # root node
            
            # copynodes = copy.deepcopy(self.nodes) # dict copy
            # copynodes[nodeid].parent = None
            # subnodes = {nid:copynodes[nid] for nid in nodelst}
            
            return Tree(subnodes,self.id,self.name)
        
        else: # get nodes starting from nodeid, i.e. subtrees toward its children.
            if separate_children==True:
                mychildren = [item.name for item in self.nodes[nodeid].children]
                if len(mychildren)>1: # more than one children
                    data = []
                    for mychild in mychildren:
                        subnodelst = [nodeid, mychild] + [item.name for item in self.nodes[mychild].descendants]
                        subnodes = {}
                        # first copy node properties
                        for nid in subnodelst:
                            ref_node = self.nodes[nid]
                            new_node = anytree.Node(nid, connector_id=ref_node.connector_id, 
                                                    connector_relation=ref_node.connector_relation,
                                                    r=ref_node.r, x=ref_node.x, y=ref_node.y, z=ref_node.z,
                                                    structure_id=ref_node.structure_id)
                            subnodes[nid] = new_node  
                        # second assign node relationship
                        for nid in subnodelst:
                            if nid != nodeid:
                                parent_id = self.nodes[nid].parent.name
                                subnodes[nid].parent = subnodes[parent_id]
                            else:
                                subnodes[nid].parent = None # set nodeid as new root

                        # copynodes = copy.deepcopy(self.nodes) # dict copy
                        # others = np.setdiff1d(mychildren,mychild)
                        # for otherid in others:
                        #     copynodes[otherid].parent = None
                        # copynodes[nodeid].parent = None
                        # subnodes = {nid:copynodes[nid] for nid in subnodelst}
                        
                        data.append(Tree(subnodes,self.id,self.name))
                        
                    return data
            
            # in case of only one child
            subnodes = {}
            
            # first copy node properties
            for nid in nodelst:
                ref_node = self.nodes[nid]
                new_node = anytree.Node(nid, connector_id=ref_node.connector_id, 
                                        connector_relation=ref_node.connector_relation,
                                        r=ref_node.r, x=ref_node.x, y=ref_node.y, z=ref_node.z,
                                        structure_id=ref_node.structure_id)
                subnodes[nid] = new_node  
            # second assign node relationship
            for nid in nodelst:
                if nid != nodeid:
                    parent_id = self.nodes[nid].parent.name
                    subnodes[nid].parent = subnodes[parent_id]
                else:
                    subnodes[nid].parent = None
            
            # copynodes = copy.deepcopy(self.nodes) # dict copy
            # subnodes = {nid:copynodes[nid] for nid in nodelst}
            # subnodes[nodeid].parent = None       
            
            return Tree(subnodes,self.id,self.name) 
    
    def copy(self,rootid=None):
        """Copy tree.
        """
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
            
        return self.extract_subtrees(nodeid=_rootid,rootid=_rootid)
    
    def prune_leaves(self,nodeid=None,length=None,rootid=None):
        """Prune leaf branching based on its length.
        
        Args:
            nodeid (list [int]): list of leaves IDs to be pruned. If None, then take all leaves into account.
            length (float): length threshold for pruning leaf branching from leaves given by nodeid.
            rootid (int): ID of root.
            
        Returns:
            new Tree after pruning.
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        if length is None:
            _length = np.inf
        else:
            _length = length
        
        segments = self.decompose_segments(_rootid)
        
        if nodeid is None:
            leafnodes = self.get_leaves(_rootid)
        else:
            leafnodes = nodeid
        
        subnodes = {}
        nodelst = []
        
        for seg in segments.values():
            contain_leaf = (np.sum([leaf in seg for leaf in leafnodes])>=1)
            seg_len = self.compute_length(seg)
            if (~contain_leaf) | (contain_leaf & (seg_len >= _length)):
                # copy node properties
                for nid in seg:
                    if nid not in nodelst:
                        ref_node = self.nodes[nid]
                        new_node = anytree.Node(nid, connector_id=ref_node.connector_id, 
                                                connector_relation=ref_node.connector_relation,
                                                r=ref_node.r, x=ref_node.x, y=ref_node.y, z=ref_node.z,
                                                structure_id=ref_node.structure_id)
                        subnodes[nid] = new_node
                        nodelst.append(nid)
        
        # assign node relationship
        for nid in nodelst:
            try:
                parent_id = self.nodes[nid].parent.name
                subnodes[nid].parent = subnodes[parent_id]
            except:
                subnodes[nid].parent = None # root node
        
        return Tree(subnodes,self.id,self.name)

    
    def decompose_segments(self,rootid=None):
        """Decompose tree in segments separating by branching nodes.
        
        Returns:
            dictionary whose each item is a list of nodes IDs specifying indices of a segment.
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        segments = {}
        controlnodes = self.get_leaves(_rootid) + self.get_branchingnodes(_rootid) + [_rootid]
        for it in range(len(controlnodes)):
            nodeid = controlnodes[it]
            branch = [n.name for n in self.nodes[nodeid].path]
            idx = len(branch)-2
            while(idx != -1):
                if branch[idx] in controlnodes:
                    subbranch = branch[idx:]
                    segments[str(branch[idx])+"_"+str(nodeid)] = subbranch
                    break
                idx = idx - 1
        
        return segments
    
    def decompose_spines(self,rootid=None):
        """Decompose tree into list of spines starting from root node.
        
        Returns:
            list whose each item is an array of nodes IDs specifying a specific spine.
        
        """
        # maximal number of recursions using in deepcopy()
        # sys.setrecursionlimit(recursion_limit)
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        data = {}
        
        # first check if there're many branches at root
        mychildren = [item.name for item in self.nodes[_rootid].children]
        if len(mychildren)>1: # more than one children
            subtrees = self.extract_subtrees(nodeid=_rootid,separate_children=True,rootid=_rootid)
            for subtree in subtrees:
                subdata = subtree.decompose_spines()
                data = {**data, **subdata}
        else:
            spinenodes = self.compute_spine(_rootid)
            spinename = str(spinenodes[0])+'_'+str(spinenodes[-1])
            data[spinename] = spinenodes
            branchingnodes = self.get_branchingnodes(_rootid)
            if len(branchingnodes)!=0:
                spinebranchingnodes = list(filter(lambda node : node in spinenodes, branchingnodes))
                
                for node in spinebranchingnodes:
                    subtrees = self.extract_subtrees(nodeid=node,separate_children=True,rootid=_rootid)
                    for subtree in subtrees:
                        firstchild = subtree.nodes[node].children[0].name
                        if firstchild not in spinenodes:
                            subdata = subtree.decompose_spines()
                            data = {**data, **subdata}
                
        return data
    
    def decompose_leaves(self,rootid=None):
        """Decompose tree into segments starting from root to every leaf.
        
        Returns:
            dictionary whose keys are leaf IDs and values are list of node IDs from root to leaf.
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        dic = {}
        for leaf in self.get_leaves(_rootid):
            dic[leaf] = self.path(target=leaf,source=_rootid)
        
        return dic
    
    def resample(self,unit_length=None,rootid=None,spline_order=1,smooth_spline=False,decompose_method="branching"):
        """Resampling tree.
        
        Args:
            rootid (int): id of root node.
            unit_length (float): if not None, then ``npoints`` is calculated from it.
            spline_order (uint): 1 means linear interpolation.
            
        Returns:
            Tree() resampled tree.
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        branching_nodes = self.get_branchingnodes(_rootid)
        
        newnodes = {} # new resampled nodes
        
        # TODO: smatter handling of ID (e.g. remove ancient IDs, new_ID_generator reuse free ancient IDs)
        nodeid_max = max(self.nodes.keys()) # for now new node ID is counted from old maximal ID
        newnodeid = nodeid_max + 1
        
        if decompose_method=="branching":
            segments = self.decompose_segments(rootid=_rootid)
        elif decompose_method=="spine":
            segments = self.decompose_spines(rootid=_rootid)
            brnode_link = [] # contain link between branching node and new closest resampled node.
        else:
            raise Exception("accept only 'branching' or 'spine' decomposition")
        
        for seg in segments.values():
            # print(seg)
            try:
                # get segment coordinates
                coors = self.get_coordinates(seg,rootid).values

                # try to remove duplicates before interpolation
                _, uix = np.unique(coors,axis=0,return_index=True)
                unique_coors = coors[np.sort(uix)]
                unique_seg = np.array(seg)[np.sort(uix)]
                
                # interpolate coordinates
                if smooth_spline==True:
                    s = None
                else:
                    s = 0
                    
                if unique_coors.shape[0]<(spline_order+1): # linear interpolation
                    coefcoors, to = interpolate.splprep(unique_coors.T.tolist(),k=1,s=s)
                else:
                    coefcoors, to = interpolate.splprep(unique_coors.T.tolist(),k=spline_order,s=s)

                # interpolate radius
                r = [self.nodes[nodeid].r for nodeid in unique_seg]
                coefr = interpolate.splrep(to,r,k=1,s=0)
            except:
                return None
                
                # # print("ok");
                # # simply copy nodes to new nodes
                # for i in range(len(seg)):
                #     if seg[i] not in newnodes.keys():
                #         node = self.nodes[seg[i]]
                #         newnodes[seg[i]] = anytree.Node(seg[i],connector_id=node.connector_id, 
                #                                         connector_relation=node.connector_relation, r=node.r, 
                #                                         x=node.x, y=node.y, z=node.z, structure_id=node.structure_id)
                #     if i != 0:
                #         newnodes[seg[i]].parent = newnodes[seg[i-1]]

                # continue # go to next segment

            # in case of success interpolation
            if unit_length == None:
                n = len(seg)
            else:
                n = max(int(np.round(self.compute_length(unique_seg)/unit_length)),2) # new sampled points, must have at least 2 points
            tn = np.linspace(0,1,n)
            xn, yn, zn = interpolate.splev(tn,coefcoors)
            rn = interpolate.splev(tn,coefr)
            
            # in case of spine decomposition
            if decompose_method=="spine":
                newix_flag = np.ones(len(tn))*-1
                # newix_supp = []
                for node in branching_nodes:
                    # index start from "1" not "0" since we don't consider branching node at begin.
                    idx = np.argwhere(node==np.array(unique_seg)[1:]).flatten()
                    if len(idx)!=0:
                        oldix = idx[0]+1
                        newix = np.argwhere(tn<to[oldix]).flatten()[-1]
                        newix_flag[newix] = node
                        # newix_supp.append([node,oldix,to[oldix],newix,tn[newix]])
                    
            # print(newix_flag)
            # print(newix_supp)

            # add two end nodes to newnodes
            for iseg in [unique_seg[-1],unique_seg[0]]:
                if iseg not in newnodes.keys():
                    node = self.nodes[iseg]
                    newnodes[iseg] = anytree.Node(iseg,connector_id=node.connector_id,
                                                  connector_relation=node.connector_relation,
                                                  r=node.r, x=node.x, y=node.y, z=node.z, structure_id=node.structure_id)

            # add resampled nodes and link to parent
            check_node = newnodes[unique_seg[-1]]   
            i = n - 2
            while i != -1:
   
                if i == 0:
                    if decompose_method=="spine":
                        if newix_flag[i]!=-1:
                            brnode_link.append([int(newix_flag[i]),unique_seg[0]])
                    
                    new_node = newnodes[unique_seg[0]]
                else:
                    if decompose_method=="spine":
                        if newix_flag[i]!=-1:
                            brnode_link.append([int(newix_flag[i]),newnodeid])
                    
                    
                    new_node = anytree.Node(newnodeid, connector_id=-1, connector_relation='None',
                                            r=rn[i], x=xn[i], y=yn[i], z=zn[i], structure_id=0)
                    
                    newnodes[newnodeid] = new_node
                    # if (newnodeid==696):
                    #     print(unique_seg)

                check_node.parent = new_node

                check_node = new_node
                newnodeid = newnodeid + 1
                i = i - 1

        if decompose_method=="spine":
            for link in brnode_link:
               mychildren = [item.name for item in newnodes[link[0]].children]
               try:
                   for mychild in mychildren:
                       newnodes[mychild].parent = newnodes[link[1]]
               except:
                   print(link)
                   print(mychildren)
                   print(newnodes[link[1]])
                   raise Exception("failed, segment {}".format(unique_seg))
                   
            for brnode in branching_nodes:
                if((brnode != _rootid) & (newnodes[brnode].parent == None)):
                    del newnodes[brnode]
        
        # new resampled neuron
        return Tree(newnodes)
    
    def compute_orientation(self,decomposed_method="leaf",sigma=0,rootid=None):
        """Return orientation vector and angles with x, y and z.
        
        Args:
            decomposed_method (str): "leaf", "spine" or "branching", method for cutting neuronal trace
            sigma (float): sigma used in Gaussian filter for smoothing tree branches
            rootid (int): ID of root
            
        Returns:
            Pandas dataframe containing vectors and angles at every nodes.
        """
        
        from genepy3d.obj.curves import Curve
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
            
        nodeid_lst, segkey_lst = [],[]
        vecx_lst, vecy_lst, vecz_lst = [], [], []
        thetax_lst, thetay_lst, thetaz_lst = [], [], []
        
        # decompose tree into segments
        if decomposed_method=="spine":
            segments = self.decompose_spines(_rootid)
        elif decomposed_method=="leaf":
            segments = self.decompose_leaves(_rootid)
        else:
            segments = self.decompose_segments(_rootid)
        
        for key,seg in segments.items():
            
            # save node IDs
            nodeid_lst = nodeid_lst + list(seg)
            
            # save segment keys
            segkey_lst += [key for _ in range(len(seg))]
            
            # create curve
            coors = self.get_coordinates(seg).values
            crv = Curve(coors)
            
            # smooth if need
            if sigma > 0:
                crv = crv.convolve_gaussian(sigma)
                
            vecs, thetas = crv.compute_orientation()
            
            vecx_lst = vecx_lst + vecs[:,0].tolist()
            vecy_lst = vecy_lst + vecs[:,1].tolist()
            vecz_lst = vecz_lst + vecs[:,2].tolist()
            
            thetax_lst = thetax_lst + thetas[:,0].tolist()
            thetay_lst = thetay_lst + thetas[:,1].tolist()
            thetaz_lst = thetaz_lst + thetas[:,2].tolist()
            
        # making dataframe
        df = pd.DataFrame({"nodeid":nodeid_lst,
                           "seg_key":segkey_lst, 
                           "vecx":vecx_lst,
                           "vecy":vecy_lst,
                           "vecz":vecz_lst,
                           "thetax":thetax_lst,
                           "thetay":thetay_lst,
                           "thetaz":thetaz_lst})
        
        df.set_index("nodeid",inplace=True)            
        return df

    def compute_local_3d_scale(self,r_lst,dim_param=None,decomposed_method="leaf",rootid=None):
        """Compute 3d local scale of neuron.
        
        Args:
            r_lst (list): list of scales (radius of curvature)
            dim_param (dic): parameters for dimension decomposition
            decomposed_method (str): "leaf", "spine" or "branching", method for cutting neuronal trace
            rootid (int): ID of root
            
        Returns:
            Pandas dataframe containing local 3D scale, 1D, 2D, 3D flags, curvature and torsion
        
        """
        
        from genepy3d.obj.curves import Curve
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        nodeid_lst, ls_lst, plane_line_lst, line_lst, threed_lst = [], [], [], [], []
        curvature_lst, torsion_lst = [], []
        segkey_lst = []
    
        # decompose tree into segments
        if decomposed_method=="spine":
            segments = self.decompose_spines(_rootid)
        elif decomposed_method=="leaf":
            segments = self.decompose_leaves(_rootid)
        else:
            segments = self.decompose_segments(_rootid)
        
        for key,seg in segments.items():

            # create curve
            coors = self.get_coordinates(seg).values
            crv = Curve(coors)
            
            # intrinsic dimension decomposition
            try:
                if dim_param is not None:
                    ls_res, intrinsic_res = crv.compute_local_3d_scale(r_lst,
                                                                       dim_param["eps_seg_len"],
                                                                       dim_param["eps_crv_len"],
                                                                       dim_param["sig_step"],
                                                                       dim_param["eps_kappa"],
                                                                       dim_param["eps_tau"],
                                                                       return_dim_results=True)
                else: # use default params
                    ls_res, intrinsic_res = crv.compute_local_3d_scale(r_lst,return_dim_results=True)
            except:
                raise Exception(seg)
    
            # save segment keys
            segkey_lst += [key for _ in range(len(seg))]
            
            # curvature and torsion
            curvature_lst += crv.compute_curvature().tolist()
            torsion_lst += crv.compute_torsion().tolist()
    
            # save node IDs
            nodeid_lst = nodeid_lst + list(seg)
            
            # local 3D scale
            ls_lst = ls_lst + list(ls_res)
    
    #         if(len(np.argwhere(np.array(ls_res)>=70).flatten())==len(ls_res)):
    #             print(seg)
    
            # 1D, 2D, 3D flags
            pl_flag = np.zeros((len(seg),len(r_lst)))
            l_flag = np.zeros((len(seg),len(r_lst)))
            for i in range(len(r_lst)):
                res = intrinsic_res[i]
                for plids in res["planeline_pred"]:
                    pl_flag[plids[0]:plids[1]+1,i]=1.
                for lids in res["line_pred"]:
                    l_flag[lids[0]:lids[1]+1,i]=1.
            threed_flag = (pl_flag + np.ones(pl_flag.shape))%2 # xor bit (3D is the opposite of planeline)
    
            plane_line_lst = plane_line_lst + pl_flag.tolist()
            line_lst = line_lst + l_flag.tolist()
            threed_lst = threed_lst + threed_flag.tolist()
        
        # making dataframe
        df = pd.DataFrame({"nodeid":nodeid_lst,
                           "seg_key":segkey_lst, 
                           "local_scale":ls_lst,
                           "plane_line_flag":plane_line_lst,
                           "line_flag":line_lst,
                           "threed_flag":threed_lst,
                           "curvature":curvature_lst,"torsion":torsion_lst})
        
    #     df.drop_duplicates("nodeid",keep=False) # drop branching nodes
        df.set_index("nodeid",inplace=True)            
        return df
    
    def summary(self):
        """Return a brief  summary of tree.
        
        Returns:
            pandas serie.
        
        """
        
        index = ['id',
                 'name',
                 'root',
                 'nb_nodes',
                 'nb_leaves',
                 'nb_branchingnodes',
                 'nb_connectors']
        
        data = [self.id,
                self.name,
                self.get_root(),
                [len(self.get_preorder_nodes(_rootid)) for _rootid in self.get_root()],
                # len(list(PreOrderIter(self.nodes[self.get_root()]))),
                [len(self.get_leaves(_rootid)) for _rootid in self.get_root()],
                [len(self.get_branchingnodes(_rootid)) for _rootid in self.get_root()],
                [len(self.get_connectors(_rootid)) for _rootid in self.get_root()]]
        
        return pd.Series(data,index=index)
    
    def to_curve(self,nodeid=None):
        """Convert a segment on tree given by nodeid list to Curve.
        """
        from genepy3d.obj.curves import Curve
        return Curve(self.get_coordinates(nodeid).values)
    
    def to_points(self,nodeid=None):
        """Convert to Points.
        """
        
        from genepy3d.obj.points import Points
        return Points(self.get_coordinates(nodeid).values)
    
    def plot(self,ax,projection='3d',rootid=None,spine_only=False,
             show_root=True,show_leaves=True,show_branchingnodes=True,show_connectors=True,
             root_args={},leaves_args={},branchingnodes_args={},connectors_args={},
             weights=None,weights_display_type="c",point_args = {},show_cbar=False,cbar_args={},
             line_args={},scales=(1.,1.,1.),equal_axis=True):
        """Plot tree.
        
        Args:
            ax: plot axis.
            projection (str): we support *3d, xy, xz, yz* modes.
            spine_only (bool): if True, then only plot tree spine.
            show_root (bool): if True, then display root node.
            show_leaves (bool): if True, then display leaves nodes.
            show_branchingnodes (bool): if True, then display branching nodes.
            show_connectors (bool): if True, then display connector nodes.
            root_args (dic): plot params for root node.
            leaves_args (dic): plot params for leaves nodes.
            branchingnodes_args (dic): plot params for branching nodes.
            connectors_args (dic): plot params for connectors nodes.
            weights (pandas serie): serie indexed by node ID and contains corresponding weights
            weights_display_type (str): "s" for point size or "c" for point color.
            point_args (dic): point plot params.
            line_args (dic): line plot params.
            scales (tuple of float): use to set x, y and z scales.
            equal_axis (bool): fix equal axes.
            
        Note:
            spine_only should be removed. We can consider it as a curve.
        
        
        """
        
        _root_args={'s':50,'c':'red'}
        for key,val in root_args.items():
            _root_args[key] = val
        
        _leaves_args={'s':8,'c':'blue'}
        for key,val in leaves_args.items():
            _leaves_args[key] = val
        
        _branchingnodes_args={'s':20,'c':'magenta'}
        for key,val in branchingnodes_args.items():
            _branchingnodes_args[key] = val
        
        _connectors_args={'s':70,'c':'red','alpha':0.7}
        for key,val in connectors_args.items():
            _connectors_args[key] = val
        
        _point_args = {"s":10,"alpha":0.8,"c":"k","cmap":"viridis"}
        for key,val in point_args.items():
            _point_args[key] = val
        
        _line_args={'alpha':0.8,'c':'k'}
        for key,val in line_args.items():
            _line_args[key] = val
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        if show_root==True:
            coors = self.get_coordinates(_rootid).values
            x, y, z = coors[:,0], coors[:,1], coors[:,2]
            pl.plot_point(ax,projection,x,y,z,scales,_root_args)
        
        if spine_only==True:
            
            spine_nodes = self.compute_spine(_rootid)
            
            coors = self.get_coordinates(spine_nodes).values
            x, y, z = coors[:,0], coors[:,1], coors[:,2]
            pl.plot_line(ax,projection,x,y,z,scales,_line_args)
            
            if weights is not None:
                weight_args = _point_args.copy()
                weight_args[weights_display_type] = weights.loc[spine_nodes]
                if "vmin" not in weight_args.keys():
                    weight_args["vmin"] = weights.min()
                if "vmax" not in weight_args.keys():
                    weight_args["vmax"] = weights.max()
                plo = pl.plot_point(ax,projection,x,y,z,scales,weight_args)
                if (show_cbar == True):
                    if "shrink" in cbar_args:
                        shrink = cbar_args["shrink"]
                    else:
                        shrink = 0.7
                    cbar = ax.figure.colorbar(plo,shrink=shrink)
                    
                    if "ticks" in cbar_args:
                        cbar.set_ticks(cbar_args["ticks"])
                    if "ticklabels" in cbar_args:
                        cbar.set_ticklabels(cbar_args["ticklabels"])
            
            if show_leaves==True:
                coors = self.get_coordinates(spine_nodes[-1]).values
                x, y, z = coors[:,0], coors[:,1], coors[:,2]
                pl.plot_point(ax,projection,x,y,z,scales,_leaves_args)
        
        else:
            
            segments = self.decompose_segments(_rootid)
            cbar_flag = True
            for seg_nodes in segments.values():
                coors = self.get_coordinates(seg_nodes).values
                x, y, z = coors[:,0], coors[:,1], coors[:,2]
                segment_args = _line_args.copy()
                
                pl.plot_line(ax,projection,x,y,z,scales,segment_args)
                
                if weights is not None:
                    weight_args = _point_args.copy()
                    weight_args[weights_display_type] = weights.loc[seg_nodes]
                    if "vmin" not in weight_args.keys():
                        weight_args["vmin"] = weights.min()
                    if "vmax" not in weight_args.keys():
                        weight_args["vmax"] = weights.max()
                    plo = pl.plot_point(ax,projection,x,y,z,scales,weight_args)
                    if (show_cbar == True) & (cbar_flag == True):
                        if "shrink" in cbar_args:
                            shrink = cbar_args["shrink"]
                        else:
                            shrink = 0.7
                        cbar = ax.figure.colorbar(plo,shrink=shrink)
                        
                        if "ticks" in cbar_args:
                            cbar.set_ticks(cbar_args["ticks"])
                        if "ticklabels" in cbar_args:
                            cbar.set_ticklabels(cbar_args["ticklabels"]);
                        cbar_flag = False
            
            if show_leaves==True:
                leaves_nodes = self.get_leaves(_rootid)
                coors = self.get_coordinates(leaves_nodes).values
                x, y, z = coors[:,0], coors[:,1], coors[:,2]
                pl.plot_point(ax,projection,x,y,z,scales,_leaves_args)
                
            if show_branchingnodes==True:
                inter_nodes = self.get_branchingnodes(_rootid)
                if len(inter_nodes)!=0:
                    coors = self.get_coordinates(inter_nodes).values
                    x, y, z = coors[:,0], coors[:,1], coors[:,2]
                    pl.plot_point(ax,projection,x,y,z,scales,_branchingnodes_args)
                    
            if show_connectors==True:
                connectors_nodes = self.get_connectors(_rootid).index.values
                if len(connectors_nodes)!=0:
                    coors = self.get_coordinates(connectors_nodes).values
                    x, y, z = coors[:,0], coors[:,1], coors[:,2]
                    pl.plot_point(ax,projection,x,y,z,scales,_connectors_args)
                
        if equal_axis==True:
            if projection != '3d':
                ax.axis('equal')
            else:
                param = pl.fix_equal_axis(self.get_coordinates(rootid=_rootid).values / np.array(scales))
                ax.set_xlim(param['xmin'],param['xmax'])
                ax.set_ylim(param['ymin'],param['ymax'])
                ax.set_zlim(param['zmin'],param['zmax'])
                
        if projection != '3d':
            if projection=='xy':
                xlbl, ylbl = 'X', 'Y'
            elif projection=='xz':
                xlbl, ylbl = 'X', 'Z'
            else:
                xlbl, ylbl = 'Y', 'Z'
            ax.set_xlabel(xlbl)
            ax.set_ylabel(ylbl)
        else:
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            

    
                
            
            
            
        
        
        
        
        
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
        
        
        
        
