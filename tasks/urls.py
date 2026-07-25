from django.urls import path
from .views import (
    task_plan_list_create,
    delete_task_plan,
    update_session_status,
    log_session_pause,
)

urlpatterns = [
    path('plans/', task_plan_list_create, name='task_plans'),
    path('plans/<uuid:pk>/', delete_task_plan, name='delete_task_plan'),
    path('sessions/<uuid:pk>/status/', update_session_status, name='update_session_status'),
    path('sessions/<uuid:pk>/pause/', log_session_pause, name='log_session_pause'),
]