from django.urls import path

from kaf_pas.planing.views import operation_history

urlpatterns = [

    path('Operation_history/Fetch/', operation_history.Operation_history_Fetch),
    path('Operation_history/Add', operation_history.Operation_history_Add),
    path('Operation_history/Update', operation_history.Operation_history_Update),
    path('Operation_history/Remove', operation_history.Operation_history_Remove),
    path('Operation_history/Lookup/', operation_history.Operation_history_Lookup),
    path('Operation_history/Info/', operation_history.Operation_history_Info),
    path('Operation_history/Copy', operation_history.Operation_history_Copy),

]
