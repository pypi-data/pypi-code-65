from ..common import *


class TD_M2M_NH_01(OneM2MTestCase):
    """
    testcase_id: TD_M2M_NH_01
    configuration: M2M_CFG_01
    objective: AE retrieves the CSEBase resource
    pre_conditions: CSEBase resource has been automatically created in CSE
    references: oneM2M TS-0001 [1], clause 10.2.3.2, oneM2M TS-0004 [2], clause 7.3.2
    sequence:
    -   description: AE is requested to send a retrieve Request to CSE with name {CSEBaseName}
        node: adn
        step_id: step_1
        type: stimuli
    -   description: Operation (op) = 2 (Retrieve), To (to) = Resource-ID of requested
            <CSEBase> resource, assumed CSE-relative here , From (from) = AE-ID of request
            originator, Request Identifier (rqi) = (token-string)
        node: null
        step_id: step_2
        type: check
    -   description: Response Status Code (rsc) = 2000 (OK), Request Identifier (rqi)
            = same string as received in request message, Content (pc) = Serialized Representation
            of <CSEBase> resource
        node: null
        step_id: step_3
        type: check
    -   description: AE indicates successful operation
        node: adn
        step_id: step_4
        type: verify


    """

    @classmethod
    @typecheck
    def get_stimulis(cls) -> list_of(Value):
        """ A sort of pattern exchanges of stimulis for testcase.
        Necessary when the implementations have exchanged more than the minimal amount of frames for test case.
        """
        return []

    def run(self):
        #self.match(None, OneM2MRequest(op='Retrieve', to=Not(''), fr=Not(''), rqi=Not('')), 'fail')
        self.match(None, OneM2MRequest(op='Retrieve',  fr=AnyValue(str), rqi=AnyValue(str)), 'fail')
        REQ_RQI = self.onem2m['rqi']
        self.next()
        #to = AnyValue(str),

        self.match(None, OneM2MResponse(rsc=2000) , 'fail')
        self.match(None, OneM2MResponse(fr = AnyValue(str) ), 'fail')
        print(dir(self))
        self.match(None, OneM2MResponse( rqi = REQ_RQI), 'fail')


        #to=Not(''),
        # fr=Not(''),
        # self.match('client', CoAP(opt=Opt(CoAPOptionOneM2MFrom())), 'fail')
        # if self.match('client', CoAP(opt=Opt(CoAPOptionOneM2MRequestIdentifier())), 'fail'):
        #     CMID = self.coap['mid']
        #     CTOK = self.coap['tok']
        #     OPTS = self.coap['opt']
        #     RI = OPTS[CoAPOptionOneM2MRequestIdentifier]
        #     RIVAL = RI[2]
        #
        #     self.next()
        #
        #     self.match('server', CoAP(code=2.05, mid=CMID, tok=CTOK, pl=Not(b'')), 'fail')
        #     self.match('server', CoAP(opt=Opt(CoAPOptionContentFormat())), 'fail')
        #     self.match('server', CoAP(opt=Opt(CoAPOptionOneM2MResponseStatusCode('2000'))), 'fail')
        #     self.match('server', CoAP(opt=Opt(CoAPOptionOneM2MRequestIdentifier(RIVAL))), 'fail')
