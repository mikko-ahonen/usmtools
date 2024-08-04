from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.filter()
def as_params(selections):
    return mark_safe('&'.join([ k + '=' + v for k, v in selections.items() ]))
