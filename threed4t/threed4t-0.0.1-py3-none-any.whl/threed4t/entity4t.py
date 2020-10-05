from ursina import *

class Entity4t(Entity):
    def __init__(self, *args, **kwargs):
        # handle default model and texture
        if not 'model' in kwargs:
            kwargs['model'] = 'cube'
            kwargs['texture'] = 'white_cube.png'

        if not 'collider' in kwargs:
            kwargs['collider'] = 'box'
        
        super().__init__(*args, **kwargs)

    def 位置動畫(self, 座標, 延遲=0, 持續=1):
        #座標 = Vec3(座標差[0], 座標差[1], 座標差[2],) + self.position
        self.animate_position(座標, delay=延遲 ,duration=持續)

    def 旋轉動畫(self, 角度, 延遲=0, 持續=1):    
        self.animate_rotation(角度, delay=延遲 ,duration=持續)

    def 縮放動畫(self, 比例, 延遲=0, 持續=1):    
        self.animate_scale(比例, delay=延遲 ,duration=持續)

    def 顏色動畫(self, 顏色, 延遲=0, 持續=1):    
        self.animate_color(顏色, delay=延遲 ,duration=持續)

    @property
    def 模型(self):
        return self.model 

    @模型.setter
    def 模型(self, value):
        self.model = value 
        # remove previous texture
        #self._texture = None
        #self.setTextureOff(True)

    @property
    def 紋理(self):
        self.setTextureOff(True)
        return self.texture 

    @模型.setter
    def 紋理(self, value):
        self.texture = value

    @property
    def 上層物件(self):
        return self.parent

    @模型.setter
    def 上層物件(self, value):
        self.parent = value

    # enabled
    @property
    def 有效狀態(self):
        return self.enabled

    @有效狀態.setter
    def 有效狀態(self, value):
        self.enabled = value

    # color
    @property
    def 顏色(self):
        return self.color 

    @顏色.setter
    def 顏色(self, value):
        self.color = value

    # origin
    @property
    def 中心點偏移(self):
        return self.origin 

    @中心點偏移.setter
    def 中心點偏移(self, value):
        self.origin = value

    # position
    @property
    def 位置(self):
        return self.position 

    @位置.setter
    def 位置(self, value):
        self.position = value  

    @property
    def 位置x(self):
        return self.x 

    @位置x.setter
    def 位置x(self, value):
        self.x = value 

    @property
    def 位置y(self):
        return self.y 

    @位置y.setter
    def 位置y(self, value):
        self.y = value 

    @property
    def 位置z(self):
        return self.z 

    @位置z.setter
    def 位置z(self, value):
        self.z = value 

    @property
    def 全域位置(self):
        return self.world_position 

    @全域位置.setter
    def 全域位置(self, value):
        self.world_position = value 

    @property
    def 全域位置x(self):
        return self.world_x 

    @全域位置x.setter
    def 全域位置x(self, value):
        self.world_x = value 

    @property
    def 全域位置y(self):
        return self.world_y 

    @全域位置y.setter
    def 全域位置y(self, value):
        self.world_y = value 

    @property
    def 全域位置z(self):
        return self.world_z 

    @全域位置z.setter
    def 全域位置z(self, value):
        self.world_z = value 

    # rotation
    @property
    def 旋轉(self):
        return self.rotation 

    @旋轉.setter
    def 旋轉(self, value):
        self.rotation = value 

    @property
    def 旋轉x(self):
        return self.rotation_x 

    @旋轉x.setter
    def 旋轉x(self, value):
        self.rotation_x = value 

    @property
    def 旋轉y(self):
        return self.rotation_y 

    @旋轉y.setter
    def 旋轉y(self, value):
        self.rotation_y = value 

    @property
    def 旋轉z(self):
        return self.rotation_z 

    @旋轉z.setter
    def 旋轉z(self, value):
        self.rotation_z = value

    @property
    def 全域旋轉(self):
        return self.world_rotation 

    @全域旋轉.setter
    def 全域旋轉(self, value):
        self.world_rotation = value

    @property
    def 全域旋轉x(self):
        return self.world_rotation_x 

    @全域旋轉x.setter
    def 全域旋轉x(self, value):
        self.world_rotation_x = value

    @property
    def 全域旋轉y(self):
        return self.world_rotation_y 

    @全域旋轉y.setter
    def 全域旋轉y(self, value):
        self.world_rotation_y = value

    @property
    def 全域旋轉z(self):
        return self.world_rotation_z 

    @全域旋轉z.setter
    def 全域旋轉z(self, value):
        self.world_rotation_z = value

    # scale
    @property
    def 縮放(self):
        return self.scale 

    @縮放.setter
    def 縮放(self, value):
        self.scale = value 

    @property
    def 縮放x(self):
        return self.scale_x 

    @縮放x.setter
    def 縮放x(self, value):
        self.scale_x = value  

    @property
    def 縮放y(self):
        return self.scale_y 

    @縮放y.setter
    def 縮放y(self, value):
        self.scale_y = value 

    @property
    def 縮放z(self):
        return self.scale_z 

    @縮放z.setter
    def 縮放z(self, value):
        self.scale_z = value 

    @property
    def 全域縮放(self):
        return self.world_scale 

    @全域縮放.setter
    def 全域縮放(self, value):
        self.world_scale = value 

    @property
    def 全域縮放x(self):
        return self.world_scale_x 

    @全域縮放x.setter
    def 全域縮放x(self, value):
        self.world_scale_x = value 

    @property
    def 全域縮放y(self):
        return self.world_scale_y 

    @全域縮放y.setter
    def 全域縮放y(self, value):
        self.world_scale_y = value 

    @property
    def 全域縮放z(self):
        return self.world_scale_z 

    @全域縮放z.setter
    def 全域縮放z(self, value):
        self.world_scale_z = value 


    