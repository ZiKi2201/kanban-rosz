from django.contrib import admin
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.urls import path
from django.utils.html import format_html
from .models import Task, TaskAttachment, TaskChangeDismissal


def is_viewonly_request(request):
    return request.GET.get('_viewonly') or request.POST.get('_viewonly')


class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 1
    fields = ('file', 'open_file', 'uploaded_at')
    readonly_fields = ('open_file', 'uploaded_at')

    def open_file(self, obj):
        if not obj.pk or not obj.file:
            return ''
        return format_html('<a href="{}" target="_blank" rel="noopener">Открыть</a>', obj.file.url)

    open_file.short_description = 'Просмотр'

    def has_add_permission(self, request, obj=None):
        if is_viewonly_request(request):
            return False
        return super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if is_viewonly_request(request):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if is_viewonly_request(request):
            return False
        return super().has_delete_permission(request, obj)


class TaskAdmin(admin.ModelAdmin):
    inlines = (TaskAttachmentInline,)
    list_display = (
        'task_link', 'get_owner', 'chief', 'boardName', 'date_end', 'date_update', 'date',
        'comment',
    )
    list_display_links = None
    exclude = ('last_api_update',)
    filter_horizontal = ('owner',)
    search_fields = ('name', 'owner__username', 'chief__username')

    def task_link(self, obj):
        return format_html('<a href="{}?_viewonly=1">{}</a>', f'{obj.pk}/change/', obj.name)

    task_link.short_description = 'Задача'
    task_link.admin_order_field = 'name'

    def has_change_permission(self, request, obj=None):
        if is_viewonly_request(request):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if is_viewonly_request(request):
            return False
        return super().has_delete_permission(request, obj)

    def get_changeform_initial_data(self, request):
        return {'chief': request.user.pk}

    def get_queryset(self, request):
        return super().get_queryset(request).visible_to(request.user)

    def get_urls(self):
        custom_urls = [
            path(
                '<uuid:task_id>/dismiss-recent-change/',
                self.admin_site.admin_view(self.dismiss_recent_change),
                name='board_task_dismiss_recent_change',
            ),
        ]
        return custom_urls + super().get_urls()

    def dismiss_recent_change(self, request, task_id):
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])
        task = get_object_or_404(self.get_queryset(request), pk=task_id)
        if task.last_api_update is not None:
            TaskChangeDismissal.objects.update_or_create(
                user=request.user, task=task,
                defaults={'dismissed_value': task.last_api_update},
            )
        return redirect('admin:index')

    def get_owner(self, obj):
        return ', '.join([owner.username for owner in obj.owner.all()])

    get_owner.short_description = 'Исполнители'


admin.site.register(Task, TaskAdmin)

admin.site.site_header = 'ГБУ РО «Ростовоблстройзаказчик»'

admin.site.site_title = 'ГБУ РО «Ростовоблстройзаказчик»'
