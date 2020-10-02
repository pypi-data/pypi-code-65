#coding = utf-8
import os

#os.system("ping www.baidu.com")
#os.system("cmd")
#os.startfile("C:\Program Files (x86)\Tencent\WeChat\WeChat.exe")

#print(os.name)
#print(os.sep)
#print(repr(os.linesep))

#print(os.stat("myfile1.py"))

#print(os.getcwd())

#os.chdir("d:")
#os.mkdir("shuji")
'''
path = os.getcwd()
list = os.walk(path)

for dirpath,dirnames,filenames in list:
    for dir in dirnames:
        print(os.path.join(dirpath,dir))

    for file in filenames:
        print(os.path.join(dirpath,file))
    print("############")
 '''

import shutil
import zipfile

#压缩
shutil.make_archive()
shutil.copyfile("a.txt","a_1.txt")