from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.locations import Locations
from kaf_pas.ckk.models.locations_view import Locations_view, Locations_viewManager


@JsonResponseWithException()
def Locations_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Locations_view.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Locations_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Locations_Add(request):
    return JsonResponse(DSResponseAdd(data=Locations.objects.createFromRequest(request=request, propsArr=['isWorkshop']), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Locations_Update(request):
    return JsonResponse(DSResponseUpdate(data=Locations.objects.updateFromRequest(request=request, removed=['calendar__full_name'], propsArr=['isWorkshop']), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Locations_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Locations.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Locations_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Locations.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Locations_Info(request):
    return JsonResponse(DSResponse(request=request, data=Locations.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
