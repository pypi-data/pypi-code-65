'''
@File       : czyutils.py
@Copyright  : rainbol
@Date       : 2020/10/9
@Desc       : Czy test used tools
'''

import json
from itertools import product
import uuid


def dict_a_in_b(dict_a, dict_b):
    '''
        is dict_a in dict_b, return True/False
        字典a是否在字典b中,返回true/false

        demo:
            # 预期结果
            expected = {'code': [1,2,3], 'msg': 'success!'}
            # 实际结果
            actual_result = {

                'msg': 'success!',
            'code': [1,2,3],
                'data': [{"username": "yoyo", "qq": "283340479"}]
            }
            print(dict_a_in_b(expected, actual_result))

    '''

    result = None
    for key in dict_a:
        if (key in dict_b) and (dict_a[key] == dict_b[key]):
            result = True
        else:
            return False
    return result


def ListToObjectToStr(*args, object=False):
    '''
        list变str,嵌套value值嵌套%s方便参数化嵌套,一般配合mixed_of_parameters方法的params_data使用
        obj=True变成对象

        demo:
            ListToObjectToStr('user_id', 'order_time', 'delivery_time') # {"user_id": "%s", "order_time": "%s", "delivery_time": "%s"}

        demo2:
            l = ['user_id', 'order_time', 'delivery_time']
            ListToObjectToStr(l) # {"user_id": "%s", "order_time": "%s", "delivery_time": "%s"}

    '''

    obj = {}
    for arg in args:
        if type(arg).__name__ == 'list':
            for l in arg:
                obj[l] = '%s'
            if object:
                return obj
            return '{}'.format(json.dumps(obj))
        obj[arg] = '%s'
    if object:
        return obj
    return '{}'.format(json.dumps(obj))


class DictToObject(dict):
    '''
        dict to object
        字典转对象
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 先调用父类的构造方法,因为传进来的是一个字典，dict这个类会把你传入的{k:v}这样的变成一个dict的类

    def __getattr__(self, item):
        # __getattr__的作用是通过x.xx的时候它会自动调用__getattr__这个方法，把你要获取的属性的key传过来
        # 比如说 user.name ,它就是调用了__getattr__，把name传给__getattr__函数，然后返回这个name的值
        value = self[item]
        if isinstance(value, dict):
            value = DictToObject(value)  # 如果是字典类型，直接返回DictToObject这个类的对象

        elif isinstance(value, list) or isinstance(value, tuple):
            # 如果是list，循环list判断里面的元素，如果里面的元素是字典，那么就把字典转成DictToObject的对象
            value = list(value)
            for index, obj in enumerate(value):
                if isinstance(obj, dict):
                    value[index] = DictToObject(obj)

        return value


def mixed_of_parameters(params_data: str, *args: list):
    '''
    参数混合嵌套:可支持多个参数
        params_data：params格式
        *args：传参
        return：params集合
    random_one:随机取一条数据即可

    demo:
        params_data = '{"username":"%s","password":"%s","user_id":"%s","sex":"%s","other_deg":"123"}'
        a_demo = ['a1', 'a2', 'a3', 'a4']
        b_demo = ['b1', 'b2', 'b3', 'b4']
        c_demo = ['c1', 'c2', 'c3', 'c4']
        d_demo = ['d1', 'd2', 'd3', 'd4']
        res = mixed_of_parameters(params_data, a_demo, b_demo, c_demo, d_demo)
        print(res)
    '''

    store_list, params_list, _variable = [], [], []
    check_length = len(args)
    try:
        json_params = json.loads(params_data)
    except Exception as e:
        raise ("json_params不为json")
    obj = DictToObject(json_params)
    for k, v in obj.items():
        if v == '%s':
            store_list.append(k)
    if not store_list:
        raise ("需要存在%s参数化关键字")
    elif check_length != len(store_list):
        raise ("params_data与参数数量不匹配")

    # 函数修饰被迭代对象来优化循环

    for _var in range(check_length):
        _variable.append(uuid.uuid4().__str__())
    for _variable in product(*args):
        data = params_data % _variable
        params_list.append(data)
    return params_list


def is_Chinese(word):
    '''
        is chinese return true/false
        判断是否是中文
    '''
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

