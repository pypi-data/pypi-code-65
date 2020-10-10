import sys

def list_lol(the_list,indent=False,level=0,fn=sys.stdout):
    for item in the_list:
        if isinstance(item,list):
            list_lol(item,indent,level+1,fn)
        else:
            if indent:
                for num in range(level):
                    print("\t",end='',file=fn)
            print(item,file=fn)

