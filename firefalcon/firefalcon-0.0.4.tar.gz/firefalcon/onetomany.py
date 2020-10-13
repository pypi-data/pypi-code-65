from firefalcon.baseresource import BaseResource


class OneToManyResource(BaseResource):
    def __init__(
        self,
        db,
        parent_path: str,
        parent_field_path: str,
        is_subcollection: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)

    def on_get(self, req, resp):
        pass

    def on_get_doc(self, req, resp, doc):
        pass

    def on_post(self, req, resp):
        try:
            validated = self._validate_post(req.media)
            valid_dict = validated.dict()
            
            

        except:
            pass

    def on_put_doc(self, req, resp, doc):
        pass

    def on_delete_doc(self, req, resp, doc):
        pass
