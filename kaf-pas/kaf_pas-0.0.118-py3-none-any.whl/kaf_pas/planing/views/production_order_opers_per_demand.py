from isc_common.http.DSResponse import DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.planing.models.production_order_opers_per_demant import Production_order_opers_per_demand, Production_order_opers_per_demandManager


@JsonResponseWithException()
def Production_order_opers_per_demand_Fetch(request):
    # _request = DSRequest(request=request)

    return JsonResponse(
        DSResponse(
            request=request,
            data=Production_order_opers_per_demand.objects.
                select_related('demand', 'item', 'launch', 'parent_launch', 'color', 'edizm').
                get_range_rows1(
                request=request,
                function=Production_order_opers_per_demandManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)
