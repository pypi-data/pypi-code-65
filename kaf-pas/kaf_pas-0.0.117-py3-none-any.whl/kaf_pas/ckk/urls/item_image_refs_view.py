from django.urls import path

from kaf_pas.ckk.views import item_image_refs_view

urlpatterns = [

    path('Item_image_refs_view/Fetch/', item_image_refs_view.Item_image_refs_view_Fetch),
    path('Item_image_refs_view/Add', item_image_refs_view.Item_image_refs_view_Add),
    path('Item_image_refs_view/Update', item_image_refs_view.Item_image_refs_view_Update),
    path('Item_image_refs_view/Remove', item_image_refs_view.Item_image_refs_view_Remove),
    path('Item_image_refs_view/Lookup/', item_image_refs_view.Item_image_refs_view_Lookup),
    path('Item_image_refs_view/Info/', item_image_refs_view.Item_image_refs_view_Info),
    path('Item_image_refs_view/Copy', item_image_refs_view.Item_image_refs_view_Copy),

]
