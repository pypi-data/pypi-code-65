import numpy as np
import uuid

class TreeNode():
    def __init__(self,val,left,right,\
                parent=None,key=None,
                left_size=0):
        self.val=val
        self.left=left
        self.right=right
        self.parent=parent
        ##WARNING: Don't trust this if you delete from the tree.
        self.left_size=left_size
        if key is None:
            self.key=val

    def __gt__(self,node2):
        return self.key>node2.key
    
    def __eq__(self,node2):
        return self.key==node2.key
    
    def __lt__(self,node2):
        return self.key<node2.key

class Tree():
    def __init__(self,root):
        self.root=root

    def insert(self,z):
        y=None
        x=self.root
        num_less=0
        while x is not None:
            y=x
            if z.key<x.key:
                x.left_size+=1
                x=x.left
            else:
                num_less+=x.left_size+1
                x=x.right                             
        z.parent=y
        if y is None:
            self.root=z #Tree was empty
        elif z.key<y.key:
            y.left=z
        else: y.right=z
        ##WARNING: Don't trust this if you delete from the tree.
        return num_less

    def transplant(self,u,v):
        """
        Does not update v.left or v.right.
        Doing so is the caller's responsibility.
        """
        if u.parent is None:
            self.root=v
        elif u==u.parent.left:
            u.parent.left=v
        else:
            u.parent.right=v
        if v is not None:
            v.parent=u.parent

    def delete(self,z):
        if z.left is None:
            self.transplant(z,z.right)
        elif z.right is None:
            self.transplant(z,z.left)
        else: 
            y=tree_min(z.right)
            if y.parent != z:##See fig 12.4 (d)
                self.transplant(y,y.right)
                y.right=z.right
                y.right.parent=y
            self.transplant(z,y)
            y.left=z.left
            y.left.parent=y


def walk_inorder(x):
    if x is not None:
        walk_inorder(x.left)
        print(x.val,end=",")
        walk_inorder(x.right)

def walk_preorder(x):
    if x is not None:
        print(x.val,end=",")
        walk_inorder(x.left)
        walk_inorder(x.right)

def walk_postoder(x):
    if x is not None:
        walk_inorder(x.left)
        walk_inorder(x.right)
        print(x.val,end=",")


def tree_search(x,k):
    if x is None or k==x.key:
        return x
    if k<x.key:
        return tree_search(x.left,k)
    else:
        return tree_search(x.right,k)

def tree_search_iterative(x,k):
    while x is not None and k!=x.key:
        if k<x.key:
            x=x.left
        else:
            x=x.right

def tree_min(tn):
    while tn.left is not None:
        tn=tn.left
    return tn.left

def tree_successor(x):
    if x.right is not None:
        return tree_min(x.right)
    y=x.parent
    ## To find y we simply go up the tree
    # from x until we encounter a node that
    # is the left child of its parent.
    while y is not None and x.key==y.right.key:
        x=y
        y=y.parent
    return y

def tst():
    tn = TreeNode(6,None,None)
    tn.left=TreeNode(5,None,None,parent=tn)
    tn.left.left=TreeNode(2,None,None,parent=tn.left)
    tn.left.right=TreeNode(5,None,None,parent=tn.left)
    tn.right=TreeNode(7,None,None,parent=tn)
    tn.right.right=TreeNode(8,None,None,parent=tn.right)
    walk_inorder(tn)
    print("")
    walk_preorder(tn)
    print("")
    walk_postoder(tn)
    print("")


def tst_tree_creation():
    tn = TreeNode(5,None,None)
    trr = Tree(tn)
    t_10 = TreeNode(10,None,None)
    trr.insert(t_10)
    t_1 = TreeNode(1,None,None)
    trr.insert(t_1)
    t_7 = TreeNode(7,None,None)
    trr.insert(t_7)
    walk_inorder(trr.root)
    print("\n")
    trr.delete(t_7)
    walk_inorder(trr.root)

