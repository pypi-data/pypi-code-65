from swap.api.clients import UBLClient
from swap.api.models import WorkflowServiceChain, CommandInput
from swap.api.sequences.builders import DefaultCommandSequenceBuilder
from swap.common.logging import logger
from swap.api.parsers import ProgressResponseParser
from swap.api.state import ProgressStateMachine


class Workflow:
    def __init__(self):
        self.service_chain_uuid = None
        self.service_chains = {}
        self.ubl_client = UBLClient()
        self.command_sequence = DefaultCommandSequenceBuilder().build()

    def create_service_chain(self, name):
        self.service_chains[name] = WorkflowServiceChain(datasets=[], services=[])

    def submit(self, wait=False):
        output = {}
        for key, service_chain in self.service_chains.items():
            command_input = CommandInput(response=None, service_chain=service_chain, wait=wait)
            output[key] = self.command_sequence.call(command_input)
            return output if not wait else \
                logger.info(f"Workflow submit set to wait={wait}. "
                f"Execution Request sent for Service Chain UUID: {command_input.response['Execution_sent']}. "
                f"Call Workflow.status(service_chain_uuid='{command_input.response['Execution_sent']}') for status updates.")

    def service_chain(self, name):
        return self.service_chains[name]

    @staticmethod
    def status(service_chain_uuid):
        def service_chain_keys():
            url = f'/progress?service_chain_uuid={service_chain_uuid}'
            parsed_response = ProgressResponseParser().parse(UBLClient().get(url))
            return parsed_response.chain_links.keys()

        output = {}
        for key in service_chain_keys():
            state_machine = ProgressStateMachine(
                service_chain_uuid=service_chain_uuid, chain_link=key
            )
            response = state_machine.submit()
            state_machine.update(response)
            state_machine.log_current_state(response)
            output[key] = state_machine.data
        return output




