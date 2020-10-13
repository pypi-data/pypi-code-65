from .loader import *
from .queries import *
from .services import *
from .transactions import *
from .web import *


class Context:

    def __init__(self, session):
        self._web = WebRequester(session)

    def get(self, query: QueryBase):
        if isinstance(query, ServiceRequestBase):
            res = self._get_info_response(query)
        else:
            res = self._get_query_response(query)

        if isinstance(res, Success) and isinstance(res.result, list):
            arr = res.result
            if len(arr) > 0 and isinstance(query, SingleResultQuery):
                return Success(res.code, arr[0])

        return res

    def execute(self, operation_builder: TransactionBuilder):
        operation = operation_builder.build()
        path = operation.url_path

        try:
            if isinstance(operation, PostTransaction):
                with self._web.post(path, operation.post_obj) as response:
                    return ResponseLoader.load_operation_response(response)

            if isinstance(operation, PutTransaction):
                with self._web.put(path, operation.put_obj) as response:
                    return ResponseLoader.load_operation_response(response)

            if isinstance(operation, DeleteTransaction):
                with self._web.delete(path) as response:
                    return ResponseLoader.load_operation_response(response)

            return Error(0, 'Operation not defined')

        except Exception as ex:
            return Error(0, ex.__str__())

    # private members

    def _get_info_response(self, info_query: ServiceRequestBase):
        path = info_query.url_path
        obj = info_query.obj

        switcher = {
            'get': lambda: self._web.get_with_content(path, obj),
            'post': lambda: self._web.post(path, obj),
            'put': lambda: self._web.put(path, obj)
        }

        if info_query.method in switcher:
            caller = switcher[info_query.method]
            with caller() as response:
                return ResponseLoader.load_get_response(response, False)

        return Error(400, 'Not valid info query')

    def _get_query_response(self, query):
        with self._web.get(query.url_path) as response:
            return ResponseLoader.load_get_response(response, True)
