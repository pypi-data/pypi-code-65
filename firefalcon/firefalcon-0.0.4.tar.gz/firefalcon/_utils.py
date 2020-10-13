from firebase_admin import firestore

def create_collection_query(collection, params=None):
    if params is None:
        return collection
    # if req.params:
    #     params = self._validate_q(req.params)

    #     if params.order_by:
    #         query = query.order_by(
    #             field_path=params.order_by, direction=params.order_dir
    #         )

    return collection


def parse_docs(self, docs):
    doc_list = []
    for doc in docs:

        doc_list.append(
            {
            "id": doc.id,
            "type": self._resource_type,
            "attributes": self._validate_get(doc.to_dict()).dict(),
            }
        )
    return doc_list


# def one_to_many_post(db):
#     transaction = db.transaction()
    
#     @firestore.transactional
    