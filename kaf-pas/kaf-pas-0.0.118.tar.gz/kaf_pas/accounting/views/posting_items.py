from django.conf import settings

from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.accounting.models.posting_items import Posting_items, Posting_itemsManager
from kaf_pas.planing.models.operations import Operations


@JsonResponseWithException()
def Posting_Fetch(request):
    opers_types = [
        settings.OPERS_TYPES_STACK.POSTING_TASK.id,
    ]
    return JsonResponse(
        DSResponse(
            request=request,
            data=Posting_items.objects.
                filter(opertype__in=opers_types).
                get_range_rows1(
                request=request,
                function=Posting_itemsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Posting_Fetch1(request):
    opers_types = [
        settings.OPERS_TYPES_STACK.POSTING_EQV_TASK.id,
    ]
    return JsonResponse(
        DSResponse(
            request=request,
            data=Posting_items.objects.
                filter(opertype__in=opers_types).
                get_range_rows1(
                request=request,
                function=Posting_itemsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Posting_items_Fetch(request):
    # _request = DSRequest(request)
    return JsonResponse(
        DSResponse(
            request=request,
            data=Posting_items.objects.
                get_range_rows1(
                request=request,
                function=Posting_itemsManager.getRecordDet
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Posting_items_Add(request):
    return JsonResponse(DSResponseAdd(data=Posting_items.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Posting_items_Add1(request):
    return JsonResponse(DSResponseAdd(data=Posting_items.objects.create1FromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Posting_item_Add(request):
    return JsonResponse(DSResponseAdd(data=Operations.objects.createFromRequest(request=request, removed=[
        'creator__short_name',
        'status__code',
        'status__name',
        'opertype__full_name',
        'isFolder',
        'color__name',
        'color__color',
        'location__code',
        'location__name',
        'location__full_name',
        'item__STMP_1_id',
        'item__STMP_1__value_str',
        'item__STMP_2_id',
        'item__STMP_2__value_str',
        'edizm__code',
        'edizm__name',
    ]), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Posting_items_Update(request):
    return JsonResponse(DSResponseUpdate(data=Posting_items.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Posting_items_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Posting_items.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Posting_items_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Posting_items.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Posting_items_Info(request):
    return JsonResponse(DSResponse(request=request, data=Posting_items.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Posting_items_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Posting_items.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
