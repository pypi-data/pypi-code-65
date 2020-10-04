#!/usr/bin/python3
import time #时间_内置库

#列表求平均值
def m(a):    
    b=0
    for c in a:
        b+=float(c)
    return b/len(a)


#日期时间
def t(a='%Y-%m-%d %H:%M:%S',b=0,c=0,d=0,e='+'): #输出时间格式,输入时间，输入时间格式，时间秒（加减时间），+或-（默认+）
    if b==0:
        return time.strftime(a,time.localtime())    #当前时间
    else:
        try:
            z=time.strptime(b,c)
            if e=='+':
                y=time.mktime(z)+d
            elif e=='-':
                y=time.mktime(z)-d
            else:
                return '第5个参数请输入+或-'
            return time.strftime(a, time.localtime(y))
        except:
            return "输入时间格式错误"