from django import template
from django.utils.html import mark_safe, format_html
from django.utils.translation import gettext as _

register = template.Library()

from boards.models import Task
from projects.models import Story

@register.filter
def task_style(task):
    category = None
    if task.task_type == Task.TASK_TYPE_EPIC:
        category = task.category
    elif task.task_type == Task.TASK_TYPE_STORY:
        if task.constraint:
            category = task.constraint.category
    else:
        raise ValueError("Invalid task type")

    if category:
        color = category.color
        return mark_safe(f"border-style: solid; border-color: { color }; border-width: 2px 2px 2px 8px;")
    return ""

@register.filter
def board_css_class(board, is_last):
    if board._max_columns == 1:
        return "col-md-12"
    elif board._max_columns == 2:
        return "col-md-6"
    elif board._max_columns == 3:
        return "col-md-4"
    elif board._max_columns == 4:
        return "col-md-3"
    elif board._max_columns == 5:
        if is_last:
            return "col-md-auto"
        return "col-md-2"
    elif board._max_columns == 6:
        return "col-md-2"


@register.filter
def task_priority(task):

    if task.priority == Story.PRIORITY_BLOCKER:
        css_class = "text-danger bi bi-exclamation-octagon-fill"

    elif task.priority == Story.PRIORITY_VERY_HIGH:
        css_class = "text-danger bi bi-chevron-double-up"

    elif task.priority == Story.PRIORITY_HIGH:
        css_class = "text-danger bi bi-chevron-up"

    elif task.priority == Story.PRIORITY_MEDIUM:
        css_class = "text-black bi bi-chevron-expand"

    elif task.priority == Story.PRIORITY_LOW:
        css_class = "taxt-info bi bi-chevron-down"

    elif task.priority == Story.PRIORITY_VERY_LOW:
        css_class = "text-info bi bi-chevron-double-down"

    elif task.priority == Story.PRIORITY_TRIVIAL:
        css_class = "text-info bi bi-circle"

    else:
        raise ValueError(f"Invalid priority: {task.priority}")

    return format_html('<i class="fs-3 align-middle {}" data-bs-toggle="tooltip" title="{}: {}"></i>', css_class, _("Priority"), task.get_priority_display())


@register.filter
def task_story_points(task):
    if task.task_type == Task.TASK_TYPE_STORY:
        story_points = task.story_points
    else:
        story_points = task.get_story_points()
    
    if story_points:
        return format_html('<span class="align-middle badge badge-pill bg-primary" data-bs-toggle="tooltip" title="{}">{}</span>', _("Story points"), story_points)
    return ''
