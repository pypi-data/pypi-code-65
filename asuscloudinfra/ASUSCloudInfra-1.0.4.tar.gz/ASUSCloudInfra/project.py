import requests
import jwt
class Project():
    def __init__(self, baseURL, apiToken, port=31382):
        self._baseURL = "http://" + baseURL + ":" + str(port)  
        self._APIToken = apiToken
        projectData = jwt.decode(apiToken, verify=False)
        self._projectId = projectData['id']
        self._headers = {
            "authorization": "Bearer " + apiToken,
            "Content-Type": "application/json"
        }

    def getProjectId(self):
        return self._projectId
        
    def get(self, action):
        url = self._baseURL + action
        resp = requests.get(url, headers=self._headers)
        print("action:get " + "url:" + url + " resp:" + str(resp))
        return resp.json()

    def post(self, action, body):
        url = self._baseURL + action
        resp = requests.post(url, json=body, headers=self._headers)
        print("action:post " + "url:" + url + " resp:" + str(resp))
        return resp.json()

    def patch(self, action, body):
        url = self._baseURL + action
        resp = requests.patch(url, json=body, headers=self._headers)
        print("action:patch " + "url:" + url + " resp:" + str(resp))
        return resp.json()

    def delete(self, action):
        url = self._baseURL + action
        resp = requests.delete(url, headers=self._headers)
        print("action:delete " + "url:" + url + " resp:" + str(resp))
        return resp.json()
