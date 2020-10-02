from django.urls import path

from kaf_pas.planing.views import tmp_operation_value

urlpatterns = [

    path('Tmp_operation_value/Fetch/', tmp_operation_value.Tmp_operation_value_Fetch),
    path('Tmp_operation_value_view/Fetch/', tmp_operation_value.Tmp_operation_value_viewFetch),
    path('Tmp_operation_value/Add', tmp_operation_value.Tmp_operation_value_Add),
    path('Tmp_operation_value/Update', tmp_operation_value.Tmp_operation_value_Update),
    path('Tmp_operation_value/Remove', tmp_operation_value.Tmp_operation_value_Remove),
    path('Tmp_operation_value/Lookup/', tmp_operation_value.Tmp_operation_value_Lookup),
    path('Tmp_operation_value/Info/', tmp_operation_value.Tmp_operation_value_Info),
    path('Tmp_operation_value/Copy', tmp_operation_value.Tmp_operation_value_Copy),

]
