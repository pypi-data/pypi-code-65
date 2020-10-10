from abc import ABC


class S3Manager(ABC):

    def get_file_meta_data(self):
        pass

    def copy_file_source_to_destination(self, destination):
        pass
