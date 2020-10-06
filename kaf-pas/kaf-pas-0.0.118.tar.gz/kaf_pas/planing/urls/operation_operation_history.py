from django.urls import path

from kaf_pas.planing.views import operation_operation_history

urlpatterns = [

    path('Operation_operation_history/Fetch/', operation_operation_history.Operation_operation_history_Fetch),
    path('Operation_operation_history/Add', operation_operation_history.Operation_operation_history_Add),
    path('Operation_operation_history/Update', operation_operation_history.Operation_operation_history_Update),
    path('Operation_operation_history/Remove', operation_operation_history.Operation_operation_history_Remove),
    path('Operation_operation_history/Lookup/', operation_operation_history.Operation_operation_history_Lookup),
    path('Operation_operation_history/Info/', operation_operation_history.Operation_operation_history_Info),
    path('Operation_operation_history/Copy', operation_operation_history.Operation_operation_history_Copy),

]
