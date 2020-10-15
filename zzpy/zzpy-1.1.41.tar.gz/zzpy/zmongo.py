from deprecated.sphinx import deprecated


__MONGO_URL_KEY = "MONGO_URL"


class MongoConfig:
    default_host = "localhost"
    default_port = 27017

    def __init__(self, url=None, host=None, port=None, database=None, param=None):
        import re
        if url:
            result = re.search(
                "^(mongodb://){0,1}([^:/]+)(:(\d+)){0,1}(/([^?]+)){0,1}(\?(.*)){0,1}", url)
            groups = result.groups()
            if not host:
                host = groups[1] if groups[1] else self.default_host
            if not port:
                port = int(groups[3]) if groups[3] else self.default_port
            if not database:
                database = groups[5] if groups[5] else None
            if not param:
                param = dict([it.split('=')
                              for it in groups[7].split('&')]) if groups[7] else {}
        self.url = url
        self.host = host
        self.port = port
        self.database = database
        self.param = param if param else {}

    def __eq__(self, value):
        return self.host == value.host and self.port == value.port and self.database == value.database and self.param == value.param


def mongo_connect(url=None):
    if not url:
        from .zconfig import get_param
        url = get_param(__MONGO_URL_KEY)
    assert url

    from pymongo import MongoClient
    import pytz

    conf = MongoConfig(url)
    client = MongoClient(host=conf.host, port=conf.port, tz_aware=True, tzinfo=pytz.timezone(
        'Asia/Shanghai'))
    if conf.database:
        client = client.get_database(conf.database)
    return client


def mongo_collection(client, collection):
    col = client
    for c in collection.split("."):
        col = col[c]
    return col


def mongo_count_collection(client, collection, where_condition=None):
    if where_condition is None:
        where_condition = {}
    return mongo_collection(client, collection).count_documents(where_condition)


def mongo_download(client, path, collection, find_args=None, progress_title=None):
    import jsonlines
    import json
    from .zjson import jsondumps
    from .zprogress import pb

    if find_args is None:
        find_args = {}

    with jsonlines.open(path, mode="w") as fw:
        iter = mongo_collection(client, collection).find(**find_args)
        if progress_title:
            total = mongo_collection(
                client, collection).estimated_document_count()
            for item in pb(iter, total=total, title=progress_title):
                fw.write(json.loads(jsondumps(item)))
        else:
            for item in iter:
                fw.write(json.loads(jsondumps(item)))


@deprecated
def mongo_download_collection(client, path, collection, where_condition=None, progress_title=None, estimated_count=True):
    import jsonlines
    import json
    from .zjson import jsondumps
    from .zprogress import pb

    if where_condition is None:
        where_condition = {}

    with jsonlines.open(path, mode="w") as fw:
        iter = mongo_collection(client, collection).find(where_condition)
        if progress_title:
            if estimated_count:
                total = mongo_collection(
                    client, collection).estimated_document_count()
            else:
                total = mongo_count_collection(
                    client, collection=collection, where_condition=where_condition)
            for item in pb(iter, total=total, title=progress_title):
                fw.write(json.loads(jsondumps(item)))
        else:
            for item in iter:
                fw.write(json.loads(jsondumps(item)))


def main():
    assert MongoConfig(url="mongodb://a:1") == MongoConfig(host="a", port=1)


if __name__ == "__main__":
    main()
