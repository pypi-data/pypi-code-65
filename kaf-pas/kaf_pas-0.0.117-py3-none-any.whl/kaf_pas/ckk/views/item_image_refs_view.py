from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.item_image_refs_view import Item_image_refs_view, Item_image_refs_viewManager


@JsonResponseWithException()
def Item_image_refs_view_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Item_image_refs_view.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Item_image_refs_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_image_refs_view_Add(request):
    return JsonResponse(DSResponseAdd(data=Item_image_refs_view.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_image_refs_view_Update(request):
    return JsonResponse(DSResponseUpdate(data=Item_image_refs_view.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_image_refs_view_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Item_image_refs_view.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_image_refs_view_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Item_image_refs_view.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_image_refs_view_Info(request):
    return JsonResponse(DSResponse(request=request, data=Item_image_refs_view.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_image_refs_view_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Item_image_refs_view.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
