from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import EveTimerForm
from .models import EveTimer, EveTimerType
from datetime import datetime, timedelta 
from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required

@login_required
@permission_required('django_eveonline_timerboard.add_evetimer', raise_exception=True)
def add_timer(request):
    if request.method == "POST":
        form = EveTimerForm(request.POST)

        if form.is_valid():
            EveTimer(
                name=form.cleaned_data['name'],
                timer=datetime.utcnow() + timedelta(days=form.cleaned_data['days'], hours=form.cleaned_data['hours'], minutes=form.cleaned_data['minutes'], seconds=form.cleaned_data['seconds']),
                type=form.cleaned_data.get('type'),
                location=form.cleaned_data['location'],
                user=request.user,
            ).save()
            messages.success(request, 'Succesfully added timer: %s' % form.cleaned_data['name'])
            return redirect('django-eveonline-timerboard-view')
        else:
            messages.error(request, 'Failed to add timer: %s' % str(form.errors.as_text))
            return redirect('django-eveonline-timerboard-view')


@login_required
@permission_required('django_eveonline_timerboard.delete_evetimer', raise_exception=True)
def remove_timer(request, pk):
    EveTimer.objects.get(pk=pk).delete()
    return redirect('django-eveonline-timerboard-view')
      

@login_required
@permission_required('django_eveonline_timerboard.view_evetimer', raise_exception=True)
def view_timerboard(request):
    timers = EveTimer.objects.filter(timer__gte=timezone.now())
    context = {
        'timers': timers,
        'types': EveTimerType.objects.all(),
        'form': EveTimerForm()
    }
    return render(request, 'django_eveonline_timerboard/adminlte/timerboard.html', context)