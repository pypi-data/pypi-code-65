import time

from blobhub.blob import Blob, Revision
from blobhub.presets.onnx import Onnx, Model


class TestCollection:

    ORG_ID = "blobhub-unit-tests"
    BLOB_ID = "onnx-multipart-large-e2e"
    API_KEY = "7gZaoBCmXL_IJANMEDbG6ttUewmq7rPEwwZKhxm_Zz1LwyXiwfgKIq1aFPb39hRVuLqmSBY_mahYyiUzOw-0aLiONWvOQxBjFJqiUy1gkzUwO_7hM-Kud6UzoTGypbG51U1oIZRW867kklJRZUwQ8ub598mAEppRCXZlkIORb8Yhk2NMCBcDkXDe426V3w-VGKba5cXiHtZHRD2vGtJU42IkncPgHKx5rYF2FGc65m4TIGzW-HVCVkpfMVpo8y2F5r1MKfVewRw9X55mVDEOjcOe9ZV14kKiAgxn9X9qgUU8oe4DiFkIIm53yPMOgAolOXucbZcvFMu9LB-YNdBV_Q"

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
        initial_model = Model.from_local_file(onnx=onnx, path="./data/onnx/bertsquad10.onnx")
        success = onnx.upload(model=initial_model)
        assert True == success

        # Wait for the model to be processed
        time.sleep(60)

        # Download and save the model
        downloaded_model = onnx.download()
        assert None != downloaded_model

        # Confirm that downloaded model is identical to the initially downloaded one
        assert downloaded_model.is_identical(model=initial_model)
