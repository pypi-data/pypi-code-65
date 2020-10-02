from django.urls import path

from kaf_pas.production.views import launch_detail

urlpatterns = [

    path('Launch_detail/Fetch/', launch_detail.Launch_detail_Fetch),
    path('Launch_detail/Add', launch_detail.Launch_detail_Add),
    path('Launch_detail/Update', launch_detail.Launch_detail_Update),
    path('Launch_detail/Remove', launch_detail.Launch_detail_Remove),
    path('Launch_detail/Lookup/', launch_detail.Launch_detail_Lookup),
    path('Launch_detail/Info/', launch_detail.Launch_detail_Info),
    path('Launch_detail/Copy', launch_detail.Launch_detail_Copy),

]
