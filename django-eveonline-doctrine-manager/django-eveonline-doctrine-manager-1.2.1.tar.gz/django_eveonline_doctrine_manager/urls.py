from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django_eveonline_doctrine_manager.views import old as views
from django_eveonline_doctrine_manager.views import api, doctrines, fittings, skillplans

urlpatterns = []

urlpatterns += [
    path('api/skillcheck', api.skillcheck_utility, 
        name='django-eveonline-doctrine-manager-api-skillcheck'),
    path('api/hangarcheck', api.hangarcheck_utility, 
         name='django-eveonline-doctrine-manager-api-hangarcheck'),
    path('api/fitting', api.get_fitting, 
         name='django-eveonline-doctrine-manager-api-get-fitting'),
    path('api/characters/shipaudit', api.ship_audit,
        name='django-eveonline-doctrine-manager-api-shipaudit'),
]

# Doctrines
urlpatterns += [
    path('doctrines/create/', doctrines.DoctrineCreateView.as_view(),
         name="django-eveonline-doctrine-manager-doctrines-create"),
    path('doctrines/', doctrines.DoctrineListView.as_view(),
         name="django-eveonline-doctrine-manager-doctrines-list"),
    path('doctrines/view/<int:id>/', doctrines.DoctrineDetailView.as_view(),
         name="django-eveonline-doctrine-manager-doctrines-detail"),
    path('doctrines/view/<int:id>/audit/', doctrines.DoctrineAuditView.as_view(),
         name="django-eveonline-doctrine-manager-doctrines-audit"),
    path('doctrines/update/<int:id>/', doctrines.DoctrineUpdateView.as_view(),
         name="django-eveonline-doctrine-manager-doctrines-update"),
    path('doctrines/delete/<int:id>/', doctrines.DoctrineDeleteView.as_view(),
         name="django-eveonline-doctrine-manager-doctrines-delete"),
]

# Fittings
urlpatterns += [
    path('fittings/create', fittings.FittingCreateView.as_view(),
         name="django-eveonline-doctrine-manager-fittings-create"),
    path('fittings', fittings.FittingListView.as_view(),
         name="django-eveonline-doctrine-manager-fittings-list"),
    path('fittings/view/<int:id>', fittings.FittingDetailView.as_view(),
         name="django-eveonline-doctrine-manager-fittings-detail"),
    path('fittings/view/<int:id>/audit/', fittings.FittingAuditView.as_view(),
         name="django-eveonline-doctrine-manager-fittings-audit"),
    path('fittings/update/<int:id>', fittings.FittingUpdateView.as_view(),
         name="django-eveonline-doctrine-manager-fittings-update"),
    path('fittings/delete/<int:id>', fittings.FittingDeleteView.as_view(),
         name="django-eveonline-doctrine-manager-fittings-delete"),
    path('api/fittings/skillcheck', views.fittings_skill_check,
         name="django-eveonline-doctrine-manager-fittings-skill-check")
]

# Skillplans
urlpatterns += [
    path('skillplans/create', skillplans.SkillPlanCreateView.as_view(),
         name="django-eveonline-doctrine-manager-skillplans-create"),
    path('skillplans', skillplans.SkillPlanListView.as_view(),
         name="django-eveonline-doctrine-manager-skillplans-list"),
    path('skillplans/view/<int:id>', skillplans.SkillPlanDetailView.as_view(),
         name="django-eveonline-doctrine-manager-skillplans-detail"),
    path('skillplans/update/<int:id>', skillplans.SkillPlanUpdateView.as_view(),
         name="django-eveonline-doctrine-manager-skillplans-update"),
    path('skillplans/delete/<int:id>', skillplans.SkillPlanDeleteView.as_view(),
         name="django-eveonline-doctrine-manager-skillplans-delete"),
]

# SRP
urlpatterns += [

]

# Seeding 
urlpatterns += [

]
