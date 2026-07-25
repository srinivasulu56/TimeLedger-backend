import uuid
from django.db import models
from django.contrib.auth.models import User

class TaskPlan(models.Model):
    CATEGORY_CHOICES = [
        ('Development', 'Development'),
        ('Design', 'Design'),
        ('Research', 'Research'),
        ('Writing', 'Writing'),
        ('Other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_plans')
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Development')
    estimated_minutes = models.IntegerField()
    session_duration = models.IntegerField(default=45)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.user.username})"


class FocusSession(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_plan = models.ForeignKey(TaskPlan, on_delete=models.CASCADE, related_name='sessions')
    order = models.IntegerField()
    topic = models.CharField(max_length=255)
    planned_duration = models.IntegerField()  # in minutes
    actual_duration = models.IntegerField(null=True, blank=True)  # in minutes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    is_carryover = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.task_plan.title} - Session #{self.order}: {self.topic}"


class PauseLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(FocusSession, on_delete=models.CASCADE, related_name='pause_logs')
    reason_category = models.CharField(max_length=100)
    custom_note = models.TextField(blank=True, default="")
    pause_duration_minutes = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pause ({self.reason_category}) - Session #{self.session.order}"