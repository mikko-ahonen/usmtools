from django import template
from django.utils.html import mark_safe

register = template.Library()

from boards.models import Task

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
