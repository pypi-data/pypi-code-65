# AS-j_Package

def first_law(u,a,t):
    print("we will multiply 'a' and 't' then minus 'u'")
    v = u-a*t
    print(v)

def second_law(u,t,a):
    s = u*t+(1/2*a*(t**2))
    print(s)

conditions = ['v',
'u',
'a',
's']
def third(v,u,a,s):
    ask = input("what you want to calculate: ")
    if ask == 'v':
        v = ((2*a*s)+(u**2))**0.5
        v = str(v)
        print('velocity is ' +v)
    if ask == 'u':
        u = (((v**2)-(2*a*s))**0.5)
        u = str(u)
        print('initial velocity: '+u)
    if ask == 's':
        s = ((v**2)-(u**2)/2*a)
        s = str(s)
        print('displacement is '+s)
    if ask == 'a':
        a = ((v**2)-(u**2)/2*s)
        a = str(a)
        print('acceleration is '+a)
    if ask not in conditions:
        print(f"invalid function connot calculate *{ask}*")