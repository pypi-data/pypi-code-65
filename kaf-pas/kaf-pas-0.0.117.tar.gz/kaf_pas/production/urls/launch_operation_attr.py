from django.urls import path

from kaf_pas.production.views import launch_operation_attr

urlpatterns = [

    path('Launch_operation_attr/Fetch/', launch_operation_attr.Launch_operation_attr_Fetch),
    path('Launch_operation_attr/Add', launch_operation_attr.Launch_operation_attr_Add),
    path('Launch_operation_attr/Update', launch_operation_attr.Launch_operation_attr_Update),
    path('Launch_operation_attr/Remove', launch_operation_attr.Launch_operation_attr_Remove),
    path('Launch_operation_attr/Lookup/', launch_operation_attr.Launch_operation_attr_Lookup),
    path('Launch_operation_attr/Info/', launch_operation_attr.Launch_operation_attr_Info),
    path('Launch_operation_attr/Copy', launch_operation_attr.Launch_operation_attr_Copy),

]
