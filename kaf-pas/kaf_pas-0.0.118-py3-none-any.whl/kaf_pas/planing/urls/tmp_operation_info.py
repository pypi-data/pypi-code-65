from django.urls import path

from kaf_pas.planing.views import tmp_operation_info

urlpatterns = [

    path('Tmp_operation_info/Fetch/', tmp_operation_info.Tmp_operation_info_Fetch),
    path('Tmp_operation_info/Add', tmp_operation_info.Tmp_operation_info_Add),
    path('Tmp_operation_info/Update', tmp_operation_info.Tmp_operation_info_Update),
    path('Tmp_operation_info/Remove', tmp_operation_info.Tmp_operation_info_Remove),
    path('Tmp_operation_info/Lookup/', tmp_operation_info.Tmp_operation_info_Lookup),
    path('Tmp_operation_info/Info/', tmp_operation_info.Tmp_operation_info_Info),
    path('Tmp_operation_info/Copy', tmp_operation_info.Tmp_operation_info_Copy),

]
