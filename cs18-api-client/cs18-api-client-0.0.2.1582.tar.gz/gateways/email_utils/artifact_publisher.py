import os
import shutil


class ArtifactPublisher:
    ARTIFACTS_FOLDER_PATH = "/tmp/artifact"
    current_test_path = ""

    @staticmethod
    def init_artifact_folder(test_method_name):
        ArtifactPublisher._create_artifact_folder(test_method_name)

    @staticmethod
    def _delete_artifact_folder(only_current_test: bool = False):
        folder_path = ArtifactPublisher.ARTIFACTS_FOLDER_PATH
        if only_current_test:
            folder_path = ArtifactPublisher.current_test_path
        if os.path.exists(folder_path):
            shutil.rmtree("/{}".format(folder_path), ignore_errors=True)
            print("Deleted old artifacts folder: '{}'".format(folder_path))

    @staticmethod
    def _create_artifact_folder(test_method_name):
        folder_path = ArtifactPublisher.ARTIFACTS_FOLDER_PATH
        ArtifactPublisher.current_test_path = os.path.join(folder_path, test_method_name)
        os.makedirs(ArtifactPublisher.current_test_path)
        print(
            "Created artifacts folder: '{}'".format(ArtifactPublisher.current_test_path)
        )

    @staticmethod
    def get_next_free_filename(file_name):
        folder_path = ArtifactPublisher.current_test_path
        file_ext = os.path.splitext(file_name)[1]
        file_name_no_ext = os.path.splitext(file_name)[0]

        if not os.path.exists(os.path.join(folder_path, file_name)):
            return file_name
        i = 1
        while True:
            new_file_name = "{}({}){}".format(file_name_no_ext, i, file_ext)
            if os.path.exists(os.path.join(ArtifactPublisher.current_test_path, new_file_name)):
                i += 1
            else:
                break
        return new_file_name
