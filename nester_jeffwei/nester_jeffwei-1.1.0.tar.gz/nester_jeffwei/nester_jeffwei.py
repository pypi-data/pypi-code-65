def list_lol(the_list,level):
    for item in the_list:
        if isinstance(item,list):
            list_lol(item,level+1)
        else:
            for num in range(level):
                print("\t",end='')
            print(item)

