from greble_flow.processors.base import BaseFlowProcessor


class SimpleProcessor(BaseFlowProcessor):
    name = "simple-flow-processor"

    def execute(self, *args, **kwargs):
        return {
            "test": 1
        }
