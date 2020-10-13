#!/usr/bin/python3
# coding=utf-8
__author__ = 'zhongyujian'

import json
from who.map import china

def get_region(id):
    """
    给出一个身份证，或者前几位号码，给出所在地的省市县
    返回格式：{‘code’:0, 'region': '', message:''}
    :return:
    """
    # 初始定义
    ok_status = 0  # 正确状态码
    error_status = 1  # 错误状态码

    def response(status, region, message):
        """

        :param status:
        :param region:
        :param message:
        :return:
        """
        return {'code': status, 'region': region, 'message': message}  # 返回值

    # def load_cardArr():
    #     with open("content.json", 'rb') as f:
    #         temp = json.loads(f.read())
    #         return temp

    def check_input_length(number):
        """
        检查识别号码的长度
        :param number:
        :return:
        """
        number = str(number)
        if len(number) < 2:
            return 1
        elif 2 <= len(number) < 4:
            return 2
        elif 4 <= len(number) < 6:
            return 4
        elif len(number) >= 6:
            return 6

    length = check_input_length(id)

    if length == 1:
        return response(error_status, '', '请输入大于2位整数的号码！')
    elif length == 2:
        num = str(id)[0:2]
        dt = china['two_digit_number']
        if num in dt:
            return response(ok_status, dt[num], None)
        # print(dt[num])
        else:
            return response(error_status, '', '请检查输入号码是否正确！')
            # print_error_msg()
    elif length == 4:
        num = str(id)[0:4]
        dt = china['four_digit_number']
        if num in dt:
            return response(ok_status, dt[num], None)
        else:
            return response(error_status, '', '请检查输入号码是否正确！')
    else:
        num = str(id)[0:6]
        dt = china['six_digit_number']
        if num in dt:
            return response(ok_status, dt[num], None)
        else:
            return response(error_status, '', '请检查输入号码是否正确！')


if __name__ == '__main__':
    # 测试
    print(get_region(1))
    print(get_region(12))
    print(get_region(19))
    print(get_region(152))
    print(get_region(1526))
    print(get_region(1599))
    print(get_region(44151))
    print(get_region(441510))
    print(get_region(441480))
    print(get_region(441481))
    print(get_region(4414810000))

