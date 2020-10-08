import json
import datetime
try:
    """Installation::
        pip install constants_and_utils["mongoengine"]
    """
    from deepdiff import DeepDiff
    from bson import ObjectId, DBRef, Binary
    from mongoengine import Document as MongoDocument
except ImportError:
    raise ImportError('MongoEngine not installed')


class JSONEncoder(json.JSONEncoder):
    """Encode JSON objects replacing ObjectId, DBRef, Binary and datetime objects
        with only their content"""
    def default(self, o):
        if (isinstance(o, ObjectId) or
                isinstance(o, DBRef) or
                isinstance(o, datetime.datetime) or
                isinstance(o, Binary)):
            return str(o)
        return json.JSONEncoder.default(self, o)


def diff_mongo_objects(
    old_object: MongoDocument,
    new_object: MongoDocument,
    ignore_order: bool = True,
    exclude_list: list = [],
    verbose_level: int = 2,
) -> dict:
    """It compare Mongo object and object modified,

    Args:
        old_object (mongoengine.Document): Mongo Document
        new_object (mongoengine.Document): Mongo Document
        ignore_order (bool): default True
        exclude_list (list): default []. Example::
                ["root['created_at']", ]
        verbose_level (int): default 2

    Returns:
        dict: changes

    Examples:
        Run function::
            >>> old_mongo_doc = MongoDocumentExampleOld()
            >>> new_mongo_doc = MongoDocumentExampleNew()
            >>> diff_mongo_objects(
            ...   old_object=old_mongo_doc,
            ...   new_object=new_mongo_doc
            ... )
            {
                "values_changed":{
                    "root['formulas']":{
                        "new_value":"0+2",
                        "old_value":"0+1"
                    },
                },
                "iterable_item_added":{
                    "root['sub_item'][2]":{
                        "uuid":"0d465a99-963d-4cc8-8275-56293af89083",
                    },
                },
                "iterable_item_removed":{
                    "root['sub_item'][1]":{
                        "uuid":"c0f83600-f940-4f7f-9a47-e67c97fb1615",
                    }
                }
            }
    """

    # Get dict from object
    old = old_object.to_mongo().to_dict()
    new = new_object.to_mongo().to_dict()

    def get_dbrefs(obj, obj_dict):
        for key, value in obj_dict.items():
            # If it is of type DBRef
            if isinstance(value, DBRef):
                field = getattr(obj, key)
                mongo_dict = field.to_mongo().to_dict()
                obj_dict[key] = mongo_dict
                get_dbrefs(field, mongo_dict)
            elif isinstance(value, list):
                for x, v in enumerate(value):
                    # If it is of type DBRef
                    if isinstance(v, DBRef):
                        mongo_dict = getattr(obj, key)[x].to_mongo().to_dict()
                        obj_dict[key][x] = mongo_dict
        return obj_dict

    old = get_dbrefs(old_object, old)
    new = get_dbrefs(new_object, new)

    old = json.loads(JSONEncoder().encode(old))
    new = json.loads(JSONEncoder().encode(new))
    diff = DeepDiff(
        old,
        new,
        ignore_order=ignore_order,
        verbose_level=verbose_level,
        exclude_paths=exclude_list
    )
    return json.loads(diff.to_json())
