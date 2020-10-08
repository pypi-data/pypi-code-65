import time

from blobhub.blob import Blob, Revision
from blobhub.presets.onnx import Onnx, Model, Config


class TestCollection:

    ORG_ID = "blobhub-unit-tests"
    BLOB_ID = "onnx-multipart-forced-e2e"
    API_KEY = "vVRaTX1QXtx-o8ZRwaQvrnfWRDXmPCxUd7lYarcknsGtV_hExnWLCtKLRWU9PO7NBmMgYrSF3buEi1kOikoeygczKthbsG-joIkPMoD9n_tuDXvYXK-KfHFaPm6Nzn1JAliRtqKD132_BSTKm6uFgrJPPvSa7JpQ11Vzzr2NPIKu7-S2oHUcKgp952yxUuPKWHKLxv58AMDpgDwZKH5pieqR2rx1GKqGOMce-GG_YKMUciQNAY99HgXqcR3VbdWZADw718PCfWtQ-k-e3aQX6dGIpQExPP3iDNTfpd5RbUccF39b38EJSYZ21HG6a231dBMyHLaRajYS06lWOgOiSw"

    def test_model_end_to_end(self):
        # Find blob
        blob = Blob(org_id=self.ORG_ID, blob_id=self.BLOB_ID, api_key=self.API_KEY)
        revision = blob.revisions.latest()

        # Revision must be "draft" and "ready"
        assert revision[Revision.FIELD_PHASE] == Revision.PHASE_DRAFT
        assert revision[Revision.FIELD_STATUS] == Revision.STATUS_READY

        # Force multi-part operations
        config = Config(
            force_multipart_download=True,
            force_multipart_upload=True
        )

        # Initialize preset
        onnx = Onnx(revision=revision, config=config)

        # Upload the model to the revision
        initial_model = Model.from_local_file(onnx=onnx, path="./data/onnx/mnist.onnx")
        success = onnx.upload(model=initial_model)
        assert True == success

        # Wait for the model to be processed
        time.sleep(5)

        # Download and save the model
        downloaded_model = onnx.download()
        assert None != downloaded_model

        # Confirm that downloaded model is identical to the initially downloaded one
        assert downloaded_model.is_identical(model=initial_model)
