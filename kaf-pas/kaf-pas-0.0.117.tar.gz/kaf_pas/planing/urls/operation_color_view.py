from django.urls import path

from kaf_pas.planing.views import operation_color_view

urlpatterns = [

    path('Operation_color_view/Fetch/', operation_color_view.Operation_color_view_Fetch),
    path('Operation_color_view/Add', operation_color_view.Operation_color_view_Add),
    path('Operation_color_view/Update', operation_color_view.Operation_color_view_Update),
    path('Operation_color_view/Remove', operation_color_view.Operation_color_view_Remove),
    path('Operation_color_view/Lookup/', operation_color_view.Operation_color_view_Lookup),
    path('Operation_color_view/Info/', operation_color_view.Operation_color_view_Info),
    path('Operation_color_view/Copy', operation_color_view.Operation_color_view_Copy),

]
