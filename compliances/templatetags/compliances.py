from django import template
from django.utils.html import mark_safe
from django.utils.html import format_html

register = template.Library()

from projects.models import Story
from ..models import TargetSection, Constraint


@register.filter
def target_section_checked(target, section):
    qs = TargetSection.objects.filter(target_id=target.id, section_id=section.id)
    if qs.exists():
        return 'checked'
    return ''


@register.filter
def team_category_checked(team, category):
    if category.team_id == team.id:
        return 'checked'
    return ''


def constraint_status_css_class(status):

    if not status:
        return ""

    if status == Constraint.STATUS_AUDITED:
        css_class = mark_safe('text-success bi bi-check-circle-fill fs-5')
    elif status in [Constraint.STATUS_ONGOING, Constraint.STATUS_COMPLIANT, Constraint.STATUS_IMPLEMENTED]:
        css_class = mark_safe('text-primary bi bi-clock-history glyphicon-border fs-5')
    elif status in [Constraint.STATUS_NEW]:
        css_class = mark_safe('text-warning bi bi-question-diamond-fill fs-5')
    elif status in [Constraint.STATUS_NON_COMPLIANT, Constraint.STATUS_FAILED]:
        css_class = mark_safe('text-danger bi bi-exclamation-octagon-fill fs-5')
    else:
        raise ValueError(f"Invalid constraint status: {status}")

    return css_class

@register.filter
def section_status(section, tooltip=""):

    css_class = constraint_status_css_class(section._status)

    return format_html('<i class="{}" data-bs-toggle="tooltip" title="{}"></i>', css_class, tooltip)


@register.filter 
def constraint_status(constraint, tooltip=""):

    status = constraint.status

    css_class = constraint_status_css_class(constraint.status)

    return format_html('<i class="{}" data-bs-toggle="tooltip" title="{}"></i>', css_class, tooltip)


@register.filter 
def requirement_status(requirement, tooltip=""):
    status = requirement.get_status()

    css_class = constraint_status_css_class(status)

    return format_html('<i class="{}" data-bs-toggle="tooltip" title="{}"></i>', css_class, tooltip)


@register.filter 
def status_icon(status, tooltip=""):
    if status == "ok":
        css_class = mark_safe('text-success bi bi-check-circle-fill fs-3')
    elif status == "unknown":
        css_class = mark_safe('text-warning bi bi-question-diamond-fill fs-3')
    elif status == "ongoing":
        css_class = mark_safe('text-primary bi bi-clock-history glyphicon-border')
    elif status == "on-hold":
        css_class = mark_safe('text-warning bi bi-pause-circle-fill fs-3')
    elif status == "not-ok":
        css_class = mark_safe('text-danger bi bi-exclamation-octagon-fill fs-3')
    else:
        return ''
    return format_html('<i class="{}" data-bs-toggle="tooltip" title="{}"></i>', css_class, tooltip)

