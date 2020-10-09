
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django_eveonline_connector.models import EveCharacter
from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required, login_required
from django.apps import apps
from django.conf import settings
from django_eveonline_doctrine_manager.models import EveFitting, EveDoctrine
from django.http import JsonResponse
import logging
import time


logger = logging.getLogger(__name__)


@login_required
@permission_required('django_eveonline_doctrine_manager.view_evedoctrine', raise_exception=True)
def view_doctrines(request):
    context = {}
    context['doctrines'] = EveDoctrine.objects.all()

    return render(request, 'django_eveonline_doctrine_manager/adminlte/doctrines.html', context)


@login_required
@permission_required('django_eveonline_doctrine_manager.view_evedoctrine', raise_exception=True)
def view_doctrine(request, doctrine_id):
    context = {}
    context['doctrine'] = EveDoctrine.objects.get(pk=doctrine_id)
    return render(request, 'django_eveonline_doctrine_manager/adminlte/view_doctrine.html', context)


@login_required
@permission_required('django_eveonline_doctrine_manager.view_evefitting', raise_exception=True)
def view_fittings(request):
    context = {}
    context['fittings'] = EveFitting.objects.all()
    return render(request, 'django_eveonline_doctrine_manager/adminlte/fittings.html', context)


@login_required
@permission_required('django_eveonline_doctrine_manager.view_evefitting', raise_exception=True)
def fittings_skill_check(request):
    if 'external_id' not in request.GET:
        return HttpResponse(status=400)
    if 'fitting_id' not in request.GET:
        return HttpResponse(status=400)
    if 'django_eveonline_entity_extensions' not in settings.INSTALLED_APPS:
        return HttpResponse(status=404)
    from django_eveonline_entity_extensions.models import EveSkill
    import roman
    eve_character = EveCharacter.objects.get(
        external_id=request.GET['external_id'])
    fitting = EveFitting.objects.get(pk=request.GET['fitting_id'])
    minimum_skills = fitting.skillplan.minimum_skills.split("\n")
    effective_skills = fitting.skillplan.effective_skills.split("\n")
    response = {}
    response['minimum_skills'] = []
    response['effective_skills'] = []
    for skill in minimum_skills:
        skill_name = " ".join(skill.split(" ")[:-1])
        skill_level = roman.fromRoman(
            "".join(skill.split(" ")[-1:]).rstrip("\n\r"))

        if EveSkill.objects.filter(name=skill_name, level__gte=skill_level, entity=eve_character).exists():
            pass
        else:
            response['minimum_skills'].append(skill)

    for skill in effective_skills:
        skill_name = " ".join(skill.split(" ")[:-1])
        skill_level = roman.fromRoman(
            "".join(skill.split(" ")[-1:]).rstrip("\n\r"))

        if EveSkill.objects.filter(name=skill_name, level__gte=skill_level, entity=eve_character).exists():
            pass
        else:
            response['effective_skills'].append(skill)

    return JsonResponse(response)


