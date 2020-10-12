from django.http import JsonResponse
from django.shortcuts import render

from emp_ide import models
from emp_ide.decorators import visit_record


@visit_record
def index(request):
    return render(request, 'index.html')


@visit_record
def post_esp_ip(request):
    try:
        espip = models.MpyMachine.objects.get(ip=request.META.get("REMOTE_ADDR"))
        if espip:
            espip.set_esp_ip(request.GET.get('esp_ip', ''))
            rsp = dict(code=0, message='esp ip added to exist record.')

    except:
        espip = models.MpyMachine(
            ip=request.META.get("REMOTE_ADDR"),
            esp_ip=request.GET.get('esp_ip', ''))
        rsp = dict(code=0, message='new esp ip added.')

    finally:
        espip.save()

    return JsonResponse(rsp)


def get_esp_ip(request):
    try:
        esp_ip = models.MpyMachine.objects.get(ip=request.META.get("REMOTE_ADDR"))
        rsp = dict(code=0, ip=esp_ip.get_esp_ip())
    except:
        rsp = dict(code=-1, ip=[])

    return JsonResponse(rsp)
