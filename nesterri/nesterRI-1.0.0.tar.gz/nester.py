"""
Module that contains useful functions
for lists with a lot of lists within.
"""
def print_lol(the_list):
    """
    Print a list in a list
    in a reccursive way.
    """
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
    else:
        print("THAT")
