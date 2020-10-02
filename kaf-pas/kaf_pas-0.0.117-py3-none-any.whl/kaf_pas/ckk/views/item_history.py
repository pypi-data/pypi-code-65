from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.item_history import Item_history, Item_historyManager


@JsonResponseWithException()
def Item_history_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Item_history.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Item_historyManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_history_Add(request):
    return JsonResponse(DSResponseAdd(data=Item_history.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_history_Update(request):
    return JsonResponse(DSResponseUpdate(data=Item_history.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_history_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Item_history.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_history_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Item_history.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_history_Info(request):
    return JsonResponse(DSResponse(request=request, data=Item_history.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_history_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Item_history.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
