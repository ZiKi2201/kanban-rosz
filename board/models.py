import os
import uuid

from django.contrib import auth
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

MAX_ATTACHMENT_SIZE = 20 * 1024 * 1024


def validate_attachment_size(file):
    if file.size > MAX_ATTACHMENT_SIZE:
        raise ValidationError('Размер файла не должен превышать 20 МБ.')


def attachment_upload_path(instance, filename):
    return os.path.join('attachments', str(instance.task_id), filename)


class TaskQuerySet(models.QuerySet):
    def visible_to(self, user):
        if user.is_superuser:
            return self
        return self.filter(models.Q(chief=user) | models.Q(owner=user)).distinct()


class Task(models.Model):
    class boardNames(models.TextChoices):
        ToDo = 'Сделать', _('Сделать')
        InProgress = 'В процессе', _('В процессе')
        Review = 'На проверке', _('На проверке')
        Done = 'Выполнено', _('Выполнено')
    chief = models.ForeignKey('auth.User', on_delete=models.RESTRICT, null=True,
                         verbose_name='Руководитель', related_name='chief')
    owner = models.ManyToManyField('auth.User',
                                   related_name='tasks', verbose_name='Исполнители',)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True,
                            editable=False)
    name = models.TextField(max_length=500, verbose_name='Задача')
    boardName = models.CharField(max_length=12, choices=boardNames.choices,
                                 default=boardNames.ToDo, verbose_name='Статус')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания',)
    date_end = models.DateTimeField(verbose_name='Крайний срок выполнения', null=True,)
    date_update = models.DateTimeField(verbose_name='Дата изменения', auto_now=True, null=True,)
    comment = models.TextField(max_length=500, verbose_name='Комментарий', null=True, blank=True)
    last_api_update = models.DateTimeField(verbose_name='Последнее изменение через фронтенд',
                                           null=True, blank=True)

    objects = TaskQuerySet.as_manager()

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return str(self.name)


class TaskAttachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE,
                             related_name='attachments', verbose_name='Задача')
    file = models.FileField(upload_to=attachment_upload_path,
                            validators=[validate_attachment_size],
                            verbose_name='Файл')
    original_filename = models.CharField(max_length=255, verbose_name='Имя файла', blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')

    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'

    def __str__(self):
        return self.original_filename

    def save(self, *args, **kwargs):
        if self.file and not self.original_filename:
            self.original_filename = os.path.basename(self.file.name)
        super().save(*args, **kwargs)


@receiver(post_delete, sender=TaskAttachment)
def delete_attachment_file(sender, instance, **kwargs):
    instance.file.delete(save=False)


class TaskChangeDismissal(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE,
                             related_name='dismissed_task_changes')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='dismissals')
    dismissed_value = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'task'], name='unique_task_dismissal_per_user'),
        ]
