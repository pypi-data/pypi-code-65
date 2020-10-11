# -*- encoding: utf-8 -*-
'''
@文件    :datadef.py
@说明    :
@时间    :2020/09/02 21:54:28
@作者    :caimmy@hotmail.com
@版本    :0.1
'''

from dataclasses import dataclass, field

@dataclass
class DbConfig:
    """
    数据库的配置参数
    """
    host: str
    dbname: str
    user: str
    password: str
    port: int = 3306

    pool_size: int = 100
    pool_recycle: int = 600

@dataclass
class OperResult:
    """
    操作的返回结果，携带操作结果信息
    """
    code: int = -1
    msg: str = "gen error"
    data: dict = field(default_factory=dict)

    @property
    def toDict(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data
        }

    def setSuccess(self, data={}):
        self.code = 0
        self.msg = ""
        self.data = data

    def setNotExists(self):
        self.code = 404
        self.msg = "not exists"