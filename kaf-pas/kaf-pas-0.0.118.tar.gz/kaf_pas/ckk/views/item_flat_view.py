from isc_common.http.DSRequest import DSRequest
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException, JsonWSResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.item_flat_view import Item_flat_view, Item_flat_viewManager
from kaf_pas.planing.models.operation_item_view import Operation_item_viewManager


@JsonResponseWithException()
def Item_flat_view_Fetch(request):
    _request = DSRequest(request=request)

    return JsonResponse(
        DSResponse(
            request=request,
            data=Item_flat_view.objects.
                select_related(
                'STMP_1',
                'STMP_2',
                'document',
                'lotsman_document',
            ).
                get_range_rows1(
                request=request,
                function=Item_flat_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_flat_view_FetchPlan(request):
    from isc_common.http.DSRequest import DSRequest
    from kaf_pas.planing.models.operation_item_view import Operation_item_view

    _request = DSRequest(request=request)
    data = _request.get_data()

    return JsonResponse(
        DSResponse(
            request=request,
            data=Operation_item_view.objects.filter(
                launch_id=data.get('launch_id'),
                level_id=data.get('level_id'),
                resource_id=data.get('resource_id'),
                location_id=data.get('location_id'),
            ).distinct('item').
                get_range_rows1(
                request=request,
                function=Operation_item_viewManager.getRecord,
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_flat_view_Add(request):
    return JsonResponse(DSResponseAdd(data=Item.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonWSResponseWithException()
def Item_flat_view_Update(request):
    return JsonResponse(DSResponseUpdate(data=Item.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_flat_view_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Item.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_flat_view_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Item.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_flat_view_Info(request):
    return JsonResponse(DSResponse(request=request, data=Item_flat_view.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_flat_view_InfoPlan(request):
    return JsonResponse(DSResponse(request=request, data=Item_flat_view.objects.get_queryset().get_infoPlan(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_flat_view_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Item_flat_view.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
