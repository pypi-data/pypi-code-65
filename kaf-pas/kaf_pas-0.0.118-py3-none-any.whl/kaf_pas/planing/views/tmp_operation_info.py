from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.models.tmp_operation_info import Tmp_operation_info, Tmp_operation_infoManager


@JsonResponseWithException()
def Tmp_operation_info_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Tmp_operation_info.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Tmp_operation_infoManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tmp_operation_info_Add(request):
    return JsonResponse(DSResponseAdd(data=Tmp_operation_info.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tmp_operation_info_Update(request):
    return JsonResponse(DSResponseUpdate(data=Tmp_operation_info.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tmp_operation_info_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Tmp_operation_info.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tmp_operation_info_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Tmp_operation_info.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tmp_operation_info_Info(request):
    return JsonResponse(DSResponse(request=request, data=Tmp_operation_info.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tmp_operation_info_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Tmp_operation_info.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
