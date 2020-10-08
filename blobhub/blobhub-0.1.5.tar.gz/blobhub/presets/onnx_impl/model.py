import hashlib
import os.path
import shutil
from typing import Optional


class InvalidOnnxFile(Exception):

    def __init__(self, path: str, message: str) -> None:
        super().__init__(message)
        self.path = path


class Model:

    @staticmethod
    def from_local_file(onnx: "Onnx", path: str):
        # Validate local file correctness
        Model._validate_local_onnx_file(path=path)

        # Construct model
        return Model(onnx=onnx, path=path)

    def __init__(self, onnx: "Onnx", path: Optional[str]) -> None:
        self.onnx = onnx
        self.path = path

    def save_to_file(self, path: str) -> None:
        # This is current assumption that the model referred by this class is always stored on disk.
        # This method merely copies the model to the new location.
        shutil.copy2(self.path, path)

    def is_identical(self, model: "Model"):
        reference_model_data = self._read_file(model.path)
        reference_model_hash = hashlib.sha256(reference_model_data).hexdigest()

        self_model_data = self._read_file(self.path)
        self_model_hash = hashlib.sha256(self_model_data).hexdigest()

        return reference_model_hash == self_model_hash

    """
    File Operations
    """

    @staticmethod
    def _validate_local_onnx_file(path: str):
        try:
            # Confirm .onnx file
            if not path.endswith(".onnx"):
                raise Exception("only_onnx_models_are_supported")

            # Validate file presence
            cwd = os.getcwd()
            if not os.path.exists(path):
                raise Exception("specified_file_does_not_exist")

            # NEXT: Validate ONNX format
        except Exception as e:
            raise InvalidOnnxFile(path=path, message=str(e))

    @staticmethod
    def _read_file(path):
        with open(path, "rb") as file:
            data = file.read()
            return data
