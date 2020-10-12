import numpy as np
import uuid

class TreeNode():
    def __init__(self,val,left,right,\
                parent=None,key=None):
        self.val=val;
        self.left=left;
        self.right=right
        self.parent=parent
        if key is None:
            self.key=val


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
