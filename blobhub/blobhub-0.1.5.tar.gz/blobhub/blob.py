from .api import Api


class Revision:

    FIELD_ID = "id"
    FIELD_STATUS = "status"
    FIELD_PHASE = "phase"

    STATUS_READY = "ready"

    PHASE_DRAFT = "draft"

    def __init__(self, blob, revision_id, revision_descr):
        self.blob = blob
        self.revision_id = revision_id
        self.revision_descr = revision_descr

    def __getitem__(self, key):
        return self.revision_descr[key]


class Revisions:

    def __init__(self, blob):
        self.blob = blob
        self.revisions_descr = self.blob.api.blobs_blob_id_org_id_revisions_get_dict(
            org_id=self.blob.org_id,
            blob_id=self.blob.blob_id
        )
        self.revisions_index = {
            revision_descr["id"]:Revision(
                blob=self.blob,
                revision_id=revision_descr["id"],
                revision_descr=revision_descr)
            for revision_descr in self.revisions_descr
        }
        self.revisions_list = [
            self.revisions_index[revision_descr["id"]]
            for revision_descr in self.revisions_descr
        ]

    def latest(self):
        return self.revisions_list[0] if len(self.revisions_list) > 0 else None


class Blob:

    FIELD_ID = "id"
    FIELD_STATUS = "status"

    STATUS_READY = "ready"

    def __init__(self, org_id, blob_id, api_key=None):
        self.org_id = org_id
        self.blob_id = blob_id
        self.api = Api(api_key=api_key)
        self.blob_descr = self.api.blobs_blob_id_org_id_get_dict(
            org_id=org_id,
            blob_id=blob_id
        )
        self.revisions = Revisions(blob=self)

    def __getitem__(self, key):
        return self.blob_descr[key]
