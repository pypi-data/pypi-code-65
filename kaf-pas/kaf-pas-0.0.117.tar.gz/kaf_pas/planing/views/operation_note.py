from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.models.operation_note import Operation_note, Operation_noteManager


@JsonResponseWithException()
def Operation_note_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Operation_note.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Operation_noteManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_note_Add(request):
    return JsonResponse(DSResponseAdd(data=Operation_note.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_note_Update(request):
    return JsonResponse(DSResponseUpdate(data=Operation_note.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_note_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Operation_note.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_note_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Operation_note.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_note_Info(request):
    return JsonResponse(DSResponse(request=request, data=Operation_note.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operation_note_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Operation_note.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
