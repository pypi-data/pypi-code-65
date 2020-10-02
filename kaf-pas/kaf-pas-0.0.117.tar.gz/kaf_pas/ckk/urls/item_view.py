from django.urls import path

from kaf_pas.ckk.views import item_view

urlpatterns = [

    path('ItemView/Fetch/', item_view.Item_view_Fetch),
    path('ItemView_Variants/Fetch/', item_view.Item_view_Variants_Fetch),
    path('Item_view_Teach/Fetch/', item_view.Item_view_Teach_Fetch),
    path('ItemView_4_id/Fetch/', item_view.Item_view_4_idFetch),
    path('ItemView/Fetch1/', item_view.Item_view_Fetch1),
    path('ItemView/Fetch2/', item_view.Item_view_Fetch2),
    path('ItemView/Fetch3/', item_view.Item_view_Fetch3),
    path('ItemView/Fetch4/', item_view.Item_view_Fetch4),
    path('ItemView/Fetch5/', item_view.Item_view_Fetch5),
    path('ItemView/Add', item_view.Item_view_Add),
    path('ItemView/Update', item_view.Item_view_Update),
    path('ItemView/Update1', item_view.Item_view_Update1),
    path('ItemView/Remove', item_view.Item_view_Remove),
    path('ItemView/Lookup/', item_view.Item_view_Lookup),
    path('ItemView/Info/', item_view.Item_view_Info),
    path('ItemView/Copy', item_view.Item_view_Copy),
    path('ItemView/CopyItems', item_view.copyItems),
    path('ItemView/CombineItems', item_view.combineItems),
    path('ItemView/CopyBlockItems', item_view.Item_view_CopyBlockItems),

]
