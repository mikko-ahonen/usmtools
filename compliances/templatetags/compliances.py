from django import template

register = template.Library()

from ..models import TargetSection

@register.filter
def target_section_checked(target, section):
    qs = TargetSection.objects.filter(target_id=target.id, section_id=section.id)
    if qs.exists():
        return 'checked'
    return ''
