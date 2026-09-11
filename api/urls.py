from api.views import DetailTask, DetailTaskAttachment, ListTask, ListTaskAttachment

from django.urls import path

urlpatterns = [
    path('tasks/', ListTask.as_view()),
    path('task/<str:pk>', DetailTask.as_view()),
    path('task/<str:task_pk>/attachments/', ListTaskAttachment.as_view()),
    path('attachment/<int:pk>', DetailTaskAttachment.as_view()),
]
