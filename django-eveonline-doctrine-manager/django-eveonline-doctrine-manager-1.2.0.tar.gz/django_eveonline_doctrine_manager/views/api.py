from django.db import models
from django.apps import apps
from django_eveonline_connector.models import EveAsset
from django_eveonline_doctrine_manager.utilities.abstractions import EveSkillList
from django_eveonline_doctrine_manager.models import EveFitting, EveSkillPlan, EveDoctrineSettings, EveDoctrine
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import permission_required, login_required
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_page
import json, logging 


@permission_required('django_eveonline_doctrine_manager.view_evefitting', raise_exception=True)
@cache_page(60 * 15)
def skillcheck_utility(request):
    external_id = None 
    fitting = None 
    doctrine = None 
    skillplan = None 
    if 'external_id' not in request.GET:
        return HttpResponse(status=400)
    else:
        external_id = request.GET['external_id']
    if 'fitting_id' in request.GET:
        fitting = EveFitting.objects.get(pk=request.GET['fitting_id'])
    elif 'doctrine_id' in request.GET:
        doctrine = EveDoctrine.objects.get(pk=request.GET['doctrine_id'])
    elif 'skillplan_id' in request.GET:
        skillplan = EveSkillPlan.objects.get(pk=request.GET['skillplan_id'])
    else:
        return HttpResponse(status=400)

    if fitting:
        missing_skills = fitting.get_required_skills().get_missing_skills(external_id)
        if missing_skills:
            return JsonResponse({
                'missing_skills': missing_skills
            }, status=200)
        else:
            return HttpResponse(status=204)
    elif skillplan:
        missing_skills = skillplan.get_required_skills().get_missing_skills(external_id)
        if missing_skills:
            return JsonResponse({
                'missing_skills': missing_skills
            }, status=200)
        else:
            return HttpResponse(status=204)
    else:
        available_fittings = []
        for fitting in doctrine.fittings:
            if not fitting.get_required_skills().get_missing_skills(external_id):
                available_fittings.append(fitting.pk)
        if len(available_fittings) > 0:
            return JsonResponse({
                'ships': available_fittings
                }, status=200)
        else:
            return HttpResponse(status=204)


@permission_required('django_eveonline_connector.view_eveasset', raise_exception=True)
@cache_page(60 * 15)
def hangarcheck_utility(request):
    if 'external_id' not in request.GET:
        return HttpResponse(status=400)
    if not EveDoctrineSettings.get_instance().staging_structure:
        return HttpResponse(status=500)
    else:
        location_id = EveDoctrineSettings.get_instance().staging_structure.structure_id
    if 'fitting_id' in request.GET:
        fitting = EveFitting.objects.get(pk=request.GET['fitting_id'])
        if EveAsset.objects.filter(type_id=fitting.ship_id, location_id=location_id, entity__external_id=request.GET['external_id']).exists():
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=404)
    if 'doctrine_id' in request.GET:
        doctrine = EveDoctrine.objects.get(pk=request.GET['doctrine_id'])
        type_ids = [fitting.ship_id for fitting in doctrine.fittings]
        if EveAsset.objects.filter(type_id__in=type_ids, location_id=location_id, entity__external_id=request.GET['external_id']).exists():
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=404)


@permission_required('django_eveonline_doctrine_manager.view_evefitting', raise_exception=True)
def get_fitting(request):
    if 'fitting_id' not in request.GET:
        return HttpResponse(status=400)
    fitting = EveFitting.objects.get(pk=request.GET['fitting_id']).parse_fitting()
    return JsonResponse(fitting)


@permission_required('django_eveonline_connector.view_evecharacter', raise_exception=True)
@permission_required('django_eveonline_doctrine_manager.view_evefitting', raise_exception=True)
@permission_required('django_eveonline_doctrine_manager.view_evedoctrine', raise_exception=True)
def ship_audit(request):
    if 'external_id' not in request.GET:
        return HttpResponse(status=400)
    else:
        external_id = request.GET['external_id']
    
    response = {
        'doctrines': [],
        'fittings': [],
        'skillplans': []
    }

    for doctrine in EveDoctrine.objects.all():
        available_fittings = []
        missing_fittings = []
        for fitting in doctrine.fittings:
            missing_skills = fitting.get_required_skills().get_missing_skills(external_id)
            if not missing_skills:
                response['fittings'].append({
                    'name': fitting.name,
                    'type_id': fitting.ship_id,
                    'can_fly': True
                })
                available_fittings.append({
                    'name': fitting.name,
                    'type_id': fitting.ship_id,
                })
            else:
                response['fittings'].append({
                    'name': fitting.name,
                    'type_id': fitting.ship_id,
                    'can_fly': False
                })
                missing_fittings.append({
                    'name': fitting.name,
                    'type_id': fitting.ship_id,
                })
                    
        if available_fittings:
            response['doctrines'].append({
                'name': doctrine.name,
                'fittings': available_fittings,
                'can_fly': True,
            })
        else:
           response['doctrines'].append({
               'name': doctrine.name,
               'fittings': available_fittings,
               'can_fly': False,
           })



    for skillplan in EveSkillPlan.objects.all():
        missing_skills = skillplan.get_required_skills().get_missing_skills(external_id)
        if missing_skills:
            response['skillplans'].append({
                'name': skillplan.name, 
                'trained': False,
                'missing_skills': [skill for skill in missing_skills ]
            })
        else:
            response['skillplans'].append({
                'name': skillplan.name, 
                'trained': True 
            })
    
    return JsonResponse(response)
