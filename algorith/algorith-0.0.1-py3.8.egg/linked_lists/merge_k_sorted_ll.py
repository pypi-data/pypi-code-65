import numpy as np

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    @staticmethod
    def print_lst_s(n):
        while n.next is not None:
            print(n.val)
            n=n.next
        print(n.val)
    
    def print_lst(self):
        ListNode.print_lst_s(self)


def array_to_lst(a):
    for i in np.arange(len(a)-1,-1,-1):
        if i==len(a)-1:
            ln = ListNode(a[i])
        else:
            ln = ListNode(a[i],ln)
    return ln


def create_and_prnt():
    ln3 = ListNode(5)
    ln2 = ListNode(3,ln3)
    ln1 = ListNode(1,ln2)
    n = ln1
    while n is not None:
        print(n.val)
        n=n.next


def merge_two(n1,n2):
    """
    Given two sorted linked list with head nodes
    n1 and n2, merges n2 into n1 so that the resulting
    list is still sorted.
    """
    if n1 is None:
        return n2
    if n2 is None:
        return n1
    n_prev1 = None; n_prev2 = None
    while True:        
        while (n1 is not None)\
                and n2.val>=n1.val:
            n_prev1=n1
            n1=n1.next
        n_prev1.next = n2
        if n1 is None:
            break
        while (n2 is not None)\
                and n2.val < n1.val:
            n_prev2=n2
            n2=n2.next
        n_prev2.next=n1
        if n2 is None:
            break

def merge_lst_array(arr):
    none_cnt = 0
    ix=0; i=0; val = np.inf
    for n in arr:
        if n is not None:
            if val > n.val:
                n0 = n
                ix=i
                val = n.val
        else:
            none_cnt+=1
        i+=1
    if none_cnt == len(arr):
        return None
    for i in range(len(arr)):
        if i != ix:
            merge_two(n0,arr[i])
    return n0


def tst_merge_two():
    n1 = array_to_lst([1,3])
    n2 = array_to_lst([2,4])
    merge_two(n1,n2)
    n1.print_lst()
    n1 = array_to_lst([1,5,8])
    n2 = array_to_lst([2,3])
    merge_two(n1,n2)
    n1.print_lst()


def tst_merge_arr():
    n1 = array_to_lst([1,3])
    n2 = array_to_lst([2,4])
    n3 = array_to_lst([5,10])
    arr=[n1,n2,n3]
    nn = merge_lst_array(arr)
    nn.print_lst()
    n1 = None
    n2 =  array_to_lst([1])
    nn = merge_lst_array([n1,n2])
    n1 = array_to_lst([1,4,5])
    n2 = array_to_lst([1,3,4])
    n3 = array_to_lst([2,6])
    nn = merge_lst_array([n1,n2,n3])
    merge_lst_array([None])

