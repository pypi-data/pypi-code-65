def list_lol(the_list,indent=False,level=0):
    for item in the_list:
        if isinstance(item,list):
            list_lol(item,indent,level+1)
        else:
            if indent:
                for num in range(level):
                    print("\t",end='')
            print(item)

