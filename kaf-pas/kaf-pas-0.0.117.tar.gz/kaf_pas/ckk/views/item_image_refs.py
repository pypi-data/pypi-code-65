from isc_common.http.DSRequest import DSRequest
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.item_image_refs import Item_image_refs, Item_image_refsManager


@JsonResponseWithException()
def Item_image_refs_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Item_image_refs.objects.
                filter(thumb__isnull=False).
                get_range_rows1(
                request=request,
                function=Item_image_refsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_image_refs_Add(request):
    return JsonResponse(DSResponseAdd(data=Item_image_refs.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_image_refs_Update(request):
    return JsonResponse(DSResponseUpdate(data=Item_image_refs.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_image_refs_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Item_image_refs.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_image_refs_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Item_image_refs.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_image_refs_Info(request):
    return JsonResponse(DSResponse(request=request, data=Item_image_refs.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Item_image_refs_Copy(request):
    _request = DSRequest(request=request)

    source = _request.json.get('source')
    srecords = source.get('records')

    destination = _request.json.get('destination')
    drecords = destination.get('records')

    res = False
    if isinstance(srecords, list):
        for srecord in srecords:
            for drecord in drecords:
                from kaf_pas.ckk.models.item import Item
                from kaf_pas.kd.models.documents_thumb import Documents_thumb

                try:
                    item = Item.objects.get(id=drecord.get('child_id'))
                except Item.DoesNotExist:
                    item = Item.objects.get(id=drecord.get('id'))

                thumb = Documents_thumb.objects.get(id=srecord.get('id'))

                item_refs, created = Item_image_refs.objects.get_or_create(item=item, thumb=thumb)
                if not created:
                    raise Exception(f'Элемент: {thumb} уже присутствует у товарной позиции: {item.item_name}')
                res = True

    if not res:
        raise Exception('Копирование не выполнено.')

    return JsonResponse(DSResponse(request=request, status=RPCResponseConstant.statusSuccess).response)
