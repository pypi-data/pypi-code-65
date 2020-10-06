from django.urls import path

from kaf_pas.ckk.views import item_history

urlpatterns = [

    path('Item_history/Fetch/', item_history.Item_history_Fetch),
    path('Item_history/Add', item_history.Item_history_Add),
    path('Item_history/Update', item_history.Item_history_Update),
    path('Item_history/Remove', item_history.Item_history_Remove),
    path('Item_history/Lookup/', item_history.Item_history_Lookup),
    path('Item_history/Info/', item_history.Item_history_Info),
    path('Item_history/Copy', item_history.Item_history_Copy),

]
