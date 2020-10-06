from django.db.models import Q

from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException, JsonWSResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.operation_typesStack import NoLaunch
from kaf_pas.production.models.launches import Launches
from kaf_pas.production.models.launches_view import Launches_view, Launches_viewManager


@JsonResponseWithException()
def Launches_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Launches_view.objects.
                select_related('demand', 'status', 'item').
                exclude(code='000').
                exclude(code=NoLaunch).
                get_range_rows1(
                request=request,
                function=Launches_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launches_Fetch_4_Production_values(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Launches_view.objects.
                select_related('demand', 'status', 'item').
                filter().
                get_range_rows_4_Production_values(
                request=request,
                function=Launches_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launches_Planing_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Launches_view.objects.
                select_related('demand', 'status', 'item').
                exclude(code=NoLaunch).
                # exclude(status__code='handmade').
                get_range_rows1(
                request=request,
                function=Launches_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launches_Fetch1(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Launches_view.objects.
                select_related('demand', 'status', 'item').
                filter(Q(code='000') | Q(parent__isnull=False)).
                get_range_rows1(
                request=request,
                function=Launches_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonWSResponseWithException()
def Launches_Add(request):
    return JsonResponse(DSResponseAdd(data=Launches.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonWSResponseWithException()
def Launches_Update(request):
    return JsonResponse(DSResponseUpdate(data=Launches.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonWSResponseWithException()
def Launches_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Launches.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launches_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Launches.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launches_Info(request):
    return JsonResponse(DSResponse(request=request, data=Launches.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Launches_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Launches.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def GetQtyChilds(request):
    return JsonResponse(DSResponse(request=request, data=Launches.objects.getQtyChilds(request=request), status=RPCResponseConstant.statusSuccess).response)
