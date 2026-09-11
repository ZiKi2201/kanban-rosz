from django import template
from django.db.models import F, OuterRef, Q, Subquery

from board.models import Task, TaskChangeDismissal

register = template.Library()

RECENT_CHANGES_LIMIT = 10


@register.inclusion_tag('admin/recent_task_changes.html', takes_context=True)
def recent_task_changes(context):
    request = context['request']
    dismissed_value = TaskChangeDismissal.objects.filter(
        user=request.user, task=OuterRef('pk')
    ).values('dismissed_value')[:1]
    tasks = (
        Task.objects.visible_to(request.user)
        .filter(last_api_update__isnull=False)
        .annotate(dismissed_value=Subquery(dismissed_value))
        .filter(Q(dismissed_value__isnull=True) | ~Q(dismissed_value=F('last_api_update')))
        .order_by('-last_api_update')[:RECENT_CHANGES_LIMIT]
    )
    return {'recent_tasks': tasks}
