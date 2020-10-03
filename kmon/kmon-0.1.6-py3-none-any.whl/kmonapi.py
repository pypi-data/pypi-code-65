import requests
import numpy as np
import json

class KmonAPI:
    backend_addr = None
    token = None
    headers = None
    __is_valid_token = False

    def __init__(self,url):
        try:
            self.backend_addr = url
            if self.backend_addr[len(self.backend_addr)-1] == '/':
                self.backend_addr = self.backend_addr[:-1]
            self.__req('/api/verifyToken','POST')
        except Exception:
            raise

    def set_token(self,token):
        try:
            self.token = token
            self.headers = {'Authorization': 'Bearer ' + token}
            res = self.__req('/api/verifyToken','POST')
            if res != None and res.status_code != 200: raise KmonException(INVALID_HTTP_REQUEST)
            # data = res.json()
            # if data.code != codedef.SUCCESS: raise KmonException(res.code,res.message,res.data)
            self.__is_valid_token = True; 
            return True
        except KmonException:
            raise            
        except Exception:
            raise

    def job_state(self,key):
        try:
            if self.__is_valid_token == False: raise KmonException(NOT_SET_TOKEN)
            data = { "key" : key}            
            res = self.__req('/api/job/state','POST',data)
            if res != None and res.status_code != 200: raise KmonException(INVALID_HTTP_REQUEST)
            data = res.json()
            if data['code'] != SUCCESS.code: raise KmonException(data['code'],data['message'],data['data'])
            return data['data']
        except KmonException:
            raise
        except Exception:
            raise

    def job_init(self,type,params,space=''):
        try:
            if self.__is_valid_token == False: raise KmonException(NOT_SET_TOKEN)
            params = self.__np2dict(params)
            data = { "type" : type, "params" : params, "space" : space , "token" : self.token}            
            res = self.__req('/api/job/init','POST',data)
            if res != None and res.status_code != 200: raise KmonException(INVALID_HTTP_REQUEST)
            data = res.json()
            if data['code'] != SUCCESS.code: raise KmonException(data['code'],data['message'],data['data'])
            return data['data']['key']
        except KmonException:
            raise
        except Exception:
            raise

    def job_next(self,key):
        try:
            if self.__is_valid_token == False: raise KmonException(NOT_SET_TOKEN)
            data = { "key" : key}
            res = self.__req('/api/job/next','POST',data)
            if res != None and res.status_code != 200: raise KmonException(INVALID_HTTP_REQUEST)
            data = res.json()
            if data['code'] != SUCCESS.code: raise KmonException(data['code'],data['message'],data['data'])
            return self.__dict2np(data['data']['output']['rho'])
        except KmonException :
            raise
        except Exception:
            raise

    def job_feedback(self,key,rho,obs):
        try:
            if self.__is_valid_token == False: raise KmonException(NOT_SET_TOKEN)
            rho = self.__np2dict(rho)
            obs = self.__np2dict(obs)
            data = { "key" : key, 'rho' : rho, 'obs' : obs}
            res = self.__req('/api/job/feedback','POST',data)
            if res != None and res.status_code != 200: raise KmonException(INVALID_HTTP_REQUEST)
            data = res.json()
            if data['code'] != SUCCESS.code: raise KmonException(data['code'],data['message'],data['data'])
            return data['data']['output']['feedback']
        except KmonException:
            raise
        except Exception:
            raise
    
    def __req(self,path, method, data={}):
        url = self.backend_addr + path
            
        if method == 'GET':
            return requests.get(url, headers=self.headers)
        else:
            return requests.post(url, headers=self.headers, json=data)

    def __np2dict(self,obj):
        if isinstance(obj, np.ndarray): return obj.tolist()
        elif isinstance(obj, dict): 
            for key, val in obj.items():
                try: json.dumps(val)
                except: obj[key] = self.__np2dict(val)
            return obj
        else : return obj

    def __dict2np(self,obj):
        if isinstance(obj, list): return np.array(obj)
        elif isinstance(obj, dict): 
            for key, val in obj.items():
                obj[key] = self.__dict2np(val)
            return obj
        else : return obj

class KmonCode:
    code = None
    message = None
    def __init__(self,code,message): self.code = code ; self.message = message

class KmonException(Exception):
    def __init__(self,code , message=None, data=None): 
        self.code = code
        self.data = data
        self.message = message
        super().__init__(self.message)    

SUCCESS = KmonCode(0,'success')

# Token errors
INVALID_TOKEN = KmonCode(100,'token is expired') # 토큰 유효기간이 만료
NOT_SET_TOKEN = KmonCode(101,'the token is not registered') # 토큰값이 등록되지 않음 (애초에 생성된 적 없는 토큰)

# Job Init errors
JOB_INIT_ERROR = KmonCode(200,'init function got problem') # init 수행하다 문제가 생겼음 (함수 자체 에러)
JOB_TYPE_ERROR = KmonCode(201,'invalid job type') # Init시 job type 인자값 (함수명)이 존재하지 않을 때
NOT_EXIST_JOB_RUNNER = KmonCode(202,'Job runner does not exist') # Job을 실행하기 위한 Job Runner가 없는 경우 (Timout 시간이 지나 Job Runner 가 삭제된 경우)
NOT_EXIST_WORKER = KmonCode(203,'Worker Node does not exist') # job key로 부터 Job을 가진 Worker Node 가 존재하지 않을때 
INVALID_WORKER_FUNCTION = KmonCode(204,'worker does not have next or feedback function') # Worker 코드가 정해진 규칙 (next, feedback함수)를 포함하지 않은 경우

# Job Next errors
JOB_NEXT_ERROR = KmonCode(300,'next function got problem') # next 수행하다 문제가 생겼음 (함수 자체 에러)
INVALID_KEY = KmonCode(301,'invalid job key') # 인자값인 키값이 잘못된 경우 

# Job Feedback errors
JOB_FEEDBACK_ERROR = KmonCode(400,'feedback function got problem') # feedback 수행하다 문제가 생겼음 (함수 자체 에러)
HAVENT_DONE_NEXT = KmonCode(401,'throw feedback, there is no "rho" value because next hasn"t executed before') # Feedback을 던졌는데 next를 수행한 적이 없어 rho인자값이 없을 때

# Common errors
NOT_PROPER_PARAMS = KmonCode(500,'parameter value is not proper (maybe data type error or too many or less argument)') # parameter값이 적절치 않음 (자료형 type에러, 예상하는 인자갯수보다 적거나 많을때)
CONNECTION_ERROR = KmonCode(600,'network problem due to the server black out or network error') # 서버가 꺼지는등의 이유로 인해 연결이 끊어지는 경우
INVALID_HTTP_REQUEST = KmonCode(700,'http request is not available due to rest api server error') # HTTP요청이 가능하지 않음 (rest api 서버 에러)
UNDEFINED_ERROR = KmonCode(999,'undefined error')
