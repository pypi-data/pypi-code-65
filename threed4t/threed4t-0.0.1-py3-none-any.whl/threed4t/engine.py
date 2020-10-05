from inspect import signature

from ursina import *

from . import common
from .repl_panda import Repl
from .entity4t import Entity4t
from .assist import CorAssist

import __main__

class Engine3D(Ursina, Repl):
    __single = None
    __first_time = True

    def __new__(clz, *args, **kwargs):
        # Singleton
        if not Engine3D.__single:
            Engine3D.__single = object.__new__(clz)
        else:
            print("模擬3D舞台已存在")

        return Engine3D.__single

    def __init__(self, *args, **kwargs):
        # check module level default physics engine
        if Engine3D.__first_time:
            self.do_init(*args, **kwargs)
            Engine3D.__first_time = False


        

    def do_init(self, 寬=common.WIN_WIDTH, 
                       高=common.WIN_HEIGHT, 
                       title=common.TITLE):  

        common.stage = self
        common.舞台 = self        
        common.is_engine_created = True
        __main__.stage = self
        __main__.舞台 = self

        #ursina 
        self.window = window


        if common.WIN_MIN_WIDTH < 寬 < common.WIN_MAX_WIDTH:
            self.win_width = round(寬,0)
        elif 寬 < common.WIN_MIN_WIDTH :
            self.win_width = common.WIN_MIN_WIDTH
        elif 寬 > common.WIN_MAX_WIDTH :
            self.win_width = common.WIN_MAX_WIDTH

        if common.WIN_MIN_HEIGHT < 高 < common.WIN_MAX_HEIGHT:
            self.win_height = round(高,0)
        elif 高 < common.WIN_MIN_HEIGHT :
            self.win_height = common.WIN_MIN_HEIGHT
        elif 高 > common.WIN_MAX_HEIGHT :
            self.win_height = common.WIN_MAX_HEIGHT        


        Ursina.__init__(self)

        self.window.windowed_size = Vec2(self.win_width,self.win_height)
        self.window.title = title
        self.window.borderless = False
        self.window.fullscreen = False
        self.window.fps_counter.enabled = False
        self.window.exit_button.visible = False
        self.window.cog_button.enabled = False
        
        self.window.position = (50, 50)

        print(f"建立舞台(寬{self.win_width}x高{self.win_height})")

        #cor assist
        self.cor_assist = CorAssist()

        #editor camera
        self.editor_camera = EditorCamera()

        # custom event handler
        self.user_update_handler = None 
        self.user_key_press_handler = None
        self.user_key_release_handler = None
        #self.user_key_hold_handler = None


    def input_up(self, key):
        if self.user_key_release_handler:
            if key in self._input_name_changes:
                k = self._input_name_changes[key]
                self.user_key_release_handler(k)
            else:
                self.user_key_release_handler(key)
        Ursina.input_up(self, key)

    # def input_hold(self, key):
    #     if self.user_key_hold_handler:
    #         self.user_key_hold_handler(key)

    #     Ursina.input_hold(self, key)

    def _update(self, task):
        if self.user_update_handler:
            dt = globalClock.getDt() * application.time_scale
            self.user_update_handler(dt)
        
        return Ursina._update(self, task)

    def input(self, key):
        if key == 'control':
            self.cor_assist.enabled = not self.cor_assist.enabled

        if self.user_key_press_handler :
            #print('do key press')
            if key in self._input_name_changes:
                k = self._input_name_changes[key]
                self.user_key_press_handler(k)
            else:
                self.user_key_press_handler(key)

        #print('my input:', key)
        Ursina.input(self, key)




    def collect_user_event_handlers(self):
        if hasattr(__main__, '當按下時'):
            # check number of parameters
            sig = signature(__main__.當按下時)
            if len(sig.parameters) == 1:
                 
                self.user_key_press_handler = __main__.當按下時
                print( '登錄事件函式：當按下時' )
            else:
                print('事件函式錯誤: 當按下時 需要1個參數')
                sys.exit()

        if hasattr(__main__, '當放開時'):
            # check number of parameters
            sig = signature(__main__.當放開時)
            if len(sig.parameters) == 1:
                 
                self.user_key_release_handler = __main__.當放開時
                print( '登錄事件函式：當放開時' )
            else:
                print('事件函式錯誤: 當放開時 需要1個參數')
                sys.exit()


        if hasattr(__main__, '當更新時'):
            # check number of parameters
            sig = signature(__main__.當更新時)
            if len(sig.parameters) == 1:
                  
                self.user_update_handler = __main__.當更新時
                print( '登錄事件函式：當更新時' )
            else:
                print('事件函式錯誤: 當更新時 需要1個參數')
                sys.exit()

    # def input_up(self, key):
    #     print('my input up:', key)
    #     Ursina.input_up(self, key)

    # def input_hold(self, key):
    #     print('my input hold:', key)
    #     Ursina.input_hold(self, key)

    def simulate(self):
        
        #self.lazy_setup()
        self.collect_user_event_handlers()
        self.start_repl()

        

        # try cursor
        #cur = self.get_system_mouse_cursor('crosshair')
        #cur = self.get_system_mouse_cursor('help')
        # set cursor to default
        #cur = self.get_system_mouse_cursor('help')
        #self.set_mouse_cursor(None)

        self.is_engine_running = True

        
        ShowBase.run(self)    

    def add_entity(self, *args, **kwargs):
        
        e = Entity4t(*args, **kwargs)
        return e


    ### property
    # @property
    # def 全螢幕(self):
    #     return self.window.fullscreen 

    # @全螢幕.setter
    # def 全螢幕(self, value):
    #     if value:
    #         self.window.fullscreen = True
    #     else:
    #         self.window.fullscreen = False 


