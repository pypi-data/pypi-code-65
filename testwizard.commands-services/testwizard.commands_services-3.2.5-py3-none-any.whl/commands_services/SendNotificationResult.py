import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class SendNotificationResult(ResultBase):
    def __init__(self, result , successMessage, failMessage):
        self.message = self.getMessageForErrorCode(self.message, result["errorCode"])

        ResultBase.__init__(self, result.ok, successMessage, failMessage)
