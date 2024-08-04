from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.filter()
def verbose_name(obj):
    return obj._meta.verbose_name

@register.filter()
def verbose_name_plural(obj):
    return obj._meta.verbose_name_plural

