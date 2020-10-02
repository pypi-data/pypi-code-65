from ..common import *


class TD_M2M_EXAMPLES(OneM2MTestCase):

    @classmethod
    @typecheck
    def get_nodes_identification_templates(cls) -> list_of(Node):
        """
        Get the nodes of this test case. This has to be be implemented into
        each test cases class.

        :return: The nodes of this TC
        :rtype: [Node]

        """
        return [
            # Node('1', OneM2MRequest()),
            # Node('2', OneM2MResponse())
        ]

    @classmethod
    @typecheck
    def get_stimulis(cls) -> list_of(Value):
        """
        Get the stimulis of this test case. This has to be be implemented into
        each test cases class.

        :return: The stimulis of this TC
        :rtype: [Value]
        """
        return [] #[OneM2MRequest()]

    def run(self):
        import logging
        #self.log('test logger')
        #self.log(self)
        #self.log(self.http)
        #self.log(self.onem2m)
        from ttproto.core.lib.inet.onem2m import Operation

        self.match(None, OneM2MRequest())
        self.match(None, OneM2MRequest(op=Operation.RETRIEVE))

        # self.match('client', CoAP(type='con', code='get'), 'fail')
        # self.match('client', CoAP(opt=Opt(CoAPOptionOneM2MFrom())), 'fail')
        # if self.match('client', CoAP(opt=Opt(CoAPOptionOneM2MRequestIdentifier())), 'fail'):
        #     CMID = self.coap['mid']
        #     CTOK = self.coap['tok']
