
from ursina import *


from . import common
from .engine import Engine3D
from .mouse4t import Mouse4T
模擬3D引擎 = Engine3D
__all__ = [ 
            '模擬3D引擎', 'Entity', 'EditorCamera',
            '模擬進行中','模擬主迴圈', '新增3D物件', 'color','Vec3','Vec4','Vec2',
            '按住的鍵', '滑鼠','天空',
            ]

按住的鍵 = held_keys
滑鼠 = Mouse4T()
天空 = Sky
######## top level function
# import __main__
# __main__.按住的鍵 = held_keys


def simulate():
    if not common.is_engine_created:
        Engine3D()

    common.stage.simulate()


模擬主迴圈 = simulate
模擬進行中 = simulate

######## top level function

def add_entity(*args, **kwargs):
    if not common.is_engine_created:
        Engine3D()
    return common.stage.add_entity(*args, **kwargs)

新增3D物件 = add_entity





if __name__ == '__main__' :
    pass
    
