# __init__.py
__version__ = "0.0.1"
import logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
import time
import csv
import json
import jwt
import requests
import urllib.parse
from pprint import pprint

class DFA():
    class Decorators():
        @staticmethod
        def refreshToken(decorated):
            def wrapper(api,*args,**kwargs):
                if api.access_token != None:
                    if time.time() - api.access_token_expiration + 500 > 0:
                        api.requestAccessToken()
                    return decorated(api,*args,**kwargs)
            return wrapper

    def __init__(self, server_id=None, client_id=None, client_secret=None,*,isQA=False):
        if not isinstance(server_id, str) or not isinstance(client_id, str) or not isinstance(client_secret, str):
            raise TypeError("Invalid API credentials")
        self.isQA = isQA
        self.server_id = server_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_calls = 0
        self.access_token = None
        self.access_token_expiration = None
        self.__start_time = time.time()
        self.session = requests.Session()
        self.session.headers.update({ 'Content-Type': 'application/json' })
        try:
            self.requestAccessToken()
            self.host = "https://qa-dataflownode.zerionsoftware.com/zcrypt/v1.0/" if self.isQA else "https://dataflownode.zerionsoftware.com/zcrypt/v1.0/"
        except Exception as e:
            print(e)
            return

    @Decorators.refreshToken
    def __get(self, resource):
        try:
            result = self.session.get(self.host+resource)
            self.api_calls += 1
            if result.status_code >= 300:
                result.raise_for_status()
        except Exception as e:
            print(f"<{result.status_code}> {e}, {result.json()['error_message']}")
        finally:
            return result.json()
    
    @Decorators.refreshToken
    def __post(self,resource,body):
        try:
            result = self.session.post(self.host+resource,data=body)
            self.api_calls += 1
            if result.status_code >= 300:
                result.raise_for_status()
        except Exception as e:
            print(f"<{result.status_code}> {e}, {result.json()['error_message']}")
        finally:
            return result.json()
    
    @Decorators.refreshToken
    def __put(self,resource,body):
        try:
            result = self.session.put(self.host+resource,data=body) if body else self.session.put(self.host+resource)
            self.api_calls += 1
            if result.status_code >= 300:
                result.raise_for_status()
        except Exception as e:
            print(f"<{result.status_code}> {e}, {result.json()['error_message']}")
        finally:
            return result.json()
    
    @Decorators.refreshToken
    def __delete(self,resource):
        try:
            result = self.session.delete(self.host+resource)
            self.api_calls += 1
            if result.status_code >= 300:
                result.raise_for_status()
        except Exception as e:
            print(f"<{result.status_code}> {e}, {result.json()['error_message']}")
        finally:
            return result.json()
    ####################################
    ## TOKEN RESOURCES
    ####################################
    def requestAccessToken(self):
        """Create JWT and request iFormBuilder Access Token
        If token is successfully returned, stored in session header
        Else null token is stored in session header
        """
        try:
            url = "https://qa-identity.zerionsoftware.com/oauth2/token" if self.isQA else "https://identity.zerionsoftware.com/oauth2/token"
            
            jwt_payload = {
                'iss': self.client_id,
                'aud': url,
                'iat': time.time(),
                'exp': time.time() + 300
            }

            encoded_jwt = jwt.encode(jwt_payload,self.client_secret,algorithm='HS256')
            token_body = {
                'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'assertion': encoded_jwt 
            }

            result = requests.post(url, data=token_body, timeout=5)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            self.access_token = result.json()['access_token']
            self.session.headers.update({ 'Authorization': "Bearer %s" % self.access_token })
            self.access_token_expiration = time.time() + 3300

    ####################################
    ## DATAFLOW RESOURCES
    ####################################
    def readDataflows(self):
        request = "dataflows"
        return self.__get(request)

    def readDataflow(self, dataflow_id):
        request = f"dataflows/{dataflow_id}"
        return self.__get(request)
    
    def createDataflow(self,body):
        request = "dataflows"
        return self.__post(request,json.dumps(body))
    
    def updateDataflow(self,dataflow_id,body):
        request = f"dataflows/{dataflow_id}"
        return self.__put(request,json.dumps(body))
    
    def deleteDataflow(self,dataflow_id):
        request = f"dataflows/{dataflow_id}"
        return self.__delete(request)
    
    ####################################
    ## RECORDSET RESOURCES
    ####################################
    def readRecordset(self, dataflow_id, recordset_id):
        request = f"dataflows/{dataflow_id}/recordsets/{recordset_id}"
        return self.__get(request)

    def readRecordsets(self, dataflow_id):
        request = f"dataflows/{dataflow_id}/recordsets"
        return self.__get(request)
    
    def createRecordset(self,dataflow_id,body):
        request = f"dataflows/{dataflow_id}/recordsets"
        return self.__post(request,json.dumps(body))
    
    def updateRecordset(self,dataflow_id,recordset_id,body):
        request = f"dataflows/{dataflow_id}/recordsets/{recordset_id}"
        return self.__put(request,json.dumps(body))
    
    def deleteRecordset(self,dataflow_id,recordset_id):
        request = f"dataflows/{dataflow_id}/recordsets/{recordset_id}"
        return self.__delete(request)
    
    def linkRecordset(self,dataflow_id,source_recordset_id,destination_recordset_id):
        request = f"dataflows/{dataflow_id}/recordsets/{source_recordset_id}/postactions"
        return self.__post(request,{"actionType": "pushrs", "actionOutputRecordSetId": destination_recordset_id})

    def rerunRecords(self,dataflow_id,recordset_id,action_id="all",run_id="All"):
        request = f"dataflows/{dataflow_id}/recordsets/{recordset_id}/postactions/{action_id}/rerun/{run_id}"
        return self.__post(request,{"dataflowId": dataflow_id, "recordSetId": recordset_id, "actionId": action_id, "rerunData": run_id})
    
    ####################################
    ## DATA REFINERY RESOURCES
    ####################################
    def readDataRefinery(self,dataflow_id,recordset_id):
        request = f"dataflows/{dataflow_id}/recordsets/{recordset_id}/datarefinery"
        return self.__get(request)
    
    def createDataRefinery(self,dataflow_id,recordset_id,body):
        request = f"dataflows/{dataflow_id}/recordsets/{recordset_id}/datarefinery"
        return self.__post(request,json.dumps(body))
    
    def updateDataRefinery(self,dataflow_id,recordset_id,datarefinery_id,body):
        request = f"dataflows/{dataflow_id}/recordsets/{recordset_id}/datarefinery/{datarefinery_id}"
        return self.__put(request,json.dumps(body))
    
    def deleteDataRefinery(self,dataflow_id,recordset_id,datarefinery_id):
        request = f"dataflows/{dataflow_id}/recordsetes/{recordset_id}/datarefinery/{datarefinery_id}"
        return self.__delete(request)
    
    ####################################
    ## WEBHOOK RESOURCES
    ####################################
    def readWebhook(self,dataflow_id,recordset_id,webhook_id):
        request = f"dataflows/{dataflow_id}/recordsets/{recordset_id}/webhooks/{webhook_id}"
        return self.__get(request)
    
    def createWebhook(self,dataflow_id,recordset_id,body):
        request = f"dataflows/{dataflow_id}/recordsets/{recordset_id}/webhooks"
        return self.__post(request,json.dumps(body))
    
    def updateWebhook(self,dataflow_id,recordset_id,webhook_id,body):
        request = f"dataflows/{dataflow_id}/recordsets/{recordset_id}/webhooks/{webhook_id}"
        return self.__put(request,json.dumps(body))
    
    def deleteWebhook(self,dataflow_id,recordset_id,webhook_id):
        request = f"dataflows/{dataflow_id}/recordsets/{recordset_id}/webhooks/{webhook_id}"
        return self.__delete(request)
    
    ####################################
    ## ACTION RESOURCES
    ####################################
    def readAction(self,dataflow_id,recordset_id,action_id):
        request = f"dataflows/{dataflow_id}/recordsets/{recordset_id}/postactions/{action_id}"
        return self.__get(request)

    def readActions(self,dataflow_id,recordset_id):
        request = f"dataflows/{dataflow_id}/recordsets/{recordset_id}/postactions"
        return self.__get(request)
    
    def createAction(self,dataflow_id,recordset_id,body):
        request = f"dataflows/{dataflow_id}/recordsets/{recordset_id}/postactions"
        return self.__post(request,json.dumps(body))

    def updateAction(self,dataflow_id,recordset_id,action_id,body):
        request = f"dataflows/{dataflow_id}/recordsets/{recordset_id}/postactions/{action_id}"
        return self.__post(request,json.dumps(body))

    def deleteAction(self,dataflow_id,recordset_id,action_id):
        request = f"dataflows/{dataflow_id}/recordsets/{recordset_id}/postactions/{action_id}"
        return self.__delete(request)

    def readActionErrorMessageCount(self, dataflow_id, recordset_id, action_id):
        request = f"dataflows/{dataflow_id}/recordsets/{recordset_id}/postactions/{action_id}/errors/count"
        return self.__get(request)

    def readActionErrorMessages(self, dataflow_id, recordset_id, action_id, offset=0, limit=1000, fields=""):
        request = f"dataflows/{dataflow_id}/recordsets/{recordset_id}/postactions/{action_id}/errors/offset/{offset}/limit/{limit}?fields={fields}"
        return self.__get(request)

    ####################################
    ## GENERIC NODE RESOURCES
    ####################################
    def deactivateNode(self, dataflow_id, node_id):
        request = f"https://dataflownode.zerionsoftware.com/zcrypt/v1.0/dataflows/{dataflow_id}/inactiveNode/nodeId/{node_id}/status/-1"
        return self.__put(request,{})

    def reactivateNode(self, dataflow_id, node_id):
        request = f"https://dataflownode.zerionsoftware.com/zcrypt/v1.0/dataflows/{dataflow_id}/inactiveNode/nodeId/{node_id}/status/1"
        return self.__put(request,{})