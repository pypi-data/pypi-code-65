import os
import re
import sys

# 遍历文件夹
def walkFile(workdir,pattern,replacement):
    for dirpath, dirnames, filenames in os.walk(os.path.realpath(workdir)):
        # 遍历文件
        for f in filenames:
            doRename(workdir,f,pattern,replacement)

# 执行重命名
def doRename(workdir,filename,pattern,replaceMent):
    workdir = os.path.realpath(workdir)
    matcies = re.search(pattern, filename, flags=0)
    print("<=  " + os.path.join(workdir, filename))
    if matcies:
        newFileName = re.sub(pattern, replaceMent, filename, count=0, flags=0)
        old_name = os.path.join(workdir, filename)
        new_name = os.path.join(workdir, newFileName)
        print("=>  " + old_name + "\t--->\t"+ new_name)
        os.rename(old_name,new_name)
    else:
        print("no match")


def main():
    if(len(sys.argv) < 4):
        print("just-rename <workdir> <pattern> <replacement>")
        return

    workdir = sys.argv[1]
    pattern = sys.argv[2]
    replacement = sys.argv[3]

    print("--"*10)
    print("workdir:\t"+workdir)
    print("pattern:\t"+pattern)
    print("replacement:\t"+replacement)
    print("--"*10)

    walkFile(workdir,pattern,replacement)


if __name__ == '__main__':
    main()