from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.models.operation_operation_history import Operation_operation_history, Operation_operation_historyManager


@JsonResponseWithException()
def Operation_operation_history_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Operation_operation_history.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Operation_operation_historyManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_operation_history_Add(request):
    return JsonResponse(DSResponseAdd(data=Operation_operation_history.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_operation_history_Update(request):
    return JsonResponse(DSResponseUpdate(data=Operation_operation_history.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_operation_history_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Operation_operation_history.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_operation_history_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Operation_operation_history.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_operation_history_Info(request):
    return JsonResponse(DSResponse(request=request, data=Operation_operation_history.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_operation_history_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Operation_operation_history.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
