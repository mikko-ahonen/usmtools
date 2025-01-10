from django import template
from django.utils.html import mark_safe
from django.utils.html import format_html

register = template.Library()

from projects.models import Story
from ..models import TargetSection


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


@register.filter
def section_status(section, tooltip=""):
    # TODO: really calculate
    status = Story.STATUS_NEW

    if status == Story.STATUS_CLOSED:
        css_class = mark_safe('text-success bi bi-check-circle-fill fs-5')
    elif status == Story.STATUS_NEW:
        css_class = mark_safe('text-danger bi bi-exclamation-octagon-fill fs-5')
    elif status in [Story.STATUS_READY]:
        css_class = mark_safe('text-warning bi bi-question-diamond-fill fs-5')
    elif status in [Story.STATUS_ONGOING]:
        css_class = mark_safe('text-primary bi bi-clock-history glyphicon-border fs-5')
    else:
        return status
    return format_html('<i class="{}" data-bs-toggle="tooltip" title="{}"></i>', css_class, tooltip)


@register.filter 
def constraint_status(constraint, tooltip=""):
    status = Story.STATUS_CLOSED
    for story in constraint.stories.all():
        if status == Story.STATUS_CLOSED and story.status != Story.STATUS_CLOSED:
            status = story.status

    if status == Story.STATUS_CLOSED:
        css_class = mark_safe('text-success bi bi-check-circle-fill fs-5')
    elif status == Story.STATUS_NEW:
        css_class = mark_safe('text-danger bi bi-exclamation-octagon-fill fs-5')
    elif status in [Story.STATUS_READY]:
        css_class = mark_safe('text-warning bi bi-question-diamond-fill fs-5')
    elif status in [Story.STATUS_ONGOING]:
        css_class = mark_safe('text-primary bi bi-clock-history glyphicon-border fs-5')
    else:
        return status
    return format_html('<i class="{}" data-bs-toggle="tooltip" title="{}"></i>', css_class, tooltip)


@register.filter 
def requirement_status(requirement, tooltip=""):
    status = Story.STATUS_CLOSED
    for constraint in requirement.statement.constraints:
        for story in constraint.stories.all():
            if status == Story.STATUS_CLOSED and story.status != Story.STATUS_CLOSED:
                status = story.status

    if status == Story.STATUS_CLOSED:
        css_class = mark_safe('text-success bi bi-check-circle-fill fs-3')
    elif status == Story.STATUS_NEW:
        css_class = mark_safe('text-danger bi bi-exclamation-octagon-fill fs-3')
    elif status in [Story.STATUS_READY]:
        css_class = mark_safe('text-warning bi bi-question-diamond-fill fs-3')
    elif status in [Story.STATUS_ONGOING]:
        css_class = mark_safe('text-primary bi bi-clock-history glyphicon-border')
    else:
        return status
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

