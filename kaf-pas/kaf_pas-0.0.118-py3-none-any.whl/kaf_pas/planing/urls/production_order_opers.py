from django.urls import path

from kaf_pas.planing.views import production_order_opers

urlpatterns = [

    path('Production_order_opers/Fetch/', production_order_opers.Production_order_opers_Fetch),
    path('Production_order_opers/FetchPerLaunch/', production_order_opers.Production_order_per_launch_FetchDetail),
    path('Production_order_opers/Add', production_order_opers.Production_order_opers_Add),
    path('Production_order_opers/Update', production_order_opers.Production_order_opers_Update),
    path('Production_order_opers/Remove', production_order_opers.Production_order_opers_Remove),
    path('Production_order_opers/Lookup/', production_order_opers.Production_order_opers_Lookup),
    path('Production_order_opers/Info/', production_order_opers.Production_order_opers_Info),
    path('Production_order_opers/Copy', production_order_opers.Production_order_opers_Copy),

]
