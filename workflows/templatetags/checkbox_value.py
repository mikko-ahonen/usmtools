from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.filter()
def checkbox_value(b):
    if b:
        return 'checked'
    else:
        return '' 
