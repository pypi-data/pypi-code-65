from ..common import *


class TD_COAP_CORE_15(CoAPTestCase):
    """

testcase_id : TD_COAP_CORE_15
uri : http://doc.f-interop.eu/tests/TD_COAP_CORE_15
objective: Perform GET transaction (CON mode, piggybacked response) in a lossy context
configuration: COAP_CFG_02
references: "[COAP] 4.4.1, 5.2.1, 5.8.1"
pre_conditions:
  - Gateway is introduced and configured to produce packet losses
  - Server offers a /test resource with resource content is not empty that can handle GET
notes: We acknowledge the efforts made by ETSI CTI and ProbeIT who have contributed to the content of this document
sequence:

  - step_id : TD_COAP_CORE_15_step_01
    type : stimuli
    node : coap_client
    description:
      - "Client is requested to send a confirmable GET request to server's resource"

  - step_id : TD_COAP_CORE_15_step_02
    type : check
    description:
      - 'Sent request must contain:'
      - - Type=0
        - Code=1
        - Client-generated Message ID (* CMID)
        - Client-generated Token (* CTOK)

  - step_id : TD_COAP_CORE_15_step_03
    type : check
    description:
      - 'Server sends response containing'
      - - Code=2.05(Content)
        - Message ID = CMID, Token = CTOK
        - Content-format option
        - Non-empty Payload

  - step_id : TD_COAP_CORE_15_step_04
    type : verify
    node : coap_client
    description:
      - 'Client displays the response'

  - step_id : TD_COAP_CORE_15_step_05
    type : check
    description:
      - 'Repeat steps 1-4 until at least one of the following actions has been observed'
      - - 'One dropped request'
        - 'One dropped response'


  - step_id : TD_COAP_CORE_15_step_06
    type : verify
    node : coap_client
    description:
      - 'For each case mentioned in step 5:'
      - 'Observe that retransmission is launched'
    """

    @classmethod
    @typecheck
    def get_stimulis(cls) -> list_of(Value):
        """
        Get the stimulis of this test case. This has to be be implemented into
        each test cases class.

        :return: The stimulis of this TC
        :rtype: [Value]
        """
        return [CoAP(type='con', code='get', opt=Opt(CoAPOptionUriPath("test")))]

    def run(self):
        self.match('client', CoAP(type='con', code='get', opt=self.uri('/test')))
        self.next(skip_retransmissions=True)
        CMID = self.coap['mid']
        CTOK = self.coap['tok']

        self.next()

        self.match('server', template=CoAP(code=2.05, mid=CMID, tok=CTOK))
        if self.match('server',
                   template=CoAP(pl=Not(b'')),
                   on_mismatch_verdict='inconclusive',
                   on_mismatch_msg = 'Test pre-conditions not met by server. Payload should not be empty'
                   ):
            self.match('server', CoAP(opt=Opt(CoAPOptionContentFormat())), 'fail')
