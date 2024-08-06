from django import template
from django.utils.html import format_html
from django.utils.html import mark_safe

register = template.Library()

from ..models import Constraint

@register.filter
def constraint_status(constraint):
    status = constraint.get_status_display()
    css_class = ''
    if constraint.status in [Constraint.STATUS_NEW, Constraint.STATUS_IMPLEMENTED, Constraint.STATUS_NON_COMPLIANT]:
        css_class = mark_safe('text-warning bi bi-question-diamond-fill fs-3')
    elif constraint.status in [Constraint.STATUS_FAILED]:
        css_class = mark_safe('text-danger bi bi-exclamation-octagon-fill fs-3')
    elif constraint.status in [Constraint.STATUS_COMPLIANT]:
        css_class = mark_safe('text-success bi bi-check-circle-fill fs-3')
    else:
        return ''
    return format_html('<i class="{}" data-bs-toggle="tooltip" data-bs-placement="right" title="{}"></i>', css_class, status)
