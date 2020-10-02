from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.models.operation_item_add import Operation_item_add, Operation_item_addManager


@JsonResponseWithException()
def Operation_item_add_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Operation_item_add.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Operation_item_addManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_item_add_Add(request):
    return JsonResponse(DSResponseAdd(data=Operation_item_add.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_item_add_Update(request):
    return JsonResponse(DSResponseUpdate(data=Operation_item_add.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_item_add_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Operation_item_add.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_item_add_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Operation_item_add.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_item_add_Info(request):
    return JsonResponse(DSResponse(request=request, data=Operation_item_add.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_item_add_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Operation_item_add.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
