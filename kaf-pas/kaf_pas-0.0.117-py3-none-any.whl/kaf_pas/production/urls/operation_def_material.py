from django.urls import path

from kaf_pas.production.views import operation_def_material

urlpatterns = [

    path('Operation_def_material/Fetch/', operation_def_material.Operation_def_material_Fetch),
    path('Operation_def_material/Add', operation_def_material.Operation_def_material_Add),
    path('Operation_def_material/Update', operation_def_material.Operation_def_material_Update),
    path('Operation_def_material/Remove', operation_def_material.Operation_def_material_Remove),
    path('Operation_def_material/Lookup/', operation_def_material.Operation_def_material_Lookup),
    path('Operation_def_material/Info/', operation_def_material.Operation_def_material_Info),
    path('Operation_def_material/Copy', operation_def_material.Operation_def_material_Copy),

]
