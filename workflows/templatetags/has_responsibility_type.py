from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.filter()
def has_responsibility_type(responsible, rtype):
    return rtype in responsible.types
