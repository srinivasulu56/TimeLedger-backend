from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import TaskPlan, FocusSession, PauseLog
from .serializers import TaskPlanSerializer, FocusSessionSerializer, PauseLogSerializer

# --- Task Plan Endpoints ---
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def task_plan_list_create(request):
    if request.method == 'GET':
        tasks = TaskPlan.objects.filter(user=request.user)
        serializer = TaskPlanSerializer(tasks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        title = request.data.get('title')
        category = request.data.get('category', 'Development')
        estimated_minutes = request.data.get('estimated_minutes', 120)
        session_duration = request.data.get('session_duration', 45)
        
        # 1. Accept either 'subtasks' OR 'sessions' from request payload
        raw_subtasks = request.data.get('subtasks') or request.data.get('sessions') or []

        task = TaskPlan.objects.create(
            user=request.user,
            title=title,
            category=category,
            estimated_minutes=estimated_minutes,
            session_duration=session_duration
        )

        # 2. Auto-generate child FocusSession records in PostgreSQL
        for index, item in enumerate(raw_subtasks):
            if isinstance(item, dict):
                topic = item.get('topic', f'Session {index + 1}')
                planned_duration = item.get('planned_duration') or item.get('plannedDuration') or session_duration
            else:
                topic = str(item)
                planned_duration = session_duration

            FocusSession.objects.create(
                task_plan=task,
                order=index + 1,
                topic=topic,
                planned_duration=planned_duration,
                status='planned'
            )

        serializer = TaskPlanSerializer(task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_task_plan(request, pk):
    try:
        task = TaskPlan.objects.get(id=pk, user=request.user)
        task.delete()
        return Response({'message': 'Task plan deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except TaskPlan.DoesNotExist:
        return Response({'error': 'Task plan not found'}, status=status.HTTP_404_NOT_FOUND)


# --- Focus Session & Telemetry Endpoints ---
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_session_status(request, pk):
    try:
        session = FocusSession.objects.get(id=pk, task_plan__user=request.user)
        status_val = request.data.get('status')
        actual_duration = request.data.get('actual_duration')

        if status_val:
            session.status = status_val
        if actual_duration is not None:
            session.actual_duration = actual_duration

        session.save()
        serializer = FocusSessionSerializer(session)
        return Response(serializer.data)
    except FocusSession.DoesNotExist:
        return Response({'error': 'Focus session not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_session_pause(request, pk):
    try:
        session = FocusSession.objects.get(id=pk, task_plan__user=request.user)
        reason_category = request.data.get('reason_category', 'Other Reason')
        custom_note = request.data.get('custom_note', '')
        pause_duration_minutes = request.data.get('pause_duration_minutes', 1)

        pause_log = PauseLog.objects.create(
            session=session,
            reason_category=reason_category,
            custom_note=custom_note,
            pause_duration_minutes=pause_duration_minutes
        )

        serializer = PauseLogSerializer(pause_log)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except FocusSession.DoesNotExist:
        return Response({'error': 'Focus session not found'}, status=status.HTTP_404_NOT_FOUND)