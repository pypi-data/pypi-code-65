"""
Module that contains useful functions
for lists with a lot of lists within.
"""
def print_lol(the_list, numberOfTabs):
    """
    Print a list in a list
    in a reccursive way.
    """
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, numberOfTabs + 1)
        else:
            for num in range(numberOfTabs):
                print("\t", end = '')
            print(each_item)
