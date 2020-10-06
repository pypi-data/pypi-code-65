from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.production.models.launch_detail import Launch_detail, Launch_detailManager


@JsonResponseWithException()
def Launch_detail_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Launch_detail.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Launch_detailManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launch_detail_Add(request):
    return JsonResponse(DSResponseAdd(data=Launch_detail.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launch_detail_Update(request):
    return JsonResponse(DSResponseUpdate(data=Launch_detail.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launch_detail_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Launch_detail.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launch_detail_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Launch_detail.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launch_detail_Info(request):
    return JsonResponse(DSResponse(request=request, data=Launch_detail.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launch_detail_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Launch_detail.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
