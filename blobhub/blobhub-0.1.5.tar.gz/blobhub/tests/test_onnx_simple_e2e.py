import time

from blobhub.blob import Blob, Revision
from blobhub.presets.onnx import Onnx, Model


class TestCollection:

    ORG_ID = "blobhub-unit-tests"
    BLOB_ID = "onnx-simple-e2e"
    API_KEY = "-RgYTiAApnK80nAACiDzfNVSHBOTR1ndrWDAfZUo2MBByZlykH3iZ6JSwZ5q3sabrrEc2q1cdfbUw2_4hNj1zXGtCOH5YWN0TCddTKaOT0ZiD9gMpQClhhj4ErRjtSlKqfqxjoggmeI8993Jf6tgmAwhKUNfl4pyN9dELRjN89BSuGACMERr4uQ6-PUXz0PpAgClEO6DHu5HAYneO4kwEYs7OW7X0_3lCy1C0b56VbbpKW3EJbV2TmbwHJS3szEZycXYPcA1TG09GtzqV-d1gzmexZbPN-Kr8cBPD-SEW78WMJavm-RgUPUrxxb13HrWaw9Q7Wy4DOR8Ney0Eb_Fxg"

    def test_model_end_to_end(self):
        # Find blob
        blob = Blob(org_id=self.ORG_ID, blob_id=self.BLOB_ID, api_key=self.API_KEY)
        revision = blob.revisions.latest()

        # Revision must be "draft" and "ready"
        assert revision[Revision.FIELD_PHASE] == Revision.PHASE_DRAFT
        assert revision[Revision.FIELD_STATUS] == Revision.STATUS_READY

        # Initialize preset
        onnx = Onnx(revision=revision)

        # Upload the model to the revision
        initial_model = Model.from_local_file(onnx=onnx, path="./data/onnx/mnist.onnx")
        success = onnx.upload(model=initial_model)
        assert True == success

        # Wait for the model to be processed
        time.sleep(5)

        # Download and save the model
        downloaded_model = onnx.download()
        assert None != downloaded_model

        # Confirm that downloaded model is identical to the initial one
        assert downloaded_model.is_identical(model=initial_model)
