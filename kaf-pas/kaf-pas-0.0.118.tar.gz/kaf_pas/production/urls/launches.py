from django.urls import path

from kaf_pas.production.views import launches

urlpatterns = [

    path('Launches/Fetch/', launches.Launches_Fetch),
    path('Launches/Fetch_4_Production_values/', launches.Launches_Fetch_4_Production_values),
    path('Launches/Planing_Fetch/', launches.Launches_Planing_Fetch),
    path('Launches/Fetch1/', launches.Launches_Fetch1),
    path('Launches/Add', launches.Launches_Add),
    path('Launches/Update', launches.Launches_Update),
    path('Launches/Remove', launches.Launches_Remove),
    path('Launches/Lookup/', launches.Launches_Lookup),
    path('Launches/Info/', launches.Launches_Info),
    path('Launches/Copy', launches.Launches_Copy),
    path('Launches/GetQtyChilds/', launches.GetQtyChilds),

]
