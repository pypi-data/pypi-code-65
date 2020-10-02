from django.urls import path

from kaf_pas.planing.views import operation_launch_item

urlpatterns = [

    path('Operation_launch_item/Fetch/', operation_launch_item.Operation_launch_item_Fetch),
    path('Operation_launch_item/Add', operation_launch_item.Operation_launch_item_Add),
    path('Operation_launch_item/Update', operation_launch_item.Operation_launch_item_Update),
    path('Operation_launch_item/Remove', operation_launch_item.Operation_launch_item_Remove),
    path('Operation_launch_item/Lookup/', operation_launch_item.Operation_launch_item_Lookup),
    path('Operation_launch_item/Info/', operation_launch_item.Operation_launch_item_Info),
    path('Operation_launch_item/Copy', operation_launch_item.Operation_launch_item_Copy),

]
