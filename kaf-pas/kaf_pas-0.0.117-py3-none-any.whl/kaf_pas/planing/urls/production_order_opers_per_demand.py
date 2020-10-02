from django.urls import path

from kaf_pas.planing.views import production_order_opers_per_demand

urlpatterns = [
    path('Production_order_opers_per_demand/Fetch/', production_order_opers_per_demand.Production_order_opers_per_demand_Fetch),
]
