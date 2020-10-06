from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.production.models.launch_operation_attr import Launch_operation_attr, Launch_operation_attrManager


@JsonResponseWithException()
def Launch_operation_attr_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Launch_operation_attr.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Launch_operation_attrManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launch_operation_attr_Add(request):
    return JsonResponse(DSResponseAdd(data=Launch_operation_attr.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launch_operation_attr_Update(request):
    return JsonResponse(DSResponseUpdate(data=Launch_operation_attr.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launch_operation_attr_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Launch_operation_attr.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launch_operation_attr_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Launch_operation_attr.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launch_operation_attr_Info(request):
    return JsonResponse(DSResponse(request=request, data=Launch_operation_attr.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launch_operation_attr_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Launch_operation_attr.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
