def list_lol(the_list):
    for item in the_list:
        if isinstance(item,list):
            list_lol(item)
        else:
            print(item)

