from django.urls import path

from kaf_pas.production.views import operations

urlpatterns = [

    path('Operations/Fetch/', operations.Operations_Fetch),
    path('Operations/Ext_Fetch/', operations.Operations_Ext_Fetch),
    path('Operations/Add', operations.Operations_Add),
    path('Operations/Copy', operations.Operations_Copy),
    path('Operations/Update', operations.Operations_Update),
    path('Operations/Remove', operations.Operations_Remove),
    path('Operations/Lookup/', operations.Operations_Lookup),
    path('Operations/Info/', operations.Operations_Info),

]
