from django.conf import settings

from isc_common.http.DSRequest import DSRequest
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.models.operations_view import Operations_view, Operations_viewManager
from kaf_pas.planing.models.routing import Routing, RoutingManager


@JsonResponseWithException()
def Routing_Fetch(request):
    _request = DSRequest(request=request)
    data = _request.get_data()
    item_id = data.get('item_id')
    resource_id = data.get('resource_id')
    launch_id = data.get('launch_id')
    opers_type = settings.OPERS_TYPES_STACK.ROUTING_TASK.id

    return JsonResponse(
        DSResponse(
            request=request,
            data=Routing.objects.raw(params=[
                item_id,  # 0
                resource_id,  # 1
                launch_id,  # 2
                item_id,  # 3
                opers_type,  # 4
                launch_id,  # 5
                item_id,  # 6
                resource_id,  # 7
                opers_type,  # 8
                launch_id,  # 9
                item_id,  # 10
                resource_id,  # 11
                opers_type,  # 12
                launch_id,  # 13
                item_id,  # 14
                opers_type,  # 15
                launch_id,  # 16
                item_id,  # 17
                resource_id,  # 18
                opers_type,  # 19
                launch_id,  # 20
            ], function=RoutingManager.getRecord),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_FetchView(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Operations_view.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Operations_viewManager.getRecord,
                distinct_field_names=['id']
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Routing_Add(request):
    return JsonResponse(DSResponseAdd(data=Routing.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Routing_Update(request):
    return JsonResponse(DSResponseUpdate(data=Routing.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Routing_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Routing.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Routing_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Routing.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Routing_Info(request):
    return JsonResponse(DSResponse(request=request, data=Routing.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Routing_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Routing.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Routing_FetchLevels(request):
    return JsonResponse(DSResponse(request=request, data=Routing.objects.fetchLevelsFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Routing_FetchLocationsLevel(request):
    return JsonResponse(DSResponse(request=request, data=Routing.objects.fetchLocationsLevelFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Routing_FetchResourcesLevel(request):
    return JsonResponse(DSResponse(request=request, data=Routing.objects.fetchResourcesLevelFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Routing_CleanRoutes(request):
    return JsonResponse(DSResponseUpdate(data=Routing.objects.cleanRoutesFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Routing_ReCalcRoutes(request):
    return JsonResponse(DSResponseUpdate(data=Routing.objects.reCalcRoutesFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
