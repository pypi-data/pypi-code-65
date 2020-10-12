from typing import Optional, Dict, Union
from .validators import CloudQueueWorkerValidator
from .orchestrator import Orchestrator
from .logging import logger


class CloudQueueWorker:
    def __init__(
        self,
        queue_mapping: Optional[Dict[str, str]] = None,
        concurrency: Optional[int] = None,
        cloud_provider_config: Optional[Dict[str, str]] = None,
    ) -> None:
        self.queue_mapping = queue_mapping
        self.concurrency = concurrency
        self.cloud_provider_config = cloud_provider_config

    def update_config(self, config: Dict[str, Union[str, int]]) -> None:
        """
        Update CloudQueueWorker object after initialization using a dict.
        :param config: dict to use to update CloudQueueWorker object
        :type config: dict
        :return: None
        """
        for key, value in config.items():
            setattr(self, key, value)

    def run(self) -> None:
        """
        Method to start CloudQueueWorker
        :return: None
        """
        logger.info("Start cloud queue worker")

        cloud_queue_worker_validator = CloudQueueWorkerValidator().load(self.__dict__)
        orchestrator = Orchestrator(**CloudQueueWorkerValidator().dump(cloud_queue_worker_validator))
        orchestrator.run()
