"""opstasks URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from django_opstasks.views import (
    dashboard_task_in_queues,
    dashboard_task_execution_trend,
    dashboard_queue_workers_in_queue,
    dashboard_queue_tasks_exe_count_in_queue,
)


urlpatterns = [
    path('dashboard/task/in_queues', dashboard_task_in_queues),
    path('dashboard/task/execution_trend', dashboard_task_execution_trend),
    path('dashboard/queue/workers_in_queue', dashboard_queue_workers_in_queue),
    path('dashboard/queue/tasks_exe_count_in_queue', dashboard_queue_tasks_exe_count_in_queue),
]
