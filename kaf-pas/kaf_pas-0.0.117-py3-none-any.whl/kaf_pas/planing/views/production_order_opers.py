from django.conf import settings

from isc_common.http.DSRequest import DSRequest
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.models.production_order_opers import Production_order_opers, Production_order_opersManager
from kaf_pas.planing.models.production_order_opers_per_launch import Production_order_opers_per_launch


@JsonResponseWithException()
def Production_order_opers_Fetch(request):
    opers_types = [
        settings.OPERS_TYPES_STACK.PRODUCTION_DETAIL_OPERS_TASK.id,
    ]

    _request = DSRequest(request=request)
    return JsonResponse(
        DSResponse(
            request=request,
            data=Production_order_opers.objects.
                filter(
                opertype__in=opers_types,
            ).distinct().
                get_range_rows1(
                request=request,
                function=Production_order_opersManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Production_order_per_launch_FetchDetail(request):
    opers_types = [
        settings.OPERS_TYPES_STACK.PRODUCTION_DETAIL_OPERS_TASK.id,
    ]

    # _request = DSRequest(request=request)
    return JsonResponse(
        DSResponse(
            request=request,
            data=Production_order_opers_per_launch.objects.
                filter(
                opertype__in=opers_types,
            ).distinct().
                get_range_rows1(
                request=request,
                function=Production_order_opersManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Production_order_opers_Add(request):
    return JsonResponse(DSResponseAdd(data=Production_order_opers.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Production_order_opers_Update(request):
    return JsonResponse(DSResponseUpdate(data=Production_order_opers.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Production_order_opers_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Production_order_opers.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Production_order_opers_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Production_order_opers.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Production_order_opers_Info(request):
    return JsonResponse(DSResponse(request=request, data=Production_order_opers.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Production_order_opers_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Production_order_opers.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
