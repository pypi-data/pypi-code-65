from typing import Optional, Dict

import boto3

from b_cf_outputs.cf_stacks import CfStacks


class CfOutputs:
    """
    Class that is responsible for working with Cloud Formation stack outputs.
    """
    def __init__(self, boto_session: boto3.session.Session) -> None:
        """
        Constructor.

        :param boto_session: AWS SDK session instance.
        """
        self.boto_session = boto_session
        self.client = self.boto_session.client('cloudformation')

    def get_outputs(self, stack_name: Optional[str] = None) -> Dict[str, Dict[str, str]]:
        """
        Gets Cloud Formation stack outputs for all stacks or a specific stack.

        :param stack_name: A stack name for which to get its outputs.

        :return: A dictionary of outputs.
        """
        all_outputs = {}

        if not stack_name:
            stack_names = list(CfStacks(self.boto_session).get_stacks())
        else:
            stack_names = [stack_name]

        for stack in stack_names:
            response = self.client.describe_stacks(StackName=stack)
            response = response['Stacks'][0].get('Outputs', [])
            stack_outputs = {out['OutputKey'] or out['ExportName']: out['OutputValue'] for out in response}
            all_outputs[stack] = stack_outputs

        return all_outputs
