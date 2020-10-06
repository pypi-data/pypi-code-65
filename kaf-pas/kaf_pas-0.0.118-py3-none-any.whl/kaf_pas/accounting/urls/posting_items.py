from django.urls import path

from kaf_pas.accounting.views import posting_items

urlpatterns = [

    path('Posting/Fetch/', posting_items.Posting_Fetch),
    path('Posting/Fetch1/', posting_items.Posting_Fetch1),
    path('Posting_items/Fetch/', posting_items.Posting_items_Fetch),
    path('Posting_items/Add', posting_items.Posting_items_Add),
    path('Posting_items/Add1', posting_items.Posting_items_Add1),
    path('Posting_item/Add', posting_items.Posting_item_Add),
    path('Posting_items/Update', posting_items.Posting_items_Update),
    path('Posting_items/Remove', posting_items.Posting_items_Remove),
    path('Posting_items/Lookup/', posting_items.Posting_items_Lookup),
    path('Posting_items/Info/', posting_items.Posting_items_Info),
    path('Posting_items/Copy', posting_items.Posting_items_Copy),

]
