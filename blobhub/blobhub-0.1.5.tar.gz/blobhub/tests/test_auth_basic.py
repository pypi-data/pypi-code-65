from blobhub.blob import Blob


class TestCollection:

    ORG_ID = "blobhub-unit-tests"
    BLOB_ID = "auth-basic"
    API_KEY = "tHIP4WspEhDOKvNTo5JJ6tEENwQoVHMUIc0tf9dvuR9A3bAf6hxHKXwxSkt48Tx3hRBV5CTfPDhBVZHbyIcy4QtyHxjn-uG5FB3QajJAhg0tZKtecASSjuzFXNlgavZ8nWV8Zvx8c_YudtWsoUXSrzHB9_etDAiJa_js5QqgS4_KBNjMmnjxD1EAwFAiEL0asyFZVQXIiwpcx1eC2bFKhpoNkFlpn7v7dGtwIjcxOIqlgLHALt7joaOlm3IP5MIaeEZgHj_z4IkY5Li63eUH9x1xHsoS0JA_HHBgB1QC8Vls771ERpa7NT35HrlSGtG76KB-QCakE6jl6P4Od0AZMg"

    def test_fetch_blob_revision(self):
        blob = Blob(org_id=self.ORG_ID, blob_id=self.BLOB_ID, api_key=self.API_KEY)
        assert blob[Blob.FIELD_STATUS] == Blob.STATUS_READY

    # TODO: Anonymous read of public - success
    # TODO: Anonymous write of public - failure
    # TODO: Anonymous read of private - failure
    # TODO: Api key fetch of another blob - failure
    # TODO: Api key write operation for write role - success
    # TODO: Api key write operation for read role - failure

