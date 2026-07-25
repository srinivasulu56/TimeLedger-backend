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
    # 1. Remove read_only=True and set required=False so DRF accepts incoming session arrays
    sessions = FocusSessionSerializer(many=True, required=False)

    class Meta:
        model = TaskPlan
        fields = ['id', 'title', 'category', 'estimated_minutes', 'session_duration', 'created_at', 'sessions']
        read_only_fields = ['user', 'created_at']

    # 2. Override create() to save both TaskPlan and its nested FocusSessions into PostgreSQL
    def create(self, validated_data):
        sessions_data = validated_data.pop('sessions', [])
        
        # Create parent TaskPlan instance
        task_plan = TaskPlan.objects.create(**validated_data)
        
        # Create each nested FocusSession tied to the newly created task_plan
        for session_data in sessions_data:
            FocusSession.objects.create(task_plan=task_plan, **session_data)
            
        return task_plan