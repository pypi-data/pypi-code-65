"""
    1.python3默认递归深度100，设置方法：sys.setrecursionlimit(10000)
    
"""
def print_lol(the_list):
    for each_item in the_list:
        if isinstance(each_item , list):
            print_lol(each_item)
        else:
            print(each_item)

    
