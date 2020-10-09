import json
import logging
import functools
import re
from types import FunctionType
from TDhelper.generic.classDocCfg import doc
from TDhelper.generic.dictHelper import createDictbyStr, findInDict
from TDhelper.network.http.REST_HTTP import GET, POST, PUT, DELETE, serializePostData
from TDhelper.generic.recursion import recursion, recursionCall
class register:
    def __init__(self, host, platformKey: str, secret=None, httpHeaders={}):
        self._host = host
        self._platformKey = platformKey
        self._secret = secret
        self._httpHeaders = httpHeaders

    def Register(self, serviceClass= None):
        '''
            使用方法描述进行注册
            - params:
            -   serviceClass: <class>, 类
        '''
        if not serviceClass:
            serviceClass= type(self)
        for k, v in serviceClass.__dict__.items():
            if isinstance(v, FunctionType):
                if not k.startswith("__"):
                    if not k.startswith("_"):
                        self._handleRegister(v)

    def RegisterByCfg(self,Cfg:dict):
        '''
            使用配置文件进行注册
            - params:
            -   Cfg:<dict>, 注册配置文件.
        '''
        if Cfg:
            kwargs={"params":Cfg}
            recursionCall(self._register_permission, **kwargs)

    def _handleRegister(self, v):
        k = v.__qualname__.replace('.', "_").upper()
        config = v.__doc__
        config= doc(v.__doc__,"permission")
        if config:
            config = re.sub(r'[\r|\n]', r'', config, count=0, flags=0).strip()
            try:
                config = json.loads(config, encoding='utf-8')
            except:
                config = None
            #todo register permission
            if config:
                kwargs={"params":config}
                recursionCall(self._register_permission, **kwargs)
        else:
            raise Exception("config is none.")
    
    @recursion
    def _register_permission(self,*args,**kwargs):
        if self._platformKey:
            kwargs['params']['permission_key']=self._platformKey+"."+kwargs['params']['permission_key']
        if not self._host.endswith('/'):
            self._host+='/'
        post_data= {
            "permission_name":kwargs['params']['permission_name'],
            "permission_key":kwargs['params']['permission_key'],
            "permission_domain":kwargs['params']['permission_domain'],
            "permission_uri":kwargs['params']['permission_uri'],
            "permission_enable":kwargs['params']['permission_enable'],
            "permission_parent":0 if 'permission_parent' not in kwargs['params'] else kwargs['params']['permission_parent']
        } 
        state,body= POST(uri= self._host+"permissions/", post_data= post_data, http_headers= self._httpHeaders, time_out=15)
        m_parent_id=0
        if state == 200:
            m_ret= str(body,encoding='utf-8')
            m_ret_json= json.loads(m_ret, encoding='utf-8')
            if m_ret_json['state']==200:
                m_parent_id= m_ret_json['msg']["permission_id"]
                logging.info("create permission '%s' success."%kwargs['params']['permission_name'])
            else:
                logging.info("create permission '%s' failed.error(%s)"%(kwargs['params']['permission_name'],m_ret_json['msg']))
        else:
            logging.info("create permission '%s' failed."%kwargs['params']['permission_name'])
        if 'children' not in kwargs['params']:
            kwargs['break'] = True
            return args, kwargs
        else:
            for item in kwargs['params']['children']:
                kwargs['params'] = item
                kwargs['params']['permission_parent']= m_parent_id
                return self._register_permission(*args, **kwargs)
            if not kwargs['params']['children']:
                kwargs['break'] = True
                return args, kwargs
        return args, kwargs
