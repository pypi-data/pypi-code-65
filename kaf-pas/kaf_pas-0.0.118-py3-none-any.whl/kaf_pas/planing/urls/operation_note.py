from django.urls import path

from kaf_pas.planing.views import operation_note

urlpatterns = [

    path('Operation_note/Fetch/', operation_note.Operation_note_Fetch),
    path('Operation_note/Add', operation_note.Operation_note_Add),
    path('Operation_note/Update', operation_note.Operation_note_Update),
    path('Operation_note/Remove', operation_note.Operation_note_Remove),
    path('Operation_note/Lookup/', operation_note.Operation_note_Lookup),
    path('Operation_note/Info/', operation_note.Operation_note_Info),
    path('Operation_note/Copy', operation_note.Operation_note_Copy),

]
