from board.models import Task, TaskAttachment

from django.contrib.auth.models import User

from rest_framework import serializers


class TaskAttachmentSerializer(serializers.ModelSerializer):
    url = serializers.FileField(source='file', use_url=True, read_only=True)

    class Meta:
        model = TaskAttachment
        fields = ('id', 'task', 'file', 'url', 'original_filename', 'uploaded_at')
        read_only_fields = ('original_filename', 'uploaded_at')
        extra_kwargs = {
            'file': {'write_only': True},
            'task': {'write_only': True, 'required': False},
        }


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    attachments = TaskAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = (
            'uuid', 'name', 'boardName', 'date', 'owner', 'date_update', 'date_end', 'chief',
            'comment', 'attachments',
        )


class UserSerializer(serializers.ModelSerializer):
    tasks = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'tasks']
