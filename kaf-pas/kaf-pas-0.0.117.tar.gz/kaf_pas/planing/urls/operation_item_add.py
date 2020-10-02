from django.urls import path

from kaf_pas.planing.views import operation_item_add

urlpatterns = [

    path('Operation_item_add/Fetch/', operation_item_add.Operation_item_add_Fetch),
    path('Operation_item_add/Add', operation_item_add.Operation_item_add_Add),
    path('Operation_item_add/Update', operation_item_add.Operation_item_add_Update),
    path('Operation_item_add/Remove', operation_item_add.Operation_item_add_Remove),
    path('Operation_item_add/Lookup/', operation_item_add.Operation_item_add_Lookup),
    path('Operation_item_add/Info/', operation_item_add.Operation_item_add_Info),
    path('Operation_item_add/Copy', operation_item_add.Operation_item_add_Copy),

]
