"""Blackout Nexus node. Base class for all personality core parts"""

# System imports
import os
import inspect
import json, base64




# 3rd Party imports
from btPostRequest import BTPostRequest

# local imports


# end file header
__author__      = "Adrian Lubitz"
__copyright__   = "Copyright (c)2017, Blackout Technologies"

class Integration(object):
    """
    This class provides all important endpoints which are needed to implement an Integration for the btNexus.
    """
    def __init__(self, connectHash=None, rcPath=None, personalityId=None):
        """
        This class provides all important endpoints which are needed to implement an Integration for the btNexus.

        :param connectHash: the connectHash - This must almost never be set! The connectHash is extracted automatically from the environment variable CONNECT_HASH or the .btnexusrc file
        :type connectHash: String
        :param rcPath: Path to your .btnexusrc file. If not set it is assumed, that it is in the working directory
        :type rcPath: String
        :param personalityId: The PersonalityId - This must almost never be set! The PersonalityId is automatically extracted from the environment variable PERSONALITY_ID (You should use it the same way while development to ensure it works in production)
        :type personalityId: String
        """
        if connectHash == None:
            if "CONNECT_HASH" in os.environ:
                connectHash = os.environ["CONNECT_HASH"]
            else:
                rcPath = rcPath if rcPath else '.btnexusrc'
                with open(rcPath) as btnexusrc:
                    connectHash = btnexusrc.read()
        
        self.connectHash = connectHash
        self.config = json.loads(base64.b64decode(self.connectHash))

        try:
            self.connectHashVersion = self.config['version']
        except KeyError:
            warnings.warn("You are using a deprecated version of the connect hash.", DeprecationWarning) #Apperently DeprecationWarnings are ignored for some reason

        self.integrationId = self.config['id']
        self.instanceURL = self.config['host']
        self.token = self.config['token']
        self.personalityId = personalityId if personalityId else os.environ["PERSONALITY_ID"]
        self.sessionToken = None
        
        # self.packagePath = packagePath if packagePath else os.path.join(os.path.dirname(os.path.realpath(os.path.abspath(inspect.getfile(self.__class__)))), 'package.json')

        # with open(self.packagePath) as jsonFile:
        #     self.package = json.load(jsonFile)



        # self.version = self.package['version']

    def _setSessionToken(self, response):
        """
        Helper method to set the sessionToken.
        """
        self.sessionToken = response['sessionToken']
        if self.sessionCallback:
            self.sessionCallback(response)
    
    def authenticateSession(self, callback=None, errBack=None, callbackArgs=None, **kwargs):
        """
        authenticate the session for calls to chat. 
        This should be called everytime a new session starts. 
        If not called explicitly it will be called by chat.

        
        :param callback: the callback which handles the response
        :type callback: function pointer
        :param errBack: callback to handle errors that prevent that the response can be handled by the callback. takes one argument which is the exception - This is needed for the threaded send() otherwise exceptions can't be handled
        :type errBack: function pointer
        """
        self.sessionCallback = callback
        BTPostRequest(
            'sessionAccessRequest', 
            {
                'integrationId': self.integrationId,
                'personalityId': self.personalityId
            }, 
            accessToken=self.token,
            url=self.instanceURL, 
            callback=self._setSessionToken, 
            errBack=errBack, 
            callbackArgs=callbackArgs
        ).send(blocking=True, **kwargs)

    def chat(self, text, language, actionSource=None, callback=None, errBack=None, callbackArgs=None, **kwargs):
        """
        Call to the chat endpoint.

        :param text: the text request to the Personality
        :type text: String       
        :param language: the language for the request in  ISO 3166-1 alpha-2 (Example: 'en-US' or 'de-DE')
        :type language: String
        :param actionSource: Source for the action(used for buttons)
        :type actionSource: String
        :param callback: the callback which handles the response
        :type callback: function pointer
        :param errBack: callback to handle errors that prevent that the response can be handled by the callback. takes one argument which is the exception - This is needed for the threaded send() otherwise exceptions can't be handled
        :type errBack: function pointer
        """
        if not self.sessionToken:
            self.authenticateSession()
        BTPostRequest(
            'chat', 
            {
                'sessionToken': self.sessionToken,
                'text': text,
                'language': language,
                'actionSource': actionSource

            }, 
            accessToken=self.token,
            url=self.instanceURL, 
            callback=callback, 
            errBack=errBack, 
            callbackArgs=callbackArgs
        ).send(**kwargs)
        

    def getPersonalityProfile(self, language, callback=None, errBack=None, callbackArgs=None, **kwargs):
        """
        Call to the personalityProfile endpoint.
     
        :param language: the language for the request in  ISO 3166-1 alpha-2 (Example: 'en-US' or 'de-DE')
        :type language: String
        :param callback: the callback which handles the response
        :type callback: function pointer
        :param errBack: callback to handle errors that prevent that the response can be handled by the callback. takes one argument which is the exception - This is needed for the threaded send() otherwise exceptions can't be handled
        :type errBack: function pointer
        """
        BTPostRequest(
            'personalityProfile', 
            {
                'personalityId': self.personalityId,
                'language': language

            }, 
            accessToken=self.token,
            url=self.instanceURL, 
            callback=callback, 
            errBack=errBack, 
            callbackArgs=callbackArgs
        ).send(**kwargs)




if __name__ == "__main__":
    api = Integration(personalityId='dc006af4-6cdf-0f50-8c14-1250496f3656')
    # api.authenticateSession(print)
    # print("SessionToken: {}".format(api.sessionToken))
    api.chat('Hi', 'en-US', callback=print, callbackArgs=["APPENDED THIS"])
    api.getPersonalityProfile('en-US', print)
