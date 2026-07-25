from django.contrib import admin
from .models import TaskPlan, FocusSession, PauseLog

admin.site.register(TaskPlan)
admin.site.register(FocusSession)
admin.site.register(PauseLog)