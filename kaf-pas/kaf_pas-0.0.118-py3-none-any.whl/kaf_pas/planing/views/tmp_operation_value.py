from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.models.tmp_operation_value import Tmp_operation_value, Tmp_operation_valueManager
from kaf_pas.planing.models.tmp_operation_value_view import Tmp_operation_value_view, Tmp_operation_value_viewManager


@JsonResponseWithException()
def Tmp_operation_value_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Tmp_operation_value.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Tmp_operation_valueManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tmp_operation_value_viewFetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Tmp_operation_value_view.objects.
                select_related('launch', 'demand', 'color', 'edizm', 'STMP_1', 'STMP_2', 'last_tech_operation').
                filter().
                distinct().
                get_range_rows1(
                request=request,
                function=Tmp_operation_value_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tmp_operation_value_Add(request):
    return JsonResponse(DSResponseAdd(data=Tmp_operation_value.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tmp_operation_value_Update(request):
    return JsonResponse(DSResponseUpdate(data=Tmp_operation_value.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tmp_operation_value_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Tmp_operation_value.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tmp_operation_value_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Tmp_operation_value.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tmp_operation_value_Info(request):
    return JsonResponse(DSResponse(request=request, data=Tmp_operation_value.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tmp_operation_value_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Tmp_operation_value.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
