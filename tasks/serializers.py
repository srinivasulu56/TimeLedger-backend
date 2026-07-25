from rest_framework import serializers
from .models import TaskPlan, FocusSession, PauseLog

class PauseLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PauseLog
        fields = ['id', 'reason_category', 'custom_note', 'pause_duration_minutes', 'timestamp']


class FocusSessionSerializer(serializers.ModelSerializer):
    pause_logs = PauseLogSerializer(many=True, read_only=True)

    class Meta:
        model = FocusSession
        fields = ['id', 'order', 'topic', 'planned_duration', 'actual_duration', 'status', 'is_carryover', 'pause_logs']


class TaskPlanSerializer(serializers.ModelSerializer):
    sessions = FocusSessionSerializer(many=True, read_only=True)

    class Meta:
        model = TaskPlan
        fields = ['id', 'title', 'category', 'estimated_minutes', 'session_duration', 'created_at', 'sessions']
        read_only_fields = ['user']