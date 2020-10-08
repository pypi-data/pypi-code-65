from blobhub.blob import Blob, Revision


class TestCollection:

    ORG_ID = "NLP"
    BLOB_ID = "ConceptNet"

    def test_fetch_blob_revision(self):
        blob = Blob(org_id=self.ORG_ID, blob_id=self.BLOB_ID)
        latest_revision = blob.revisions.latest()
        assert latest_revision[Revision.FIELD_PHASE] == Revision.PHASE_DRAFT
        assert latest_revision[Revision.FIELD_STATUS] == Revision.STATUS_READY
