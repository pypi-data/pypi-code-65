with open("c.txt","r",encoding="utf-8") as f:
    print("The file's name is:{0}".format(f.name))
    print(f.tell())
    print("read:{0}".format(str(f.readline())))
    print(f.tell())
    f.seek(6)
    print(f.tell())
    print("read:{0}".format(str(f.readline())))