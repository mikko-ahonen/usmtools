import re
from django import template
from django.utils.html import mark_safe, format_html, format_html_join, escape
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

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


def constraint_status_css_class(status, use_circle=False, font_size="fs-5"):

    if not status:
        return ""

    symbol = "bi-circle-fill"

    if status == Constraint.STATUS_AUDITED:
        if not use_circle:
            symbol = "bi-check-circle-fill"
        css_class = mark_safe(f'text-success bi {symbol}{font_size}')
    elif status in [Constraint.STATUS_ONGOING, Constraint.STATUS_COMPLIANT, Constraint.STATUS_IMPLEMENTED]:
        if not use_circle:
            symbol = "bi-clock-history glyphicon-border"
        css_class = mark_safe(f'text-primary bi {symbol} {font_size}')
    elif status in [Constraint.STATUS_NEW]:
        if not use_circle:
            symbol = "bi-question-diamond-fill"
        css_class = mark_safe(f'text-warning bi {symbol} {font_size}')
    elif status in [Constraint.STATUS_NON_COMPLIANT, Constraint.STATUS_FAILED]:
        if not use_circle:
            symbol = "bi-exclamation-octagon-fill"
        css_class = mark_safe(f'text-danger bi {symbol} {font_size}')
    else:
        raise ValueError(f"Invalid constraint status: {status}")

    return css_class

@register.filter
def section_status(section, tooltip=""):

    css_class = constraint_status_css_class(section._status, font_size="", use_circle=True)

    return format_html('<i class="{}" data-bs-toggle="tooltip" title="{}"></i>', css_class, tooltip)


@register.filter 
def constraint_status_small(constraint):

    if not constraint:
        status = Constraint.STATUS_NEW
        tooltip = _("Status") + ": " + "New"
    else:
        status = constraint.status
        tooltip = _("Status") + ": " + constraint.get_status_display()

    css_class = constraint_status_css_class(status, font_size="", use_circle=True)

    return format_html('<i class="align-middle {}" data-bs-toggle="tooltip" title="{}"></i>', css_class, tooltip)

@register.filter 
def constraint_status(constraint, tooltip=""):

    status = constraint.status

    css_class = constraint_status_css_class(constraint.status)

    return format_html('<i class="{}" data-bs-toggle="tooltip" title="{}"></i>', css_class, tooltip)


@register.filter 
def requirement_status(requirement, tooltip=""):
    status = requirement.get_status()

    css_class = constraint_status_css_class(status, font_size="", use_circle=True)

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


links = {
    "$document$": "https://usmwiki.com/index.php/Document",
    "$document$": "https://usmwiki.com/index.php/Document",
    "$party$": "https://usmwiki.com/index.php/Party",
    "$Party$": "https://usmwiki.com/index.php/Party",
    "$profile$": "https://usmwiki.com/index.php/Profile",
    "$Profile$": "https://usmwiki.com/index.php/Profile",
    "$risk$": "https://usmwiki.com/index.php/Risk",
    "$Risk$": "https://usmwiki.com/index.php/Risk",
    "$task$": "https://usmwiki.com/index.php/Task",
    "$Task$": "https://usmwiki.com/index.php/Task",
    "$employee$": "https://usmwiki.com/index.php/Employee",
    "$Employee$": "https://usmwiki.com/index.php/Employee",
    "$profile$": "https://usmwiki.com/index.php/Profile",
    "$Profile$": "https://usmwiki.com/index.php/Profile",
    "$responsibility$": "https://usmwiki.com/index.php/Responsibility",
    "$Responsibility$": "https://usmwiki.com/index.php/Responsibility",
}

def strong_repl(m):
    return format_html('<strong>{}</strong>', m.group(0))

@register.filter
def compliances_format_text(text):
    retval = []

    for m in re.finditer(r'(?:([^$@]*)(?:\$([^$]*)\$)?([^$@]*)|([^@]*)(?:@([^$@]*)@)?([^$@]*))', text):
        if m.group(1):
            retval.append(escape(m.group(1)))
        if m.group(2):
            retval.append(format_html("<strong>{}</strong>", m.group(2)))
        if m.group(3):
            retval.append(escape(m.group(3)))
        if m.group(4):
            retval.append(escape(m.group(4)))
        if m.group(5):
            retval.append(format_html("<strong>{}</strong>", m.group(5)))
        if m.group(6):
            retval.append(escape(m.group(6)))

    return mark_safe("".join(retval))


@register.filter
def constraint_status_text(status):
    return Constraint.status_text(status)

constraint_status_text
@register.filter
def compliances_format_links(text):
    for link, url in links.items():
        display_text = link.replace('$', '')
        text = text.replace(link, format_html('<a href="{}">{}</a>', url, display_text))
    return mark_safe(text)

@register.filter
def compliances_story_category(story):
    return format_html(
        '<span class="badge align-midde" style="background-color: {}">{}</span>',
        (story.constraint.category.color if story.constraint else '#ffffffff') or '#ffffffff',
        story.constraint.category.name if story.constraint else _('No name'))


def story_status(story):
    status_css_class = constraint_status_css_class(story.constraint.status if story.constraint else Constraint.STATUS_NEW, use_circle=True, font_size="")
    tooltip = ""
    return format_html(
        '<i class="align-middle {}" data-bs-toggle="tooltip" title="{}"></i>',
        status_css_class,
        tooltip)

@register.simple_tag()
def compliances_story(domain, story):

    sprint_id = story.get_sprint_id()
    if sprint_id:
        project = story.get_project()
        url = reverse("projects:project-sprint-story", kwargs={"tenant_id": domain.tenant_id, "pk": project.id, "sprint_id": sprint_id, "story_id": story.id})
    else:
        url = "#"

    task_id = story.get_task_id()

    story_status_light = story_status(story)
    cat_badge = compliances_story_category(story)

    return format_html(
        '<a class="btn btn-sm btn-outline-primary" href="{}">{} <span class="align-middle">{}</span> {}</a>',
        url,
        story_status_light,
        task_id,
        cat_badge)
