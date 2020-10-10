from abc import ABC


class ProcessInventory(ABC):

    def get_ingestion_date(self):
        pass

    def get_participant_id(self):
        pass
