from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.models.operation_launch_item import Operation_launch_item, Operation_launch_itemManager


@JsonResponseWithException()
def Operation_launch_item_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Operation_launch_item.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Operation_launch_itemManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_launch_item_Add(request):
    return JsonResponse(DSResponseAdd(data=Operation_launch_item.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_launch_item_Update(request):
    return JsonResponse(DSResponseUpdate(data=Operation_launch_item.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_launch_item_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Operation_launch_item.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_launch_item_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Operation_launch_item.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_launch_item_Info(request):
    return JsonResponse(DSResponse(request=request, data=Operation_launch_item.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_launch_item_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Operation_launch_item.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
