import json
import os
import tempfile
from collections import OrderedDict

from django.apps import apps
from django.core import serializers

from .adapter import DBAdapter


class CouchdbStream:
    def __init__(self):
        self.db = DBAdapter()
        self.output = tempfile.NamedTemporaryFile(delete=False, suffix='.json')

    def __del__(self):
        del self.db
        os.remove(self.output.name)

    def write(self, val):
        self.output.write(bytes(val, encoding='utf-8'))

    def read(self):
        with open(self.output.name, 'r') as fd:
            return json.load(fd)

    def get_output_name(self):
        return self.output.name

    def send(self):
        for obj in self.read():
            self.db.put_document(obj)

    def retrieve(self):
        """
        Objects must be imported following the right order
        """
        def _clean(doc):
            d = doc['doc']
            _doc_id = d.pop('_id')
            _doc_rev = d.pop('_rev')
            return d

        _docs = self.db.get_documents()['rows']
        app_labels = set(list(map(lambda x: x['doc']['model'], _docs)))

        app_list = OrderedDict()
        for label in app_labels:
            app_label, model_label = label.split('.')
            try:
                app_config = apps.get_app_config(app_label)
            except LookupError as e:
                raise Exception(str(e))

            try:
                model = app_config.get_model(model_label)
            except LookupError:
                raise Exception("Unknown model: %s.%s" % (app_label, model_label))

            app_list_value = app_list.setdefault(app_config, [])

            # We may have previously seen a "all-models" request for
            # this app (no model qualifier was given). In this case
            # there is no need adding specific models to the list.
            if app_list_value is not None:
                if model not in app_list_value:
                    app_list_value.append(model)

        sorted_models = serializers.sort_dependencies(app_list.items())

        docs = []
        for model in sorted_models:
            model_label = model._meta.label.lower()

            model_docs = list(filter(lambda x: x['doc']['model'] == model_label, _docs))

            docs += list(map(lambda x: _clean(x), model_docs))

        with open(self.output.name, 'w') as fd:
            json.dump(docs, fd)