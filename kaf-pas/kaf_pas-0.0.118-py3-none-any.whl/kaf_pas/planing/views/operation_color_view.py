from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.models.operation_color_view import Operation_color_viewManager, Operation_color_view


@JsonResponseWithException()
def Operation_color_view_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Operation_color_view.objects.
                select_related('color', 'demand', 'launch', 'operation').
                get_range_rows1(
                request=request,
                function=Operation_color_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_color_view_Add(request):
    return JsonResponse(DSResponseAdd(data=Operation_color_view.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_color_view_Update(request):
    return JsonResponse(DSResponseUpdate(data=Operation_color_view.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_color_view_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Operation_color_view.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_color_view_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Operation_color_view.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_color_view_Info(request):
    return JsonResponse(DSResponse(request=request, data=Operation_color_view.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_color_view_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Operation_color_view.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
