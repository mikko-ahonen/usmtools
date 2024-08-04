from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.filter()
def indent(count, increment_px=20):
    return mark_safe(str(count * increment_px) + "px")
