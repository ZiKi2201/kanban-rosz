from api.serializers import TaskAttachmentSerializer, TaskSerializer

from board.models import Task, TaskAttachment

from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated


class ListTask(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(owner=user)

    def perform_create(self, serializer):
        task = serializer.save()
        task.owner.set([self.request.user])


class DetailTask(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(owner=user)

    def perform_update(self, serializer):
        serializer.save(last_api_update=timezone.now())


class ListTaskAttachment(generics.ListCreateAPIView):
    serializer_class = TaskAttachmentSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_task(self):
        return get_object_or_404(Task, pk=self.kwargs['task_pk'], owner=self.request.user)

    def get_queryset(self):
        return TaskAttachment.objects.filter(task=self.get_task())

    def perform_create(self, serializer):
        task = self.get_task()
        serializer.save(task=task)
        task.last_api_update = timezone.now()
        task.save(update_fields=['last_api_update'])


class DetailTaskAttachment(generics.DestroyAPIView):
    serializer_class = TaskAttachmentSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TaskAttachment.objects.filter(task__owner=self.request.user)

    def perform_destroy(self, instance):
        task = instance.task
        instance.delete()
        task.last_api_update = timezone.now()
        task.save(update_fields=['last_api_update'])
